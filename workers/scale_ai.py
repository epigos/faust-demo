import asyncio
import logging
import os
from datetime import datetime

import faust
import utils

kafka_host = os.environ.get("KAFKA_HOST", "kafka://localhost")
app = faust.App("scale_ai", broker=kafka_host, datadir="/tmp/scale_ai-data")

scale_ai_topic = app.topic("scale_ai", value_type=utils.VideoSchema)
audit_topic = app.topic("audit", value_type=utils.AuditSchema)


async def audit_log(audit):
    logging.info(f"Publishing audit logs for {audit}")
    await audit_topic.send(value=audit)


@app.agent(scale_ai_topic, sink=[audit_log])
async def scale_ai(videos):
    async for video in videos:
        logging.info(f"Making Scale AI prediction for video {video}")
        await asyncio.sleep(1)

        audit = utils.AuditSchema(
            trace_id=video.trace_id,
            timestamp=datetime.now(),
            stage="prediction",
            log=dict(category="sports", strategy="scale_ai", confidence=90),
        )
        yield audit


if __name__ == "__main__":
    app.main()
