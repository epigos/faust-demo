import boto3
import settings

RETRY_MAX = 3


def get_client():
    sqs_client = boto3.session.Session().client(
        service_name="sqs",
        region_name="eu-west-2",
        aws_access_key_id="fake",
        aws_secret_access_key="fake",
        endpoint_url=settings.AWS_ENDPOINT_URL,
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
