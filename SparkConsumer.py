import findspark
findspark.find()

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, when, isnan, col, round
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType, IntegerType, DoubleType

import time

import os
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

TOPIC = config.get("kafka","topic")
BOOTSTRAP_SERVERS = config.get("kafka","bootstrap_servers")
HOST = config.get("postgresql","host")
PORT = config.get("postgresql","port")
TABLE = config.get("postgresql","table")
URL = config.get("postgresql","url")
DRIVER = config.get("postgresql","driver")
USER = config.get("postgresql","user")
PWD = config.get("postgresql","pwd")


def write_to_postgresql(df,epoch_id):
    df.write \
    .format("jdbc") \
    .options(url=URL,
            driver=DRIVER,
            dbtable=TABLE,
            user=USER,
            password=PWD,
            ) \
    .mode("append") \
    .save()

if __name__ == "__main__":
    print("Stream Data Processing Starting ...")
    print(time.strftime("%Y-%m-%d %H:%M:%S"))

    spark = SparkSession \
        .builder \
        .appName("PySpark Streaming") \
        .master("local[*]") \
        .getOrCreate()

    data_stream = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", BOOTSTRAP_SERVERS) \
        .option("subscribe", TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    # Define a schema for the data
    orders_schema=StructType() \
	.add("Invoice",StringType()) \
	.add("StockCode",StringType()) \
	.add("Description",StringType()) \
	.add("Quantity",StringType()) \
	.add("InvoiceDate",StringType()) \
	.add("Price",StringType()) \
	.add("CustomerID",StringType()) \
	.add("Country",StringType())

    
    df_order = data_stream.selectExpr("CAST(value AS STRING)") \
                          .select(from_json(col("value"), orders_schema).alias("order")) \
                          .select("order.*")

    df_order.printSchema()
    print(df_order.columns)
    df_order_transformed = df_order.withColumn("Description", when(isnan(col("Description")), "Description Not Provided").otherwise(col("Description"))) \
                                   .withColumn("Cancelled",col("Invoice").rlike("^C")) \
                                   .withColumn("Cancelled", when(col("Cancelled") == "true", "1").otherwise("0")) \
                                   .withColumn("Price", when(col("Price") < "0", "0").otherwise(col("Price"))) \
                                   .withColumn("Quantity", when(col("Quantity") < "0", "0").otherwise(col("Quantity"))) \
                                   .withColumn("Total", round(col("Price")*col("Quantity"), 2)) \
                                   .withColumn("Price", col("Price").cast(DoubleType())) \
                                   .withColumn("Quantity", col("Quantity").cast(DoubleType())) \
                                   .withColumn("InvoiceDate", col("InvoiceDate").cast(TimestampType())) \
                                   .where(col("CustomerID").isNotNull())

    # Agregeting Total Amount
    df_order_agregated=df_order_transformed.groupBy("Invoice","InvoiceDate","CustomerID","Country","Cancelled") \
                                           .agg({"Total":"sum"}).select("Invoice","InvoiceDate","CustomerID","Country","Cancelled",col("sum(total)").alias("total_amount"))

    df_order_agregated.printSchema()
    postgresql_stream=df_order_agregated.writeStream \
        .trigger(processingTime="5 seconds") \
        .outputMode("update") \
        .foreachBatch(write_to_postgresql) \
        .start()

    spark.streams.awaitAnyTermination()

    print("Stream Processing Completed")