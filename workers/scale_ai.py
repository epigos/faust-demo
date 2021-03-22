import asyncio
import logging
from datetime import datetime

import faust
import settings
from avro_codecs.avro import avro_category_tag_audit_serializer
from models import audit, enums, video

app = faust.App("autotag", broker=settings.KAFKA_HOST, datadir="/tmp/autotag-data")

autotag_topic = app.topic("scale_ai", value_type=video.VideoModel)
audit_topic = app.topic(
    "audit",
    value_type=audit.CategoryTagAudit,
    value_serializer=avro_category_tag_audit_serializer,
)


async def audit_log(value):
    logging.info(f"Publishing ScaleAI audit logs for {value}")
    await audit_topic.send(
        value=value,
    )


@app.agent(autotag_topic, sink=[audit_log])
async def autotag(videos):
    async for event in videos:
        logging.info(f"Making ScaleAI prediction for video {event}")
        await asyncio.sleep(1)

        value = audit.CategoryTagAudit(
            trace_id=event.trace_id,
            timestamp=datetime.now(),
            stage=enums.Stages.prediction.value,
            category="commedy",
            strategy=enums.PredictionStrategy.scaleai.value,
            confidence=90,
        )
        yield value


if __name__ == "__main__":
    app.main()
