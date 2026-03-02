from pyspark.sql import DataFrame
from pyspark.sql import functions as F

def check_invalid_ohlc(df: DataFrame) -> int:
    """
    Check for invalid OHLC rules.
    Returns the count of invalid records. 
    Rule:
    - price items > 0
    - high >= max(open, close)
    - low <= min(open, close)
    """
    invalid_df = df.filter(
        (F.col("open") <= 0) |
        (F.col("high") <= 0) |
        (F.col("low") <= 0) |
        (F.col("close") <= 0) |
        (F.col("high") < F.greatest(F.col("open"), F.col("close"))) |
        (F.col("low") > F.least(F.col("open"), F.col("close")))
    )
    return invalid_df.count()

def check_duplicate_bars(df: DataFrame) -> int:
    """
    Check for duplicate bar_start_ts records for a symbol in a source.
    Returns the number of duplicated key groups.
    """
    dupes = df.groupBy("source", "symbol", "bar_start_ts") \
              .count() \
              .filter(F.col("count") > 1)
    return dupes.count()

def check_macro_null_rates(df: DataFrame) -> dict:
    """
    Check null rates of the joined market_macro_daily table.
    """
    total = df.count()
    if total == 0:
        return {"total": 0, "eurusd_null_rate": 0.0, "fedfunds_null_rate": 0.0}
        
    res = df.select(
        (F.sum(F.when(F.col("eurusd_rate").isNull(), 1).otherwise(0)) / total).alias("fx_null_rate"),
        (F.sum(F.when(F.col("fedfunds").isNull(), 1).otherwise(0)) / total).alias("fed_null_rate")
    ).first()
    
    return {
        "total": total,
        "eurusd_null_rate": res["fx_null_rate"],
        "fedfunds_null_rate": res["fed_null_rate"]
    }
