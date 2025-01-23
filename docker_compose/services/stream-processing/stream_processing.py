from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_json, struct, window, avg
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# Initialize Spark Session
spark = SparkSession.builder \
    .appName("Time-Based-SMA") \
    .getOrCreate()

# Kafka configuration
KAFKA_BROKER = "192.168.1.10:9092"
INPUT_TOPIC = "stock_prices"
OUTPUT_TOPIC = "SMA"

# Schema for stock price data
schema = StructType([
    StructField("stock_symbol", StringType(), True),
    StructField("opening_price", DoubleType(), True),
    StructField("closing_price", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("volume", DoubleType(), True),
    StructField("timestamp", TimestampType(), True),  # Use TimestampType for time-based processing
    StructField("local_time", StringType(), True)
])

# Read data from Kafka
raw_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", INPUT_TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

# Parse JSON data
parsed_stream = raw_stream.selectExpr("CAST(value AS STRING)") \
    .withColumn("data", from_json(col("value"), schema)) \
    .select("data.*")

# Calculate SMA using a time-based window
# Window duration: 3 minutes, Sliding interval: 1 minute
sma_stream = parsed_stream \
    .withWatermark("timestamp", "3 minutes") \
    .groupBy(
        window(col("timestamp"), "3 minutes", "1 minute"),
        col("stock_symbol")
    ) \
    .agg(avg("closing_price").alias("SMA")) \
    .select(
        col("stock_symbol"),
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("SMA")
    )

# Prepare data for writing back to Kafka
output_stream = sma_stream.selectExpr(
    "CAST(stock_symbol AS STRING) AS key",
    "to_json(struct(*)) AS value"
)

# Write SMA to Kafka
query = output_stream.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("topic", OUTPUT_TOPIC) \
    .option("checkpointLocation", "/tmp/spark-checkpoints/time-based-sma") \
    .start()

query.awaitTermination()
