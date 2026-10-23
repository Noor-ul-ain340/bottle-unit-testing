"""
Laiba Tabassum - Unit tests for bottle.BaseResponse
Techniques: ECP (Equivalence Class Partitioning) + BVA (Boundary Value Analysis)
See ECP_BVA_Notes.md for the design notes behind these tests.
"""
import pytest

from bottle import BaseResponse
from tests.conftest import read_csv

pytestmark = [pytest.mark.laiba_tests, pytest.mark.response]


# ---------------------------------------------------------------- smoke
@pytest.mark.smoke
@pytest.mark.order(1)
def test_default_response_is_200_ok():
    """TC-L01: A fresh response must default to 200 OK with an empty body."""
    r = BaseResponse()
    assert r.status_code == 200
    assert r.status_line == "200 OK"
    assert r.body == ""


# ---------------------------------------------------------------- ECP: status (int)
@pytest.mark.ecp
@pytest.mark.order(2)
@pytest.mark.parametrize(
    "code, reason",
    [
        (100, "Continue"),                 # 1xx informational
        (200, "OK"),                       # 2xx success
        (301, "Moved Permanently"),        # 3xx redirect
        (404, "Not Found"),                # 4xx client error
        (500, "Internal Server Error"),    # 5xx server error
    ],
    ids=["1xx", "2xx", "3xx", "4xx", "5xx"],
)
def test_status_valid_integer_classes(code, reason):
    """TC-L02: One representative from each valid HTTP status class."""
    r = BaseResponse(status=code)
    assert r.status_code == code
    assert r.status_line == f"{code} {reason}"


# ---------------------------------------------------------------- BVA: status (int)
@pytest.mark.bva
@pytest.mark.order(3)
@pytest.mark.parametrize("code", [100, 101, 998, 999], ids=["min", "min+1", "max-1", "max"])
def test_status_boundaries_inside_range_are_accepted(code):
    """TC-L03: Lower (100) and upper (999) boundaries and their inner neighbours."""
    assert BaseResponse(status=code).status_code == code


@pytest.mark.bva
@pytest.mark.order(4)
@pytest.mark.parametrize("code", [99, 1000, -1, 10000], ids=["min-1", "max+1", "negative", "far-above"])
def test_status_boundaries_outside_range_raise_value_error(code):
    """TC-L04: Values just outside 100-999 must be rejected."""
    with pytest.raises(ValueError, match="out of range"):
        BaseResponse(status=code)


@pytest.mark.bva
@pytest.mark.order(5)
def test_status_zero_is_falsy_and_falls_back_to_default():
    """TC-L05: status=0 is falsy, so the constructor silently keeps 200 OK."""
    assert BaseResponse(status=0).status_code == 200


@pytest.mark.ecp
@pytest.mark.order(6)
def test_unknown_but_in_range_code_gets_unknown_reason():
    """TC-L06: 599 is in range but has no standard reason -> 'Unknown'."""
    assert BaseResponse(status=599).status_line == "599 Unknown"


# ---------------------------------------------------------------- ECP: status (str)
@pytest.mark.ecp
@pytest.mark.order(7)
@pytest.mark.parametrize(
    "text, code, line",
    [
        ("404 Not Found", 404, "404 Not Found"),
        ("418 Brain not found", 418, "418 Brain not found"),
        ("404 ", 404, "404 Unknown"),
    ],
    ids=["standard", "custom-reason", "empty-reason"],
)
def test_status_valid_string_formats(text, code, line):
    """TC-L07: '<code> <reason>' strings are parsed correctly."""
    r = BaseResponse(status=text)
    assert (r.status_code, r.status_line) == (code, line)


@pytest.mark.ecp
@pytest.mark.order(8)
@pytest.mark.parametrize(
    "text",
    ["404", "abc def", "99 Too Low", "1000 Too High", "404 Café"],
    ids=["no-space", "non-numeric", "below-range", "above-range", "non-ascii"],
)
def test_status_invalid_strings_raise_value_error(text):
    """TC-L08: Malformed status strings must raise ValueError."""
    with pytest.raises(ValueError):
        BaseResponse(status=text)


# ---------------------------------------------------------------- headers
@pytest.mark.ecp
@pytest.mark.order(9)
def test_set_header_replaces_and_add_header_appends():
    """TC-L09: set_header replaces, add_header keeps duplicates, lookup is case-insensitive."""
    r = BaseResponse()
    r.set_header("X-Test", "1")
    r.set_header("x-test", "2")
    assert r["X-TEST"] == "2"
    r.add_header("X-Test", "3")
    values = [v for k, v in r.headerlist if k == "X-Test"]
    assert values == ["2", "3"]


@pytest.mark.ecp
@pytest.mark.order(10)
@pytest.mark.parametrize("bad", ["a\nb", "a\rb", "a\0b"], ids=["LF", "CR", "NUL"])
def test_header_value_with_control_characters_is_rejected(bad):
    """TC-L10: Header injection characters must raise ValueError."""
    with pytest.raises(ValueError):
        BaseResponse().set_header("X-Bad", bad)


@pytest.mark.ecp
@pytest.mark.order(11)
def test_default_content_type_is_added_to_headerlist():
    """TC-L11: Content-Type defaults to text/html; charset=UTF-8 and charset is UTF-8."""
    r = BaseResponse()
    assert ("Content-Type", "text/html; charset=UTF-8") in r.headerlist
    assert r.charset == "UTF-8"


@pytest.mark.ecp
@pytest.mark.order(12)
@pytest.mark.parametrize(
    "status, removed",
    [(204, "Content-Type"), (304, "Last-Modified")],
    ids=["204-no-content-type", "304-no-last-modified"],
)
def test_forbidden_headers_removed_for_204_and_304(status, removed):
    """TC-L12: 204/304 responses must not send certain headers (RFC rules)."""
    r = BaseResponse(status=status)
    r.set_header(removed, "something")
    assert removed not in [k for k, _ in r.headerlist]


@pytest.mark.ecp
@pytest.mark.order(13)
def test_copy_creates_independent_response():
    """TC-L13: A copy keeps the data but later changes do not leak to the original."""
    original = BaseResponse(status=404, headers={"X-A": "1"})
    clone = original.copy()
    clone.set_header("X-A", "changed")
    clone.status = 500
    assert original["X-A"] == "1"
    assert original.status_code == 404
    assert clone.status_code == 500


# ---------------------------------------------------------------- CSV data-driven (Task 3)
CSV_ROWS = read_csv("test_data_laiba.csv")


@pytest.mark.csv_driven
@pytest.mark.order(14)
@pytest.mark.parametrize("row", CSV_ROWS, ids=[r["test_id"] for r in CSV_ROWS])
def test_status_codes_from_csv(row):
    """TC-L14: Status inputs and expected results are read from test_data_laiba.csv."""
    value = int(row["status_input"]) if row["input_type"] == "int" else row["status_input"]
    if row["expected_outcome"] == "error":
        with pytest.raises(ValueError):
            BaseResponse(status=value)
    else:
        r = BaseResponse(status=value)
        assert r.status_code == int(row["expected_code"])
        assert r.status_line == row["expected_status_line"]
