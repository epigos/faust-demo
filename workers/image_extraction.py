import asyncio
import logging
from datetime import datetime

import faust
import settings
import utils
from avro_codecs.avro import avro_extraction_audit_serializer, avro_video_serializer
from models import audit, enums, video

app = faust.App(
    "image-extraction", broker=settings.KAFKA_HOST, datadir="/tmp/image-data"
)

image_extraction_topic = app.topic(
    "image-extraction",
    value_type=video.VideoModel,
    value_serializer=avro_video_serializer,
)
autotag_topic = app.topic(
    "autotag", value_type=video.VideoModel, value_serializer=avro_video_serializer
)
scale_ai_topic = app.topic(
    "scale_ai", value_type=video.VideoModel, value_serializer=avro_video_serializer
)
audit_topic = app.topic(
    "extraction-audit",
    value_type=audit.ExtractionAudit,
    value_serializer=avro_extraction_audit_serializer,
)


async def audit_log(value: video.VideoModel):
    value = audit.ExtractionAudit(
        trace_id=value.trace_id,
        timestamp=datetime.now(),
        stage=enums.Stages.extraction.value,
        num_frames=16,
        strategy=enums.ExtractionStrategy.memory.value,
    )
    logging.info(f"Publishing Image Extraction audit logs for {value}")
    await audit_topic.send(
        value=value,
    )


async def prediction_stage(value: video.VideoModel):
    await autotag_topic.send(
        key=str(value.video_id),
        value=value,
    )
    await scale_ai_topic.send(key=str(value.video_id), value=value)


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
                await image_extraction_topic.send(key=str(event.video_id), value=event)
        finally:
            logging.info(f"Sending video to ML prediction stage: {event}")
            yield event


if __name__ == "__main__":
    app.main()
