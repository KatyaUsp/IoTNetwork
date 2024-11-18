# pyspark/pyspark_streaming.py

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import *

def main():
    # Initialize Spark Session
    spark = SparkSession.builder \
        .appName("IoTDataProcessing") \
        .config("spark.es.nodes", "elasticsearch") \
        .config("spark.es.port", "9200") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    
    # Define the schema based on your dataset fields
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
        StructField("Timestamp", TimestampType(), True)
    ])

    # Read data from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "iot_topic") \
        .load()

    # Define the timestamp format
    timestamp_format = "dd/MM/yyyy hh:mm:ss a"

    df_with_timestamp = df.withColumn("Timestamp", to_timestamp("Timestamp", timestamp_format))

    df_parsed = df_with_timestamp.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")
    
    # Perform transformations if needed
    # For example, filter anomalies
    #anomalies = df_parsed.filter(col("Label") != "Benign")

    #Write the stream to console (for testing)
    # query = df_parsed.writeStream \
    #     .outputMode("append") \
    #     .format("console") \
    #     .start()

    #Alternatively, write to Elasticsearch for real-time analytics
# ... previous code ...

    query = df_parsed.writeStream \
        .outputMode("append") \
        .format("es") \
        .option("checkpointLocation", "/tmp/checkpoints") \
        .option("es.resource", "iot_index_4") \
        .start()

# ... rest of the code ...



    query.awaitTermination()

if __name__ == "__main__":
    main()



