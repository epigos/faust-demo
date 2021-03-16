import json
import random
import time

from utils import get_client, get_queue_url


def publish_message():
    video_id = random.randint(1, 10000)
    message = {"video_id": video_id, "video_url": f"dummy_{video_id}.mp4"}
    print(f"Sending video message {message} to SQS: {queue_url}")

    sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))


if __name__ == "__main__":
    queue_url = get_queue_url()
    sqs_client = get_client()
    while True:
        publish_message()
        time.sleep(20)
