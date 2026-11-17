# Daily routine: email clickers → Milton's call queue

Runs Monday to Friday at 08:40 Europe/Lisbon as a scheduled task. Each run turns the
people who clicked a Brevo email since the previous run into HubSpot call tasks for
Milton Navaia (HubSpot owner ID `35549712`).

**Status: draft.** How the tasks get created (automatically, after approval, or as a
Slack list for Milton instead) is still to be decided by Vasco. Until then, every
HubSpot change in this routine needs a person's approval in the session, as the
HubSpot connector requires. Do nothing else in HubSpot: no deal changes, no
reassignments, no deletions.

## Steps

1. **Window.** `until` = now. `since` = the previous weekday at 08:40 Europe/Lisbon
   (on Monday that is Friday). Convert both to UTC.

2. **Clickers.** From the repository root:

   ```
   python3 scripts/brevo_clickers.py --since <since UTC ISO> --until <until UTC ISO> --out clicks.json
   ```

   Brevo is reached through the environment's network proxy, which adds the API key.
   The script retries Brevo's rate limits and intermittent IP refusals by itself.

3. **Look up each clicker in HubSpot** (`search_crm_objects`, CONTACT, `email` IN up to
   100 emails per call) with properties `email, firstname, lastname, lifecyclestage,
   closedate, notes_next_activity_date, hubspot_owner_id`. Skip a clicker when:
   - they are not in HubSpot (list them in the report),
   - `closedate` is set or `lifecyclestage` is `customer` (already a customer),
   - `notes_next_activity_date` falls within the next 7 days (a follow-up is already booked).

4. **Deal and fleet.** For each remaining contact, find their deals
   (`search_crm_objects`, DEAL, associatedWith the contact) with properties
   `dealname, dealstage, fleet, hubspot_owner_id`. Use the most recently modified deal
   that is not Closed Won. No deal is fine: the task goes on the contact only.

5. **Rank and cap.** Sort by fleet size (largest first, unknown last), then by links
   clicked. Keep the top **15**. List the rest in the report as "not scheduled today".

6. **Create the tasks** (`manage_crm_objects`, at most 10 objects per call):
   - `hs_task_subject`: `Email click follow-up – <deal name, or contact name/email> (fleet N)`
     (leave out "(fleet N)" when unknown)
   - `hs_task_body`: which campaign(s) they clicked and when, in one line each
   - `hs_task_type` CALL, `hs_task_priority` HIGH, `hs_task_status` NOT_STARTED
   - `hubspot_owner_id` 35549712
   - `hs_timestamp`: today 14:00 Europe/Lisbon, in UTC
   - associations: the contact, and the deal when there is one

   If HubSpot disconnects mid-way, reconnect, check which tasks already exist
   (TASK search: owner 35549712, created today, subject contains "Email") and create
   only the missing ones.

7. **Report** at the end of the session: window, campaigns checked, clickers found,
   how many were skipped and why, and the tasks created with their HubSpot links.

## Notes

- Scanner clicks (email security systems that click every link) are removed by the
  script: known Google, Microsoft and AWS IP ranges, or 4+ links clicked at once.
- Campaigns sent in the last 10 days are checked, since clicks keep arriving for days.
