from datetime import timedelta, date

def create_schedule(topics, exam_date):
    """
    Create a daily study schedule splitting topics evenly until exam_date.
    Returns a dictionary with date strings as keys and list of topics as values.
    """
    today = date.today()
    days_left = (exam_date - today).days

    if days_left <= 0:
        return {}

    topics_per_day = max(1, len(topics) // days_left)
    schedule = {}
    day_counter = 0

    for i in range(0, len(topics), topics_per_day):
        day = today + timedelta(days=day_counter)
        schedule[day.strftime("%Y-%m-%d")] = topics[i:i+topics_per_day]
        day_counter += 1

    return schedule


def generate_calendar_file(schedule):
    """
    Generate a downloadable .ics calendar file from the schedule.
    """
    ics_data = "BEGIN:VCALENDAR\nVERSION:2.0\n"
    for day, topics in schedule.items():
        ics_data += (
            "BEGIN:VEVENT\n"
            f"SUMMARY:Study {', '.join(topics)}\n"
            f"DTSTART;VALUE=DATE:{day.replace('-', '')}\n"
            f"DTEND;VALUE=DATE:{day.replace('-', '')}\n"
            "END:VEVENT\n"
        )
    ics_data += "END:VCALENDAR"
    return ics_data
