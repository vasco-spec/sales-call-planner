#!/usr/bin/env python3
"""List people who clicked a Brevo email campaign within a time window.

Brevo is reached through the session's network proxy, which adds the API key,
so no key is read here. Brevo sometimes refuses a request from one of the
proxy's outgoing IPs or with a spurious permission error; every call is retried.

Usage:
  python3 scripts/brevo_clickers.py --since 2026-11-17T08:40:00Z [--until ...] [--out clicks.json]

Output (JSON list), one entry per person, earliest real click in the window first:
  {"email", "first_click", "campaigns": [{"id", "subject", "click"}], "links_clicked"}
"""
import argparse
import csv
import io
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

API = "https://api.brevo.com/v3"
# Email security scanners open every link automatically; their clicks are not people.
SCANNER_PREFIXES = ("66.249.", "72.14.", "74.125.", "172.253.", "209.85.", "64.233.", "108.177.",
                    "173.194.", "35.", "34.", "40.", "52.", "13.", "20.", "104.47.", "3.", "18.", "54.")
SCANNER_MIN_LINKS = 4
CAMPAIGN_LOOKBACK_DAYS = 10  # campaigns sent this recently can still be collecting clicks


def curl(args, retries=20):
    out, wait = "", 5
    for _ in range(retries):
        res = subprocess.run(["curl", "-sS", "-w", "\n%{http_code}"] + args, capture_output=True, text=True).stdout
        out, _, code = res.rpartition("\n")
        if code == "429":  # rate limited: back off, up to 2 minutes between tries
            time.sleep(wait)
            wait = min(wait * 2, 120)
            continue
        if "unrecognised IP" not in out and "not authorized for resource" not in out:
            return out
        time.sleep(1)
    raise RuntimeError(f"Brevo kept refusing: {out[:200]}")


def get(path):
    return json.loads(curl([f"{API}{path}"]))


def parse_ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def recent_campaigns(now):
    data = get("/emailCampaigns?status=sent&limit=30&sort=desc&excludeHtmlContent=true")
    cutoff = now - timedelta(days=CAMPAIGN_LOOKBACK_DAYS)
    out = []
    for c in data.get("campaigns", []):
        sent = c.get("sentDate") or c.get("scheduledAt")
        if sent and parse_ts(sent) >= cutoff:
            out.append({"id": c["id"], "subject": (c.get("subject") or "").strip(), "sent": sent})
    return out


def clickers_csv(campaign_id):
    r = json.loads(curl(["-X", "POST", "-H", "content-type: application/json",
                         "-d", '{"recipientsType":"clickers"}',
                         f"{API}/emailCampaigns/{campaign_id}/exportRecipients"]))
    pid = r["processId"]
    for _ in range(60):
        p = get(f"/processes/{pid}")
        if p.get("status") == "completed":
            return subprocess.run(["curl", "-sS", p["export_url"]], capture_output=True, text=True).stdout
        time.sleep(3)
    raise RuntimeError(f"export for campaign {campaign_id} did not finish")


def real_clicks(csv_text):
    """Yield (email, click_time_utc, links_clicked) for human clicks."""
    reader = csv.reader(io.StringIO(csv_text.lstrip("﻿")), delimiter=";")
    header = next(reader, None)
    if not header:
        return
    for row in reader:
        if len(row) < 19:
            continue
        ip, nlinks = row[14], int(row[16] or 0)
        if ip.startswith(SCANNER_PREFIXES) or nlinks >= SCANNER_MIN_LINKS:
            continue
        times = [datetime.strptime(v.strip(), "%d-%m-%Y %H:%M:%S") for v in row[18:] if v.strip()]
        if not times:
            continue
        # Brevo export times are Europe/Lisbon local time; treat them as UTC+0 in winter, UTC+1 in summer.
        t = min(times)
        offset = 1 if 4 <= t.month <= 10 else 0
        yield row[2].strip().lower(), (t - timedelta(hours=offset)).replace(tzinfo=timezone.utc), nlinks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", required=True, help="UTC ISO time; only clicks at or after this count")
    ap.add_argument("--until", help="UTC ISO time; default now")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    a = ap.parse_args()
    now = datetime.now(timezone.utc)
    since = parse_ts(a.since)
    until = parse_ts(a.until) if a.until else now

    people = {}
    camps = recent_campaigns(now)
    for c in camps:
        for email, t, nlinks in real_clicks(clickers_csv(c["id"])):
            if not (since <= t < until):
                continue
            p = people.setdefault(email, {"email": email, "first_click": t, "campaigns": [], "links_clicked": 0})
            p["first_click"] = min(p["first_click"], t)
            p["links_clicked"] += nlinks
            p["campaigns"].append({"id": c["id"], "subject": c["subject"], "click": t.isoformat()})
    result = sorted(people.values(), key=lambda p: p["first_click"])
    for p in result:
        p["first_click"] = p["first_click"].isoformat()
    text = json.dumps({"window": [since.isoformat(), until.isoformat()],
                       "campaigns_checked": camps, "clickers": result}, ensure_ascii=False, indent=1)
    if a.out:
        open(a.out, "w").write(text)
    else:
        print(text)
    print(f"{len(result)} clickers from {len(camps)} recent campaigns", file=sys.stderr)


if __name__ == "__main__":
    main()
