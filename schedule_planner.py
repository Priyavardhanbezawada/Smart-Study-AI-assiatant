# schedule_planner.py
from datetime import date, timedelta
from ics import Calendar, Event

def create_schedule(topics: list, end_date: date):
    today = date.today()
    study_days = (end_date - today).days

    if study_days < 1 or not topics:
        return None, None

    # Distribute topics among days
    topics_per_day = len(topics) // study_days if study_days > 0 else len(topics)
    if topics_per_day == 0:
        topics_per_day = 1

    schedule = {}
    topic_index = 0
    for i in range(study_days + 1):
        current_date = today + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")
        
        # Assign topics for the day
        end_index = topic_index + topics_per_day
        daily_topics = topics[topic_index:end_index]
        if daily_topics:
            schedule[date_str] = daily_topics
        topic_index = end_index

        if topic_index >= len(topics):
            break
            
    return schedule

def generate_calendar_file(schedule: dict):
    cal = Calendar()
    for day, topics in schedule.items():
        event_date = date.fromisoformat(day)
        event = Event()
        event.name = f"Study: {topics[0]}"
        event.description = "Topics to study today:\n- " + "\n- ".join(topics)
        event.begin = event_date
        event.make_all_day()
        cal.events.add(event)
    return str(cal)
