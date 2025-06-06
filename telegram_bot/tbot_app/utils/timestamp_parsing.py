from datetime import datetime


def timestamp_parse(time_string: str) -> datetime.date:
    # time_ = datetime.strptime(message_.text, '%H:%M').time()
    hours, minutes = time_string.split(":")
    return datetime.today().replace(hour=int(hours), minute=int(minutes), second=0)