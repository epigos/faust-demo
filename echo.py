import logging
import os

import faust

import utils

kafka_host = os.environ.get("KAFKA_HOST", "kafka://localhost")
app = faust.App("echo", broker=kafka_host, datadir="/tmp/{appid}-data")

ml_topic = app.topic("prediction", value_type=utils.VideoSchema)
autotag_topic = app.topic("autotag", value_type=utils.VideoSchema)
scale_ai_topic = app.topic("scale_ai", value_type=utils.VideoSchema)


@app.agent(ml_topic)
async def process(stream):
    async for event in stream.echo(autotag_topic, scale_ai_topic):
        logging.info(f"Forwarded video {event} to {autotag_topic} and {scale_ai_topic}")


if __name__ == "__main__":
    app.main()
