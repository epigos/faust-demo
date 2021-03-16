import asyncio
import logging
import os
from datetime import datetime

import faust

import utils

kafka_host = os.environ.get("KAFKA_HOST", "kafka://localhost")
app = faust.App("autotag", broker=kafka_host, datadir="/tmp/{appid}-data")

autotag_topic = app.topic("autotag", value_type=utils.VideoSchema)
audit_topic = app.topic("audit", value_type=utils.AuditSchema)


async def audit_log(audit):
    logging.info(f"Publishing audit logs for {audit}")
    await audit_topic.send(value=audit)


@app.agent(autotag_topic, sink=[audit_log])
async def autotag(videos):
    async for video in videos:
        logging.info(f"Making AutoTag prediction for video {video}")
        await asyncio.sleep(1)

        audit = utils.AuditSchema(
            trace_id=video.trace_id,
            timestamp=datetime.now(),
            stage="prediction",
            log=dict(category="commedy", strategy="autotag", confidence=90),
        )
        yield audit


if __name__ == "__main__":
    app.main()
