from lakehouse.macro_rules import is_valid_ecb_fx_record, is_valid_fred_record


def test_is_valid_ecb_fx_record_true():
    row = {
        "rate_date": "2026-02-25",
        "base_ccy": "EUR",
        "quote_ccy": "USD",
        "fx_rate": 1.05,
    }
    assert is_valid_ecb_fx_record(row) is True


def test_is_valid_ecb_fx_record_false_rate():
    row = {
        "rate_date": "2026-02-25",
        "base_ccy": "EUR",
        "quote_ccy": "USD",
        "fx_rate": 0,
    }
    assert is_valid_ecb_fx_record(row) is False


def test_is_valid_fred_record_true():
    assert is_valid_fred_record({"obs_date": "2026-02-25", "value": 4.33}) is True


def test_is_valid_fred_record_false():
    assert is_valid_fred_record({"obs_date": "2026-02-25", "value": None}) is False
