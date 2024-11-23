from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp
from pyspark.sql.types import *

def main():
    # Initialize the Spark session
    spark = SparkSession.builder \
        .appName("IoTDataProcessing") \
        .config("spark.es.nodes", "elasticsearch") \
        .config("spark.es.port", "9200") \
        .config("spark.es.nodes.wan.only", "true") \
        .config("spark.es.net.ssl.cert.allow.self.signed", "true") \
        .config("spark.es.net.ssl", "false") \
        .config("spark.es.net.ssl.verification", "false") \
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
        StructField("Timestamp", StringType(), True)  
    ])

    # Read data from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "iot_topic") \
        .load()

   
    # Parse the "value" column as JSON and extract the fields using the schema
    df_parsed = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")
    
    device_ips = ['192.168.0.13', '192.168.0.24', '192.168.0.16'] 

    # Filter the DataFrame by IP and create separate streams for each device
    df_device_1 = df_parsed.filter(col("Src_IP") == device_ips[0])
    df_device_2 = df_parsed.filter(col("Src_IP") == device_ips[1])
    df_device_3 = df_parsed.filter(col("Src_IP") == device_ips[2])

    # Set checkpoint directory for each stream (you can use different directories if needed)
    checkpoint_dir = "/tmp/spark_checkpoint"  # You can choose any directory here

    # Write the streams to different outputs (e.g., console or Elasticsearch) for each device
    query_device_1 = df_device_1.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("checkpointLocation", checkpoint_dir + "/device_1") \
        .start()

    query_device_2 = df_device_2.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("checkpointLocation", checkpoint_dir + "/device_2") \
        .start()

    query_device_3 = df_device_3.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("checkpointLocation", checkpoint_dir + "/device_3") \
        .start()

    # Await termination of the streams
    query_device_1.awaitTermination()
    query_device_2.awaitTermination()
    query_device_3.awaitTermination()

if __name__ == "__main__":
    main()
   