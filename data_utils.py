"""
data_utils.py

Three small, well-defined data utility functions used by the data validation
pipeline. These are the functions exercised by Part 4's pytest unit tests.
"""
import os
import re
import csv
import pandas as pd


def load_csv(filepath: str) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame.

    Raises:
        FileNotFoundError: if filepath does not exist.
        pd.errors.EmptyDataError: if the file exists but has no columns/data.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No such file: '{filepath}'")

    # Let pandas raise EmptyDataError naturally for a genuinely empty file;
    # this also correctly handles a header-only (0-row) CSV, which loads to
    # an empty-but-valid DataFrame rather than raising.
    df = pd.read_csv(filepath)
    return df


def clean_phone(phone) -> str:
    """Normalize a phone number to the consistent format '###-###-####'.

    Accepts varied raw formats such as '(123) 456-7890', '123.456.7890',
    '+1-123-456-7890', '1234567890', etc.

    Returns an empty string for missing/invalid input (None, NaN, empty
    string, or a value that doesn't contain exactly 10 digits after
    stripping a leading US country code '1').
    """
    if phone is None:
        return ""
    if isinstance(phone, float) and pd.isna(phone):
        return ""

    phone = str(phone).strip()
    if phone == "" or phone.lower() == "nan":
        return ""

    digits = re.sub(r"\D", "", phone)

    # Strip a leading country code "1" if it leaves exactly 10 digits
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]

    if len(digits) != 10:
        return ""  # cannot normalize -> invalid

    return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"


EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_email(email) -> bool:
    """Return True if `email` is a syntactically valid email address."""
    if email is None:
        return False
    if isinstance(email, float) and pd.isna(email):
        return False

    email = str(email).strip()
    if email == "" or " " in email:
        return False

    return bool(EMAIL_REGEX.match(email))
