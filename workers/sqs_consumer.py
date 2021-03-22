import asyncio
import json
import logging
import uuid

import faust
import settings
import utils
from avro_codecs.avro import avro_video_serializer
from models import video

app = faust.App("sqs", broker=settings.KAFKA_HOST, datadir="/tmp/sqs-data")

image_extraction_topic = app.topic(
    "image-extraction",
    value_type=video.VideoModel,
    value_serializer=avro_video_serializer,
)
queue_url = utils.get_queue_url()
sqs_client = utils.get_client()


@app.timer(10, on_leader=True)
async def listen():
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
    )
    messages = response.get("Messages", [])
    if messages:
        logging.info(f"Received messages {len(messages)} from {queue_url}")

    for msg in messages:
        body = json.loads(msg["Body"])
        receipt_handle = msg["ReceiptHandle"]

        logging.info(f"Obtaining audit trace id for {msg}")
        trace_id = str(uuid.uuid4())

        await asyncio.sleep(1)

        value = video.VideoModel(
            video_id=body["video_id"], video_url=body["video_url"], trace_id=trace_id
        )

        logging.info(
            f"Message published successfully to kafka topic {image_extraction_topic}"
        )
        await image_extraction_topic.send(
            key=str(body["video_id"]),
            value=value,
        )

        logging.info(f"Deleting SQS message {receipt_handle}")
        sqs_client.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle)


if __name__ == "__main__":
    app.main()
