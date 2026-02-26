from lakehouse.ref_parser import parse_ecb_fx_xml, parse_fred_observations


def test_parse_ecb_fx_xml_handles_single_quotes():
    raw = (
        "<Cube time='2026-02-25'>"
        "<Cube currency='USD' rate='1.05'/>"
        "<Cube currency='GBP' rate='0.85'/>"
        "</Cube>"
    )
    out = parse_ecb_fx_xml(raw, base_ccy="EUR")
    assert len(out) == 2
    assert out[0]["rate_date"] == "2026-02-25"
    assert out[0]["base_ccy"] == "EUR"
    assert {r["quote_ccy"] for r in out} == {"USD", "GBP"}



def test_parse_fred_observations_filters_missing_values():
    raw = (
        '{"observations":['
        '{"date":"2026-02-24","value":"4.33"},'
        '{"date":"2026-02-25","value":"."},'
        '{"date":"2026-02-26","value":"NaN"}'
        "]} "
    )
    out = parse_fred_observations(raw)
    assert len(out) == 1
    assert out[0]["obs_date"] == "2026-02-24"
    assert out[0]["value"] == 4.33
