import logging
import os

KAFKA_HOST = os.environ.get("KAFKA_HOST", "kafka://broker:9092")

SCHEMA_REGISTRY_URL = os.environ.get(
    "SCHEMA_REGISTRY_URL", "http://schema-registry:8081"
)

AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL")

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(asctime)s pid:%(process)s module:%(module)s %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)
