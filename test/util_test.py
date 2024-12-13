from scapi.util import dissoc, guess_mime_type


def test_dissoc():
    d = {"a": "alpha", "b": "beta", "c": "gamma"}
    assert {"a": "alpha", "b": "beta"} == dissoc(d, "c")
    assert d == dissoc(d, "")
    assert {} == dissoc({}, "a")


def test_guess_mime_type():
    assert "application/json" == guess_mime_type("example.json")
    assert "image/png" == guess_mime_type("example.png")
    assert "text/plain" == guess_mime_type("example.txt")
    assert "text/csv" == guess_mime_type("example.csv")
    assert "text/tab-separated-values" == guess_mime_type("example.tsv")
    assert "application/vnd.apache.parquet" == guess_mime_type("example.parquet")
    assert "application/octet-stream" == guess_mime_type("example.unknown_extension")
