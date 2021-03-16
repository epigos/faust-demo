import asyncio
import logging
import os
from datetime import datetime

import faust
import utils

kafka_host = os.environ.get("KAFKA_HOST", "kafka://localhost")
app = faust.App("image-extraction", broker=kafka_host, datadir="/tmp/image-data")

image_extraction_topic = app.topic("image-extraction", value_type=utils.VideoSchema)
prediction_topic = app.topic("prediction", value_type=utils.VideoSchema)
audit_topic = app.topic("audit", value_type=utils.AuditSchema)


async def audit_log(video: utils.VideoSchema):
    audit = utils.AuditSchema(
        trace_id=video.trace_id,
        timestamp=datetime.now(),
        stage="extraction",
        log=dict(num_frames=16, strategy="basic"),
    )
    logging.info(f"Publishing audit logs for {audit}")
    await audit_topic.send(value=audit)


@app.agent(image_extraction_topic, sink=[audit_log])
async def image_extraction(videos):
    async for video in videos:
        try:
            logging.info(f"Extracting video frames from {video}")
            await asyncio.sleep(1)

            s3_key = f"s3://scd-tfrecords/{video.video_id}.tfrecord"
            logging.info(f"Uploading video frames to s3: {s3_key}")
            await asyncio.sleep(1)

            video.frames_s3_key = s3_key
            logging.info(f"Sending video to ML prediction stage: {video}")
            await prediction_topic.send(key=str(video.video_id), value=video)

        except Exception:
            if video.retry_counter < utils.RETRY_MAX:
                video.retry_counter += 1
                logging.info(f"Retrying video: {video}")
                await image_extraction_topic.send(key=str(video.video_id), value=video)
        finally:
            yield video


if __name__ == "__main__":
    app.main()
