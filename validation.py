"""
validation.py - input validation for the booking form.

Every validate_* function takes the raw text typed by the user and returns an
error message. An empty string ("") means the value is valid.
"""
import re

from config import MAX_AGE, MAX_DAYS, MIN_AGE, MIN_DAYS

# Letters (including accented ones) separated by single spaces, hyphens or
# apostrophes - e.g. "Mary-Jane", "O'Brien", "Anne Marie". No digits or symbols.
_NAME_PATTERN = re.compile(r"^[^\W\d_]+(?:[ '\-][^\W\d_]+)*$", re.UNICODE)


def validate_name(value: str, field_name: str) -> str:
    """Validate a first name or surname. field_name is used in the message text."""
    text = value.strip()
    if not text:
        return f"{field_name} is required."
    if len(text) < 2:
        return f"{field_name} must be at least 2 characters."
    if len(text) > 40:
        return f"{field_name} must be 40 characters or fewer."
    if not _NAME_PATTERN.match(text):
        return f"{field_name} can only contain letters, spaces, hyphens and apostrophes."
    return ""


def validate_address(value: str) -> str:
    """Validate the customer address (length and must contain letters)."""
    text = " ".join(value.split())  # collapse repeated whitespace before checking
    if not text:
        return "Address is required."
    if len(text) < 8:
        return "Please enter the full address (street and town/postcode)."
    if len(text) > 120:
        return "Address must be 120 characters or fewer."
    if not re.search(r"[A-Za-z]", text):
        return "Address must contain letters."
    return ""


def validate_age(value: str) -> str:
    """Validate the customer age: a whole number between MIN_AGE and MAX_AGE."""
    text = value.strip()
    if not text:
        return "Age is required."
    if not re.fullmatch(r"\d{1,3}", text):
        return "Age must be a whole number, e.g. 25."
    age = int(text)
    if age < MIN_AGE:
        return f"Customers must be at least {MIN_AGE} years old to rent a car."
    if age > MAX_AGE:
        return f"Please check the age - the maximum accepted is {MAX_AGE}."
    return ""


def validate_days(value: str) -> str:
    """Validate the number of rental days: a whole number from MIN_DAYS to MAX_DAYS."""
    text = value.strip()
    if not text:
        return "Number of days is required."
    if not re.fullmatch(r"-?\d+", text):   # allows a leading minus so we can give a range message
        return "Number of days must be a whole number."
    days = int(text)
    if not MIN_DAYS <= days <= MAX_DAYS:
        return f"Rentals must be between {MIN_DAYS} and {MAX_DAYS} days."
    return ""
