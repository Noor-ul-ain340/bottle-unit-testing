"""
Noor ul Ain - Unit tests for bottle.HeaderDict (case-insensitive header storage)
Techniques: ECP + BVA on header names/values, empty strings, case sensitivity.
"""
import pytest

from bottle import HeaderDict
from tests.conftest import read_csv

pytestmark = [pytest.mark.noor_tests, pytest.mark.headers]


# ---------------------------------------------------------------- smoke
@pytest.mark.smoke
@pytest.mark.order(1)
def test_new_headerdict_is_empty():
    """TC-N01: A new HeaderDict has no keys and returns defaults for missing headers."""
    h = HeaderDict()
    assert len(h) == 0
    assert h.get("X-Missing") is None
    assert h.get("X-Missing", "fallback") == "fallback"
    assert h.getall("X-Missing") == []


# ---------------------------------------------------------------- ECP: case sensitivity
@pytest.mark.ecp
@pytest.mark.order(2)
@pytest.mark.parametrize(
    "lookup",
    ["content-type", "CONTENT-TYPE", "Content-Type", "cOnTeNt-TyPe"],
    ids=["lower", "upper", "title", "mixed"],
)
def test_lookup_is_case_insensitive(lookup):
    """TC-N02: Any casing of the name finds the same header."""
    h = HeaderDict()
    h["content-type"] = "text/html"
    assert h[lookup] == "text/html"
    assert lookup in h


@pytest.mark.ecp
@pytest.mark.order(3)
@pytest.mark.parametrize(
    "raw, normalised",
    [
        ("x_custom_header", "X-Custom-Header"),    # underscore -> dash
        ("ACCEPT", "Accept"),                      # upper -> title
        ("user-agent", "User-Agent"),              # lower -> title
        ("  spaced  ", "Spaced"),                  # surrounding spaces stripped
    ],
    ids=["underscore", "upper", "lower", "whitespace"],
)
def test_header_names_are_normalised(raw, normalised):
    """TC-N03: Names are title-cased, stripped and '_' becomes '-'."""
    h = HeaderDict()
    h[raw] = "v"
    assert list(h.keys()) == [normalised]


# ---------------------------------------------------------------- BVA: empty strings
@pytest.mark.bva
@pytest.mark.order(4)
def test_empty_string_value_is_stored():
    """TC-N04: An empty value is legal and is returned as '' (not None)."""
    h = HeaderDict()
    h["X-Empty"] = ""
    assert h["x-empty"] == ""
    assert "X-Empty" in h


@pytest.mark.bva
@pytest.mark.order(5)
def test_empty_string_name_is_accepted_as_a_key():
    """TC-N05: Boundary case - the empty header name '' is currently accepted."""
    h = HeaderDict()
    h[""] = "v"
    assert h[""] == "v"
    assert "" in list(h.keys())


@pytest.mark.ecp
@pytest.mark.order(6)
@pytest.mark.parametrize(
    "value, stored",
    [(5, "5"), (0, "0"), (3.5, "3.5"), (b"bytes", "bytes")],
    ids=["int", "zero", "float", "bytes"],
)
def test_non_string_values_are_converted_to_text(value, stored):
    """TC-N06: Values are converted to str (bytes are decoded)."""
    h = HeaderDict()
    h["X-Num"] = value
    assert h["X-Num"] == stored


# ---------------------------------------------------------------- invalid input
@pytest.mark.ecp
@pytest.mark.order(7)
@pytest.mark.parametrize("bad", ["a\nb", "a\rb", "a\0b"], ids=["LF", "CR", "NUL"])
def test_control_characters_in_name_or_value_raise(bad):
    """TC-N07: CR / LF / NUL (header injection) are rejected in names and values."""
    h = HeaderDict()
    with pytest.raises(ValueError):
        h[bad] = "v"
    with pytest.raises(ValueError):
        h["X-Ok"] = bad


@pytest.mark.ecp
@pytest.mark.order(8)
def test_missing_header_raises_key_error_but_get_does_not():
    """TC-N08: h[name] raises KeyError for a missing header; h.get() returns the default."""
    h = HeaderDict()
    with pytest.raises(KeyError):
        h["Missing"]
    assert h.get("Missing") is None


# ---------------------------------------------------------------- multi-value API
@pytest.mark.ecp
@pytest.mark.order(9)
def test_append_keeps_all_values_and_setitem_replaces():
    """TC-N09: append() collects values, [] / replace() overwrite them, get() can pick an index."""
    h = HeaderDict()
    h.append("Set-Cookie", "a=1")
    h.append("set-cookie", "b=2")
    assert h.getall("SET-COOKIE") == ["a=1", "b=2"]
    assert h["set-cookie"] == "b=2"                  # last value by default
    assert h.get("set-cookie", index=0) == "a=1"     # first value on request
    h["Set-Cookie"] = "only"
    assert h.getall("set-cookie") == ["only"]
    h.replace("set-cookie", "z")
    assert h.getall("set-cookie") == ["z"]


@pytest.mark.ecp
@pytest.mark.order(10)
def test_delete_and_filter_remove_headers_case_insensitively():
    """TC-N10: del and filter() ignore case."""
    h = HeaderDict({"A-One": "1", "B-Two": "2", "C-Three": "3"})
    del h["a-one"]
    assert "A-One" not in h
    h.filter(["B-TWO", "does-not-exist"])
    assert list(h.keys()) == ["C-Three"]


@pytest.mark.ecp
@pytest.mark.order(11)
def test_constructor_accepts_dict_and_keywords():
    """TC-N11: HeaderDict(dict, **kw) loads both sources with normalised names."""
    h = HeaderDict({"a-b": "1"}, c="2")
    assert sorted(h.keys()) == ["A-B", "C"]


# ---------------------------------------------------------------- CSV data-driven (Task 3)
CSV_ROWS = read_csv("test_data_noor.csv")


@pytest.mark.csv_driven
@pytest.mark.order(12)
@pytest.mark.parametrize("row", CSV_ROWS, ids=[r["test_id"] for r in CSV_ROWS])
def test_headers_from_csv(row):
    """TC-N12: Header names/values and expected results come from test_data_noor.csv."""
    h = HeaderDict()
    h[row["header_name"]] = row["header_value"]
    assert h[row["lookup_name"]] == row["expected_value"]
    assert row["expected_key_in_dict"] in list(h.keys())
