import asyncio
import logging
from codecs.avro import avro_extraction_audit_serializer, avro_video_serializer
from datetime import datetime

import faust
import settings
import utils
from models import audit, enums, video

app = faust.App(
    "image-extraction", broker=settings.KAFKA_HOST, datadir="/tmp/image-data"
)

image_extraction_topic = app.topic("image-extraction", value_type=video.VideoModel)
autotag_topic = app.topic("autotag", value_type=video.VideoModel)
scale_ai_topic = app.topic("scale_ai", value_type=video.VideoModel)
audit_topic = app.topic("extraction-audit", value_type=audit.ExtractionAudit)


async def audit_log(value: video.VideoModel):
    value = dict(
        trace_id=value.trace_id,
        timestamp=datetime.now(),
        stage=enums.Stages.extraction,
        num_frames=16,
        strategy=enums.ExtractionStrategy.memory,
    )
    logging.info(f"Publishing Image Extraction audit logs for {value}")
    await audit_topic.send(
        value=value, value_serializer=avro_extraction_audit_serializer
    )


async def prediction_stage(value: video.VideoModel):
    await autotag_topic.send(
        key=str(value.video_id), value=value, value_serializer=avro_video_serializer
    )
    await scale_ai_topic.send(
        key=str(value.video_id), value=value, value_serializer=avro_video_serializer
    )


@app.agent(image_extraction_topic, sink=[prediction_stage, audit_log])
async def image_extraction(videos):
    async for event in videos:
        try:
            logging.info(f"Extracting video frames from {event}")
            await asyncio.sleep(1)

            s3_key = f"s3://scd-tfrecords/{event.video_id}.tfrecord"
            logging.info(f"Uploading video frames to s3: {s3_key}")
            await asyncio.sleep(1)

            event.frames_s3_key = s3_key
        except Exception:
            if event.retry_counter < utils.RETRY_MAX:
                event.retry_counter += 1
                logging.info(f"Requeue video: {event}")
                await image_extraction_topic.send(
                    key=str(event.video_id),
                    value=event,
                    value_serializer=avro_video_serializer,
                )
        finally:
            logging.info(f"Sending video to ML prediction stage: {event}")
            yield event


if __name__ == "__main__":
    app.main()
