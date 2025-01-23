#!/bin/bash

# Wait for Zookeeper to start
while ! nc -z zookeeper 2181; do
  sleep 1;
done;

# Wait for Kafka broker to start
while ! nc -z kafka-broker 9092; do
  sleep 1;
done;

# Delete the stock_prices topic if it exists
kafka-topics --delete --topic stock_prices --bootstrap-server kafka-broker:9092 || true;

# Create the stock_prices topic with 5 partitions
kafka-topics --create --topic stock_prices --bootstrap-server kafka-broker:9092 --partitions 5 --replication-factor 1 || true;