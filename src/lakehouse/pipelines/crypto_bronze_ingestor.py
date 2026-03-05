import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from pyspark.sql import Row, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StringType,
    StructField,
    StructType,
    TimestampType,
)

from lakehouse.ingestion import (
    fetch_pages_concurrently,
    resolve_symbol_start_for_realtime,
)


class CryptoBronzeIngestor:
    """
    Orchestrates the ingestion of crypto market data from an API Client
    into a Bronze Delta Table.
    """

    def __init__(
        self,
        spark: SparkSession,
        catalog: str,
        schema: str,
        table_name: str,
        api_client: Any,
        source_name: str = "coinbase",
    ):
        self.spark = spark
        self.target_table = f"{catalog}.{schema}.{table_name}"
        self.api_client = api_client
        self.source_name = source_name

    def _get_watermarks(self, symbols: List[str], interval: str) -> Dict[str, datetime]:
        """Fetch the latest event_time for each symbol to resume ingestion."""
        wm_by_symbol = {}
        if self.spark.catalog.tableExists(self.target_table):
            # Using DataFrame API to find max event_time per symbol
            wm_rows = (
                self.spark.table(self.target_table)
                .where((F.col("source") == self.source_name) & (F.col("interval") == interval))
                .where(F.col("symbol").isin(symbols))
                .groupBy("symbol")
                .agg(F.max("event_time").alias("mx"))
                .collect()
            )
            wm_by_symbol = {r["symbol"].upper(): r["mx"] for r in wm_rows if r["mx"] is not None}
        return wm_by_symbol

    def _resolve_days_to_fetch(
        self,
        mode: str,
        symbols: List[str],
        interval: str,
        start_date: Optional[datetime],
        end_date: datetime,
        max_days: int,
        default_lookback_days: int,
        repair_start_date: Optional[datetime] = None,
        repair_end_date: Optional[datetime] = None,
    ) -> Dict[str, List[datetime]]:
        """Determine exactly which days each symbol needs to fetch."""

        days_by_symbol = {}

        if mode == "backfill":
            if not start_date:
                raise ValueError("backfill mode requires start_date")

            if end_date < start_date:
                raise ValueError(
                    f"end_date {end_date.date()} must be >= start_date {start_date.date()}"
                )

            num_days = (end_date.date() - start_date.date()).days + 1
            if num_days > max_days:
                raise ValueError(f"Requested {num_days} days exceeds limit of {max_days}.")

            shared_days = [start_date + timedelta(days=i) for i in range(num_days)]
            days_by_symbol = {sym: shared_days for sym in symbols}

        elif mode == "realtime":
            wm_by_symbol = self._get_watermarks(symbols, interval)

            for sym in symbols:
                sym_upper = sym.upper()
                if start_date:
                    sym_start = start_date
                else:
                    wm = wm_by_symbol.get(sym_upper)
                    sym_start = resolve_symbol_start_for_realtime(
                        watermark=wm,
                        end_dt=end_date,
                        lookback_days=default_lookback_days,
                        interval=interval,
                    )

                if sym_start > end_date:
                    days_by_symbol[sym] = []
                    continue

                req_days = (end_date.date() - sym_start.date()).days + 1
                if req_days > max_days:
                    raise ValueError(
                        f"{sym}: requested {req_days} days exceeds limit of {max_days}."
                    )

                days_by_symbol[sym] = [sym_start + timedelta(days=i) for i in range(req_days)]
        else:
            raise ValueError("mode must be 'backfill' or 'realtime'")

        # Inject repair windows if specified
        if repair_start_date:
            repair_end = repair_end_date or end_date
            if repair_end < repair_start_date:
                raise ValueError("repair_end_date must be >= repair_start_date")

            repair_num_days = (repair_end.date() - repair_start_date.date()).days + 1
            repair_days = [repair_start_date + timedelta(days=i) for i in range(repair_num_days)]

            for sym in symbols:
                merged = sorted(set(days_by_symbol.get(sym, []) + repair_days))
                if len(merged) > max_days:
                    raise ValueError(
                        f"{sym}: merged repair days {len(merged)} exceeds max_days {max_days}."
                    )
                days_by_symbol[sym] = merged

        return days_by_symbol

    def run(
        self,
        mode: str,
        symbols: List[str],
        interval: str,
        end_date: datetime,
        start_date: Optional[datetime] = None,
        max_days: int = 7,
        default_lookback_days: int = 1,
        repair_start_date: Optional[datetime] = None,
        repair_end_date: Optional[datetime] = None,
        max_workers: int = 4,
    ) -> Dict[str, Any]:
        """
        Executes the ingestion pipeline.
        Returns a summary dictionary with execution metrics.
        """

        # 1. Resolve Extraction Window
        days_by_symbol = self._resolve_days_to_fetch(
            mode=mode,
            symbols=symbols,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            max_days=max_days,
            default_lookback_days=default_lookback_days,
            repair_start_date=repair_start_date,
            repair_end_date=repair_end_date,
        )

        total_days_to_fetch = sum(len(days) for days in days_by_symbol.values())
        print(
            f"[INFO] Ingestor resolved total {total_days_to_fetch} symbol-day tasks across {len(symbols)} symbols."
        )

        if total_days_to_fetch == 0:
            return {"status": "skipped", "reason": "No new days to fetch", "rows_written": 0}

        # 2. Extract Data Concurrently using injected API client
        all_pages = []
        all_errors = []

        for sym in symbols:
            sym_days = days_by_symbol.get(sym, [])
            if not sym_days:
                continue

            print(f"[INFO] Fetching {sym} for {len(sym_days)} day(s)...")
            # We map backfill_klines_one_day from the client
            sym_pages, sym_errors = fetch_pages_concurrently(
                symbols=[sym],
                days=sym_days,
                interval=interval,
                fetch_func=self.api_client.backfill_klines_one_day,
                max_workers=max_workers,
            )
            all_pages.extend(sym_pages)
            all_errors.extend(sym_errors)

        if all_errors:
            print(f"[WARN] Encountered {len(all_errors)} errors during concurrent fetch:")
            for err in all_errors[:10]:
                print(err)

        # 3. Transform Raw Pages to Spark DataFrame Rows
        rows = []
        run_id = str(uuid.uuid4())
        ingestion_ts = datetime.now(timezone.utc)
        kept_pages = 0
        skipped_empty = 0

        for sym, day_start, pages in all_pages:
            for p in pages:
                kline_count = int(p.get("kline_count", 0) or 0)
                if kline_count <= 0:
                    skipped_empty += 1
                    continue

                kept_pages += 1
                rows.append(
                    Row(
                        source=self.source_name,
                        symbol=sym.upper(),
                        interval=interval,
                        event_time=day_start.replace(tzinfo=timezone.utc),
                        raw_json=json.dumps(p, separators=(",", ":")),
                        run_id=run_id,
                        ingestion_ts=ingestion_ts,
                    )
                )

        print(
            f"[INFO] Bronze transformation: kept_pages={kept_pages}, skipped_empty={skipped_empty}, rows_to_write={len(rows)}"
        )

        # 4. Load (Write to Delta Lake)
        if rows:
            schema = StructType(
                [
                    StructField("source", StringType(), False),
                    StructField("symbol", StringType(), False),
                    StructField("interval", StringType(), False),
                    StructField("event_time", TimestampType(), True),
                    StructField("raw_json", StringType(), False),
                    StructField("run_id", StringType(), False),
                    StructField("ingestion_ts", TimestampType(), False),
                ]
            )

            # Ensure target table exists before writing
            self.spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {self.target_table} (
              source STRING,
              symbol STRING,
              interval STRING,
              event_time TIMESTAMP,
              raw_json STRING,
              run_id STRING,
              ingestion_ts TIMESTAMP
            )
            USING DELTA
            """)

            df = self.spark.createDataFrame(rows, schema=schema).dropDuplicates()

            # Upsert behavior (Append with potential dedup later on silver)
            df.write.mode("append").format("delta").saveAsTable(self.target_table)

            return {
                "status": "success",
                "rows_written": len(rows),
                "run_id": run_id,
                "errors": len(all_errors),
            }

        return {"status": "success", "rows_written": 0, "errors": len(all_errors)}
