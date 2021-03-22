import asyncio
import logging
from codecs.avro import avro_category_tag_audit_serializer
from datetime import datetime

import faust
import settings
from models import audit, enums, video

app = faust.App("autotag", broker=settings.KAFKA_HOST, datadir="/tmp/autotag-data")

autotag_topic = app.topic("scale_ai", value_type=video.VideoModel)
audit_topic = app.topic("audit", value_type=audit.CategoryTagAudit)


async def audit_log(value):
    logging.info(f"Publishing ScaleAI audit logs for {value}")
    await audit_topic.send(
        value=value, value_serializer=avro_category_tag_audit_serializer
    )


@app.agent(autotag_topic, sink=[audit_log])
async def autotag(videos):
    async for event in videos:
        logging.info(f"Making ScaleAI prediction for video {event}")
        await asyncio.sleep(1)

        value = dict(
            trace_id=event.trace_id,
            timestamp=datetime.now(),
            stage=enums.Stages.prediction,
            category="commedy",
            strategy=enums.PredictionStrategy.scaleai,
            confidence=90,
        )
        yield value


if __name__ == "__main__":
    app.main()
