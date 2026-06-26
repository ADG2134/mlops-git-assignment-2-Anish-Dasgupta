"""
Part 4: pytest unit tests for load_csv, clean_phone, and validate_email.
"""
import pandas as pd
import pytest

from data_utils import load_csv, clean_phone, validate_email


# ----------------------------------------------------------------------
# load_csv
# ----------------------------------------------------------------------
class TestLoadCsv:
    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            load_csv("does_not_exist_anywhere.csv")

    def test_empty_file_raises_empty_data_error(self, tmp_path):
        empty_file = tmp_path / "empty.csv"
        empty_file.write_text("")  # truly empty, no header
        with pytest.raises(pd.errors.EmptyDataError):
            load_csv(str(empty_file))

    def test_successful_load_returns_dataframe_with_expected_shape(self, tmp_path):
        csv_file = tmp_path / "sample.csv"
        csv_file.write_text("a,b,c\n1,2,3\n4,5,6\n")
        df = load_csv(str(csv_file))
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["a", "b", "c"]
        assert len(df) == 2
        assert df.iloc[0]["a"] == 1

    def test_header_only_file_loads_as_empty_dataframe(self, tmp_path):
        csv_file = tmp_path / "header_only.csv"
        csv_file.write_text("a,b,c\n")
        df = load_csv(str(csv_file))
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["a", "b", "c"]


# ----------------------------------------------------------------------
# clean_phone
# ----------------------------------------------------------------------
class TestCleanPhone:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            ("(123) 456-7890", "123-456-7890"),
            ("123-456-7890", "123-456-7890"),
            ("123.456.7890", "123-456-7890"),
            ("123 456 7890", "123-456-7890"),
            ("1234567890", "123-456-7890"),
            ("+1-123-456-7890", "123-456-7890"),
            ("1 123 456 7890", "123-456-7890"),
            ("11234567890", "123-456-7890"),  # 11 digits, leading country code 1
        ],
    )
    def test_various_valid_formats_normalize_consistently(self, raw, expected):
        assert clean_phone(raw) == expected

    @pytest.mark.parametrize(
        "raw",
        [
            "",
            None,
            "abc-def-ghij",
            "12345",          # too short
            "123456789012",   # too long, no valid country code interpretation
            float("nan"),
        ],
    )
    def test_invalid_inputs_return_empty_string(self, raw):
        assert clean_phone(raw) == ""

    def test_output_is_always_a_string(self):
        assert isinstance(clean_phone("123-456-7890"), str)
        assert isinstance(clean_phone(None), str)


# ----------------------------------------------------------------------
# validate_email
# ----------------------------------------------------------------------
class TestValidateEmail:
    @pytest.mark.parametrize(
        "email",
        [
            "user@example.com",
            "first.last@example.co.uk",
            "user+tag@example.org",
            "user_name123@sub.example.com",
        ],
    )
    def test_valid_emails_return_true(self, email):
        assert validate_email(email) is True

    @pytest.mark.parametrize(
        "email",
        [
            "userexample.com",       # missing @
            "user@@example.com",     # double @
            "user@example",          # missing TLD
            "user @example.com",     # contains space
            "@example.com",          # missing local part
            "user@.com",             # missing domain label
            "",
        ],
    )
    def test_invalid_emails_return_false(self, email):
        assert validate_email(email) is False

    @pytest.mark.parametrize(
        "email",
        [None, float("nan")],
    )
    def test_edge_case_inputs_return_false(self, email):
        assert validate_email(email) is False

    def test_return_type_is_bool(self):
        assert isinstance(validate_email("user@example.com"), bool)
        assert isinstance(validate_email("not-an-email"), bool)
