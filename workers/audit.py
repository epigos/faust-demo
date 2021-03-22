import asyncio
import logging

import faust
import settings
from models import audit

app = faust.App("audit", broker=settings.KAFKA_HOST, datadir="/tmp/audit-data")

extraction_audit_topic = app.topic("extraction-audit", value_type=audit.ExtractionAudit)
category_tag_audit_topic = app.topic(
    "category-audit", value_type=audit.CategoryTagAudit
)


@app.agent(extraction_audit_topic)
async def extraction_audit_stream(stream):
    async for event in stream:
        logging.info(f"Saving audit record {event}")
        await asyncio.sleep(1)


@app.agent(category_tag_audit_topic)
async def category_tag_audit_stream(stream):
    async for event in stream:
        logging.info(f"Saving audit record {event}")
        await asyncio.sleep(1)


if __name__ == "__main__":
    app.main()
