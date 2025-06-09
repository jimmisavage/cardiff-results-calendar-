import requests
from ics import Calendar, Event
from datetime import datetime
import pytz

# --- CONFIG ---
TEAM_NAME = "Cardiff City"  # <- configurable team name
ICAL_URL = "https://calendar.google.com/calendar/ical/rko4lf06cub3obcun2umnblulg%40group.calendar.google.com/public/basic.ics"
OUTPUT_FILE = "index.ics"

# Download original calendar
response = requests.get(ICAL_URL)
calendar = Calendar(response.text)

# Timezone setup
london_tz = pytz.timezone("Europe/London")

# Create a new calendar
output_calendar = Calendar()

for event in calendar.events:
    summary = event.name or ""
    if TEAM_NAME not in summary:
        continue  # skip unrelated events

    # Extract teams
    try:
        team1, team2_raw = summary.split(" - ", 1)
    except ValueError:
        continue  # skip if format is unexpected

    # Check for score
    if "(" in team2_raw and ")" in team2_raw:
        try:
            team2_part, score_part = team2_raw.split("(", 1)
            team2 = team2_part.strip()
            score1, score2 = score_part.strip(")").split("-")
            cleaned_summary = f"{team1.strip()} {score1.strip()} v {score2.strip()} {team2.strip()}"
        except Exception:
            cleaned_summary = f"{team1.strip()} v {team2_raw.strip()}"
    else:
        cleaned_summary = f"{team1.strip()} v {team2_raw.strip()}"

    # Copy over the original start time
    start = event.begin.astimezone(london_tz)

    new_event = Event()
    new_event.name = cleaned_summary
    new_event.begin = start
    new_event.end = start + (event.end - event.begin) if event.end else start
    new_event.uid = event.uid
    output_calendar.events.add(new_event)

# Save to file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.writelines(output_calendar.serialize_iter())
