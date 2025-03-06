import datetime
import decimal
import functools
import pathlib

import pytest
import pytz

from beanhub_extract.data_types import Fingerprint
from beanhub_extract.data_types import Transaction
from beanhub_extract.extractors.wealthsimple import WealthsimpleExtractor
from beanhub_extract.extractors.wealthsimple import parse_date
from beanhub_extract.utils import strip_txn_base_path


@pytest.mark.parametrize(
    "date_str, expected",
    [
        ("2024-04-01", datetime.date(2024, 4, 1)),
    ],
)
def test_parse_date(date_str: str, expected: datetime.date):
    """
    Given a date string in the format YYYY-MM-DD
    When parse_date is called
    Should return the correct datetime.date object
    """
    assert parse_date(date_str) == expected


@pytest.mark.parametrize(
    "input_file, expected",
    [
        (
            "wealthsimple.csv",
            [
                Transaction(
                    extractor="wealthsimple",
                    file="wealthsimple.csv",
                    lineno=1,
                    reversed_lineno=-5,
                    date=datetime.date(2024, 4, 1),
                    desc="Interest earned",
                    amount=decimal.Decimal("12.34"),
                    type="INT",
                    extra={"balance": decimal.Decimal("5123.45")},
                ),
                Transaction(
                    extractor="wealthsimple",
                    file="wealthsimple.csv",
                    lineno=2,
                    reversed_lineno=-4,
                    date=datetime.date(2024, 4, 2),
                    desc="Coffee Shop",
                    amount=decimal.Decimal("-4.56"),
                    type="SPEND",
                    extra={"balance": decimal.Decimal("5118.89")},
                ),
                Transaction(
                    extractor="wealthsimple",
                    file="wealthsimple.csv",
                    lineno=3,
                    reversed_lineno=-3,
                    date=datetime.date(2024, 4, 3),
                    desc="Cash back reward",
                    amount=decimal.Decimal("1.23"),
                    type="CASHBACK",
                    extra={"balance": decimal.Decimal("5120.12")},
                ),
                Transaction(
                    extractor="wealthsimple",
                    file="wealthsimple.csv",
                    lineno=4,
                    reversed_lineno=-2,
                    date=datetime.date(2024, 4, 4),
                    desc="Grocery Store",
                    amount=decimal.Decimal("-45.67"),
                    type="SPEND",
                    extra={"balance": decimal.Decimal("5074.45")},
                ),
                Transaction(
                    extractor="wealthsimple",
                    file="wealthsimple.csv",
                    lineno=5,
                    reversed_lineno=-1,
                    date=datetime.date(2024, 4, 15),
                    desc="Direct deposit",
                    amount=decimal.Decimal("1234.56"),
                    type="AFT_IN",
                    extra={"balance": decimal.Decimal("6309.01")},
                ),
            ],
        ),
    ],
)
def test_wealthsimple_extractor(
    fixtures_folder: pathlib.Path, input_file: str, expected: list[Transaction]
):
    """
    Given a Wealthsimple CSV file
    When the extractor is called
    Should extract the correct transactions
    """
    input_path = fixtures_folder / input_file
    with open(input_path, "r", encoding="utf-8") as f:
        extractor = WealthsimpleExtractor(f)
        transactions = list(extractor())

    # Strip the base path from the transactions for easier comparison
    transactions = [
        strip_txn_base_path(fixtures_folder, txn, pure_posix=True) for txn in transactions
    ]

    assert transactions == expected


@pytest.mark.parametrize(
    "input_file, expected",
    [
        ("wealthsimple.csv", True),
        ("mercury.csv", False),
        ("empty.csv", False),
        ("other.csv", False),
        (pytest.lazy_fixture("zip_file"), False),
    ],
)
def test_wealthsimple_detect(
    fixtures_folder: pathlib.Path, input_file: str, expected: bool
):
    """
    Given a file
    When the detect method is called
    Should correctly identify if it's a Wealthsimple CSV file
    """
    input_path = fixtures_folder / input_file
    with open(input_path, "r", encoding="utf-8") as f:
        extractor = WealthsimpleExtractor(f)
        assert extractor.detect() == expected


def test_wealthsimple_fingerprint(fixtures_folder: pathlib.Path):
    """
    Given a Wealthsimple CSV file
    When the fingerprint method is called
    Should generate the correct fingerprint
    """
    input_path = fixtures_folder / "wealthsimple.csv"
    with open(input_path, "r", encoding="utf-8") as f:
        extractor = WealthsimpleExtractor(f)
        fingerprint = extractor.fingerprint()

    assert fingerprint is not None
    assert fingerprint.starting_date == datetime.date(2024, 4, 1)
    assert isinstance(fingerprint.first_row_hash, str)
    assert len(fingerprint.first_row_hash) > 0 