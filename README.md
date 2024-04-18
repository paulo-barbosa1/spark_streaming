# Quickstart

## Setup
Clone the repository and run pip install so you can run the project.
Make sure you have Installed python 3.11, Spark 3.5.2 and Docker.

```
cd Spark_Stuctured_Streaming
pip install -r requirement.txt
docker-compose up -d
```

### 1) Create a Server
Connect pgAdmin to our database to see the data. You can access the pgAdmin GUI through http://localhost:5050/

- hostname : postgres
- port : 5432
- username : admin
- password : admin 

### 2) Create a Database and a table
```
cd postgresql
python create_database.py
python create_table
```

These scripts will configure the start of our database.
## Kafka Spark Stuctured Streaming configuration
#### Setup Kafka Manager

Access http://localhos:9000/addCluster :

* Cluster name: Kafka
* Zookeeper hosts: localhost:2181

### 1) Kafka Producer
The command will start a simulated streaming process from our order_data.csv.

```
spark-submit kafka_producer.py
```

### 2) Spark Consumer 
This command will start consuming the data from the topic of the Kafka producer, do some transformation, and write the result to our SQL database. 
```
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.2.18 SparkConsumer.py
```
