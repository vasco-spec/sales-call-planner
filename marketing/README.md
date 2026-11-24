# Marketing assets (moved from the previous chat, 24 Nov 2026)

- `videos/`: Seedance drafts (10h limit clip, 25% commission B-roll) and `abertura-de-atividade-v1.mp4` (v1, robot voice rejected). `seedance_prompts.json` = prompts for the top-10 clips.
- `video-abertura/`: how v1 was built. `build.py` writes the mock Finanças screens (HTML), render them to PNG with Playwright at 1920x1080, `make.py` adds voice per line of `lines.txt` and joins with ffmpeg. Next version: Vasco's own voice + his face in a circle bottom-right.
- `charts/`: last 10 Brevo emails, open and click rates (`plot.py` + `last10.json`).
- `emails.html`: the 5 new email drafts (also in Google Doc 1OJUrJflcPkJyUvR-KP21wzW3ThEsEx7w70tHbjfgPIE).
- `sources/`: TVDE law, parliament committee final text (Lei 59/2026), used for the 10h and 25% claims.
