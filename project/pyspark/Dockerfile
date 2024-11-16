# pyspark/Dockerfile

FROM bitnami/spark:latest

# Install necessary tools
USER root
RUN apt-get update && apt-get install -y wget unzip

# Switch back to non-root user
USER 1001

# Copy the PySpark application
COPY pyspark_streaming.py /app/

ENV SPARK_HOME=/opt/bitnami/spark
ENV PATH=$SPARK_HOME/bin:$PATH
ENV PYTHONPATH=$SPARK_HOME/python/:$PYTHONPATH
ENV PYSPARK_PYTHON=python3

# Set the default command with required packages and repositories
CMD ["spark-submit", \
     "--repositories", "https://artifacts.elastic.co/maven", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.2.0", \
     "/app/pyspark_streaming.py"]
