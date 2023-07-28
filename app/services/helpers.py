from datetime import datetime

def dt2str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")