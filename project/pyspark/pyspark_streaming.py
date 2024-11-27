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
        StructField("Timestamp", StringType(), True)  # Timestamp is initially a string
    ])

    #Schema definition
    # schema_ls = []

    # f_num = open('numeric_cols.txt', 'r')

    # for num_col in f_num:
    #     schema_ls.append(StructField(num_col, IntegerType(), True))

    # f_num.close()

    # f_non_num = open('non_numeric_cols.txt', 'r')

    # for non_num_col in f_non_num:
    #     schema_ls.append(StructField(non_num_col, StringType(), True))

    # f_non_num.close()

    # schema = StructType(schema_ls)

    # Read data from Kafka
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "iot_topic") \
        .load()

    # Define the timestamp format
    timestamp_format = "dd/MM/yyyy hh:mm:ss a"

    # Parse the "value" column as JSON and extract the fields using the schema
    df_parsed = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")

    # Convert the "Timestamp" field from String to TimestampType
    df_with_timestamp = df_parsed.withColumn("Timestamp", to_timestamp("Timestamp", timestamp_format))

    # Set a checkpoint location for the Elasticsearch commit log
    checkpoint_dir = "/tmp/spark_checkpoint"  # You can choose any directory here

    # Write the parsed data to Elasticsearch with checkpointing
    query = df_with_timestamp.writeStream \
        .outputMode("append") \
        .format("org.elasticsearch.spark.sql") \
        .option("es.resource", "iot_index") \
        .option("checkpointLocation", checkpoint_dir) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
