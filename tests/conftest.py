import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "spark: mark test as requiring a live SparkSession "
        "(skipped in CI, run locally with -m spark)",
    )


@pytest.fixture(scope="session")
def spark():
    """
    Session-scoped SparkSession for PySpark unit tests.
    Only activated when tests are marked with @pytest.mark.spark.

    Usage:
        Install PySpark locally:  pip install -e ".[spark]"
        Run spark tests:          pytest -m spark
        CI skips spark tests:     pytest -m "not spark"
    """
    try:
        from pyspark.sql import SparkSession

        session = (
            SparkSession.builder.master("local[1]")
            .appName("lakehouse-unit-tests")
            .config("spark.sql.shuffle.partitions", "1")
            .config("spark.ui.enabled", "false")
            .getOrCreate()
        )
        session.sparkContext.setLogLevel("ERROR")
        yield session
        session.stop()
    except ImportError:
        pytest.skip("PySpark not installed — run `pip install -e '.[spark]'` to enable spark tests")
