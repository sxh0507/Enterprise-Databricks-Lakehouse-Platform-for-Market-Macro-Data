from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window


def build_gold_market_macro_daily(
    mkt_df: DataFrame, fx_df: DataFrame, fed_df: DataFrame, max_fill_days: int = 5
) -> DataFrame:
    """
    Build the gold mart table linking daily crypto OHLC with macro indicators (FX and Fed Funds).
    Includes a forward-fill mechanism for weekends/holidays with a maximum TTL (Time-To-Live).

    Args:
        mkt_df: Silver crypto OHLC dataframe (daily)
        fx_df: Silver ECB FX dataframe (daily)
        fed_df: Silver FRED dataframe (daily)
        max_fill_days: Maximum number of days to forward-fill stale macro data.
    """

    # 1. Market Data (7x24)
    mkt = mkt_df.groupBy("source", "symbol", F.to_date("bar_start_ts").alias("trade_date")).agg(
        F.max_by("close", "bar_end_ts").alias("close_px"), F.sum("volume").alias("daily_volume")
    )

    # 2. FX Data
    fx = fx_df.filter((F.col("base_ccy") == "EUR") & (F.col("quote_ccy") == "USD")).select(
        F.col("rate_date"), F.col("fx_rate").alias("raw_fx")
    )

    # 3. FED Data (DFF)
    fed = fed_df.filter(F.col("series_id") == "DFF").select(
        F.col("obs_date"), F.col("value").alias("raw_fed")
    )

    # Join everything together
    joined = mkt.join(fx, mkt.trade_date == fx.rate_date, "left").join(
        fed, mkt.trade_date == fed.obs_date, "left"
    )

    # Window for forward fill
    window_spec = Window.partitionBy("source", "symbol").orderBy("trade_date")

    # Step 4 & 5: Forward fill and apply TTL (Time-To-Live) safety bounds
    # We also keep track of the date the value was last observed to calculate the gap

    filled = (
        joined.withColumn(
            "last_fx_date",
            F.last(F.when(F.col("raw_fx").isNotNull(), F.col("trade_date")), ignorenulls=True).over(
                window_spec
            ),
        )
        .withColumn(
            "last_fed_date",
            F.last(
                F.when(F.col("raw_fed").isNotNull(), F.col("trade_date")), ignorenulls=True
            ).over(window_spec),
        )
        .withColumn("filled_fx", F.last("raw_fx", ignorenulls=True).over(window_spec))
        .withColumn("filled_fed", F.last("raw_fed", ignorenulls=True).over(window_spec))
        .withColumn("fx_gap_days", F.datediff(F.col("trade_date"), F.col("last_fx_date")))
        .withColumn("fed_gap_days", F.datediff(F.col("trade_date"), F.col("last_fed_date")))
    )

    # Apply TTL logic: If the gap is > max_fill_days, revert to NULL
    final_df = filled.select(
        "source",
        "symbol",
        "trade_date",
        "close_px",
        "daily_volume",
        F.when(F.col("fx_gap_days") <= max_fill_days, F.col("filled_fx"))
        .otherwise(F.lit(None))
        .alias("eurusd_rate"),
        F.when(F.col("fed_gap_days") <= max_fill_days, F.col("filled_fed"))
        .otherwise(F.lit(None))
        .alias("fedfunds"),
        F.current_timestamp().alias("mart_ts"),
    )

    return final_df
