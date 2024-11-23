from prometheus_client import start_http_server, Counter, Gauge
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType  # Import necessary types
import threading

import threading
# Initialize Spark Session
def initialize_spark():
    spark = SparkSession.builder \
        .appName("IoTDataProcessing") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    return spark

# Example metric definitions
processed_records = Counter('processed_records', 'Number of records processed')
processing_latency = Gauge('processing_latency', 'Latency in processing records')

# Function to record metrics
def record_metrics(record_count, latency):
    processed_records.inc(record_count)
    processing_latency.set(latency)

# Start Prometheus server on port 8000
def start_prometheus_server():
    threading.Thread(target=start_http_server, args=(8000,), daemon=True).start()

def main():
    # Initialize Spark session
    spark = initialize_spark()

    # Read data from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "iot_topic") \
        .load()
    
    schema = StructType([
        StructField("Flow_ID", StringType(), True),
        StructField("Src_IP", StringType(), True),
        StructField("Src_Port", IntegerType(), True),
        StructField("Dst_IP", StringType(), True),
        StructField("Dst_Port", IntegerType(), True),
        StructField("Protocol", StringType(), True),
        # Add all other fields accordingly
        StructField("Label", StringType(), True),
        StructField("Cat", StringType(), True),
        StructField("Sub_Cat", StringType(), True),
        StructField("Timestamp", StringType(), True)  # Timestamp is initially a string
    ])

    # Define the timestamp format
    timestamp_format = "dd/MM/yyyy hh:mm:ss a"

    # Parse the "value" column as JSON and extract the fields using the schema
    df_parsed = df.selectExpr("CAST(value AS STRING)") \
    # Parse the "value" column as JSON and extract the fields using the schema
    df_parsed = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    # Convert the "Timestamp" field from String to TimestampType
    df_with_timestamp = df_parsed.withColumn("Timestamp", to_timestamp("Timestamp", timestamp_format))

    # Start Prometheus metrics server
    start_prometheus_server()

    query = df_with_timestamp.writeStream \
        .outputMode("append") \
        .format("console") \
        .foreachBatch(lambda df, epoch_id: record_metrics(df.count(), 0.5)) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
