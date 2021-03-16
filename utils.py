import logging
import os
from datetime import datetime
from typing import Optional

import boto3
import faust

RETRY_MAX = 3


class VideoSchema(faust.Record):
    video_id: int
    video_url: str
    trace_id: str
    frames_s3_key: Optional[str]
    retry_counter: int = 0


class AuditSchema(faust.Record):
    trace_id: str
    stage: str
    timestamp: datetime
    log: Optional[dict]


def get_client():
    sqs_client = boto3.session.Session().client(
        service_name="sqs",
        region_name="eu-west-2",
        aws_access_key_id="fake",
        aws_secret_access_key="fake",
        endpoint_url=os.environ.get("AWS_ENDPOINT_URL"),
    )
    return sqs_client


def get_queue_url():
    client = get_client()
    queue_name = "scd"
    try:
        resp = client.get_queue_url(QueueName=queue_name)
    except Exception:
        resp = client.create_queue(QueueName=queue_name)

    return resp["QueueUrl"]


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(asctime)s pid:%(process)s module:%(module)s %(message)s",
    datefmt="%d/%m/%y %H:%M:%S",
)
