from typing import Optional

import faust
from dataclasses_avroschema import AvroModel


class VideoModel(faust.Record, AvroModel, serializer="avro_video"):
    video_id: int
    video_url: str
    trace_id: str
    frames_s3_key: Optional[str] = None
    retry_counter: int = 0

    class Meta:
        namespace = "com.avro"
