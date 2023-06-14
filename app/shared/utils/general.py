# from urllib.parse import urlparse
from typing import Optional
from enum import Enum
# from app.main import SessionLocal
# from sqlalchemy.orm import Session
import random

def get_prefix_email_subject(subject: str, domain: Optional[str] = None) -> Optional[str]:
    if domain is None:
        return f'Localhost: {subject}'
    if 'localhost' in domain:
        return f'Localhost: {subject}'
    if 'staging' in domain:
        return f'Staging: {subject}'
    return None


def random_code_5():
    return random.randint(10000, 99999)

# disable

class ExtendedEnum(Enum):
    """
    Extended python enum
    """

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))