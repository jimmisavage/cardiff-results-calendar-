import requests
from ics import Calendar, Event
from datetime import datetime
import pytz

# Download original calendar
url = "https://calendar.google.com/calendar/ical/rko4lf06cub3obcun2umnblulg%40group.calendar.google.com/public/basic.ics"
response = requests.get(url)
calendar = Calendar(response.text)

# Timezone setup
london_tz = pytz.timezone("Europe/London")

# Create a new calendar
output_calendar = Calendar()

for event in calendar.events:
    summary = event.name or ""
    if "Wales" not in summary:
        continue  # skip non-Wales games

    # Extract teams
    try:
        team1, rest = summary.split(" - ", 1)
        if "[" in rest:
            team2, _ = rest.split(" [", 1)
        else:
            team2 = rest
    except ValueError:
        continue

    # Get score from original summary
    if "(" in summary and ")" in summary:
        try:
            score_part = summary.split("(")[-1].split(")")[0]
            score1, score2 = score_part.strip().split("-")
            score1 = score1.strip()
            score2 = score2.strip()
            cleaned_summary = f"{team1.strip()} {score1} v {score2} {team2.strip()}"
        except Exception:
            cleaned_summary = f"{team1.strip()} v {team2.strip()}"
    else:
        cleaned_summary = f"{team1.strip()} v {team2.strip()}"

    # Copy over the original start time
    start = event.begin.astimezone(london_tz)

    new_event = Event()
    new_event.name = cleaned_summary
    new_event.begin = start
    new_event.end = start + (event.end - event.begin) if event.end else start
    new_event.uid = event.uid
    output_calendar.events.add(new_event)

# Save to file
with open("index.ics", "w", encoding="utf-8") as f:
    f.writelines(output_calendar.serialize_iter())
