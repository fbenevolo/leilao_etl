from datetime import datetime

def format_money(value: str) -> float:
    return float(value.replace("R$", "")
                .replace(".", "")
                .replace(",", ".")
                .strip())

def format_datetime(value: str, format: str):
    if not value:
            return None
    
    return datetime.strptime(
        value.strip(),
        format
    )