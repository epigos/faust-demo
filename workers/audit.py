import asyncio
import logging
import os

import faust
import utils

kafka_host = os.environ.get("KAFKA_HOST", "kafka://localhost")
app = faust.App("audit", broker=kafka_host, datadir="/tmp/audit-data")

audit_topic = app.topic("audit", value_type=utils.AuditSchema)


@app.agent(audit_topic)
async def image_extraction(stream):
    async for audit in stream:
        logging.info(f"Saving audit record {audit}")
        await asyncio.sleep(1)


if __name__ == "__main__":
    app.main()
