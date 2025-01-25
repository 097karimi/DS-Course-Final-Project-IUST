import logging
import json
import math
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from kafka import KafkaProducer
import psycopg2  # For inserting into QuestDB

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
def configure_logging():
    logging.basicConfig(level=logging.WARNING)

# -----------------------------------------------------------------------------
# Spark Session Initialization
# -----------------------------------------------------------------------------
def initialize_spark_session():
    """Initialize Spark session and configure log level."""
    spark = SparkSession.builder \
        .appName("OneRowPerSymbolMinute") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
        .config("spark.executor.extraJavaOptions", "-Dlog4j.configuration=log4j.properties") \
        .config("spark.driver.extraJavaOptions", "-Dlog4j.configuration=log4j.properties") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark

# -----------------------------------------------------------------------------
# QuestDB Configuration
# -----------------------------------------------------------------------------
QUESTDB_HOST = "questdb"
QUESTDB_PORT = 8812
QUESTDB_DATABASE = "qdb"
QUESTDB_USER = "admin"
QUESTDB_PASSWORD = "quest"

def insert_batch_to_questdb(records):
    """Insert record dicts into QuestDB's 'stock_data' table."""
    if not records:
        return

    try:
        conn = psycopg2.connect(
            dbname=QUESTDB_DATABASE,
            user=QUESTDB_USER,
            password=QUESTDB_PASSWORD,
            host=QUESTDB_HOST,
            port=QUESTDB_PORT
        )
        logging.warning("Successfully connected to QuestDB.")
    except Exception as e:
        logging.error(f"Error connecting to QuestDB: {e}")
        return

    try:
        query = """
        INSERT INTO stock_data (
            stock_symbol, local_time, open, high, low, close, volume,
            SMA_5, EMA_10, delta, gain, loss, avg_gain_10, avg_loss_10,
            rs, RSI_10, signal
        )
        VALUES (
            %(stock_symbol)s, %(local_time)s, %(open)s, %(high)s, %(low)s,
            %(close)s, %(volume)s, %(SMA_5)s, %(EMA_10)s, %(delta)s,
            %(gain)s, %(loss)s, %(avg_gain_10)s, %(avg_loss_10)s,
            %(rs)s, %(RSI_10)s, %(signal)s
        );
        """
        with conn.cursor() as cur:
            for record in records:
                # Clean NaN values
                for k, v in record.items():
                    if isinstance(v, float) and math.isnan(v):
                        record[k] = None
                    elif isinstance(v, str) and v.lower() == "nan":
                        record[k] = None

                cur.execute(query, record)
        conn.commit()
        logging.warning(f"Inserted {len(records)} new records into QuestDB.")
    except Exception as e:
        logging.error(f"Error inserting into QuestDB: {e}")
    finally:
        conn.close()

# -----------------------------------------------------------------------------
# Compute Technical Indicators
# -----------------------------------------------------------------------------
def compute_indicators_for_group(group_df: pd.DataFrame):
    """Compute technical indicators for a group of data."""
    gdf = group_df.copy()
    gdf["SMA_5"] = gdf["close"].rolling(window=5).mean()
    gdf["EMA_10"] = gdf["close"].ewm(span=10, adjust=False, min_periods=10).mean()

    gdf["delta"] = gdf["close"].diff()
    gdf["gain"] = gdf["delta"].clip(lower=0)
    gdf["loss"] = -gdf["delta"].clip(upper=0)
    gdf["avg_gain_10"] = gdf["gain"].rolling(window=10).mean()
    gdf["avg_loss_10"] = gdf["loss"].rolling(window=10).mean()

    gdf["rs"] = gdf["avg_gain_10"] / gdf["avg_loss_10"].replace({0: None})
    gdf["RSI_10"] = 100 - (100 / (1 + gdf["rs"]))
    return gdf

# -----------------------------------------------------------------------------
# Generate Trading Signals
# -----------------------------------------------------------------------------
def generate_signals_scenario_b(df: pd.DataFrame) -> pd.DataFrame:
    """Generate trading signals based on crossover and RSI."""
    def get_signal(row):
        rsi, sma_5, ema_10 = row["RSI_10"], row["SMA_5"], row["EMA_10"]
        if pd.isnull(rsi) or pd.isnull(sma_5) or pd.isnull(ema_10):
            return "HOLD"
        if (sma_5 > ema_10) and (rsi < 70):
            return "BUY"
        elif (sma_5 < ema_10) and (rsi > 30):
            return "SELL"
        else:
            return "HOLD"

    df["signal"] = df.apply(get_signal, axis=1)
    return df

# -----------------------------------------------------------------------------
# Process Each Micro-Batch
# -----------------------------------------------------------------------------
already_sent = set()
global_data = pd.DataFrame(columns=[
    "stock_symbol", "local_time", "open", "high", "low", "close", "volume"
])

def process_batch(batch_df, batch_id):
    """Process each micro-batch from the data stream."""
    print(f"\n=== Processing Micro-Batch: {batch_id} ===")
    spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "false")

    batch_df = batch_df.selectExpr(
        "stock_symbol",
        "CAST(local_time AS STRING) AS local_time_str",
        "open", "high", "low", "close", "volume"
    )

    pdf = batch_df.toPandas()
    if pdf.empty:
        print("No new data in this batch.")
        return

    global global_data
    pdf["local_time"] = pd.to_datetime(pdf["local_time_str"])
    pdf.drop(columns=["local_time_str"], inplace=True)

    global_data = pd.concat([global_data, pdf], ignore_index=True)
    global_data.sort_values(["stock_symbol", "local_time"], inplace=True)
    updated_pdf = global_data.groupby("stock_symbol", group_keys=False).apply(compute_indicators_for_group)
    updated_pdf.reset_index(drop=True, inplace=True)

    updated_pdf = generate_signals_scenario_b(updated_pdf)

    latest_symbol_time = updated_pdf.groupby(["stock_symbol", "local_time"], group_keys=False).tail(1)

    new_records = []
    for row_dict in latest_symbol_time.to_dict(orient="records"):
        combo = (row_dict["stock_symbol"], row_dict["local_time"])
        if combo not in already_sent:
            new_records.append(row_dict)
            already_sent.add(combo)

    if not new_records:
        print("No newly updated rows to send this batch.")
        return

    send_to_kafka(new_records)
    insert_batch_to_questdb(new_records)

def send_to_kafka(records):
    """Send new records to Kafka."""
    producer = KafkaProducer(
        bootstrap_servers=[kafka_broker],
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
    )
    for row in records:
        producer.send(output_topic, row)
    producer.flush()
    producer.close()
    print(f"Sent {len(records)} new (symbol, local_time) combos to Kafka topic: {output_topic}")

# -----------------------------------------------------------------------------
# Main Application Setup
# -----------------------------------------------------------------------------
def main():
    configure_logging()
    spark = initialize_spark_session()

    kafka_broker = "kafka-broker:9092"
    input_topics = "btcirt_topic,usdtirt_topic,ethirt_topic,etcirt_topic,shibirt_topic"
    output_topic = "output_topic"

    schema = StructType([
        StructField("stock_symbol", StringType(), True),
        StructField("local_time", TimestampType(), True),
        StructField("open", DoubleType(), True),
        StructField("high", DoubleType(), True),
        StructField("low", DoubleType(), True),
        StructField("close", DoubleType(), True),
        StructField("volume", DoubleType(), True)
    ])

    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_broker) \
        .option("subscribe", input_topics) \
        .option("startingOffsets", "earliest") \
        .load()

    value_df = df.select(
        from_json(col("value").cast("string"), schema).alias("data")
    ).select("data.*")

    query = value_df.writeStream \
        .foreachBatch(process_batch) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
