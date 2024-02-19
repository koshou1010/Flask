from uuid import uuid4


def generate_uuid():
    """Generate hex uuid with upper case."""
    return uuid4().hex.upper()
