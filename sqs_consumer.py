import json
import os
import time
import uuid

from kafka import KafkaProducer

from utils import get_client, get_queue_url

TOPIC = "image-extraction"


def publish_message(producer_instance, topic_name, key, value):
    try:
        key_bytes = bytes(str(key), encoding="utf-8")
        value_bytes = bytes(value, encoding="utf-8")
        producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
        producer_instance.flush()
        print(f"Message published successfully to kafka topic {TOPIC}")
    except Exception as ex:
        print("Exception in publishing message")
        print(ex)


def connect_kafka_producer():
    _producer = None
    try:
        # host.docker.internal is how a docker container connects to the local
        # machine.
        # Don't use in production, this only works with Docker for Mac in
        # development
        _producer = KafkaProducer(
            bootstrap_servers=[os.environ.get("KAFKA_HOST", "localhost:9092")],
            api_version=(0, 10),
        )
    except Exception as ex:
        print("Exception while connecting Kafka")
        print(ex)
    return _producer


def listen():
    print(f"Consuming messages from {queue_url}")

    response = sqs_client.receive_message(
        QueueUrl=queue_url,
    )
    for msg in response.get("Messages", []):
        body = json.loads(msg["Body"])
        receipt_handle = msg["ReceiptHandle"]

        print(f"Obtaining audit trace id for {msg}")

        time.sleep(1)
        body["trace_id"] = str(uuid.uuid4())

        publish_message(kafka_producer, TOPIC, body["video_id"], json.dumps(body))
        sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)


if __name__ == "__main__":
    queue_url = get_queue_url()
    sqs_client = get_client()
    kafka_producer = connect_kafka_producer()
    while True:
        listen()
        time.sleep(10)
