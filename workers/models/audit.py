from dataclasses import dataclass
from datetime import datetime

import faust
from dataclasses_avroschema import AvroModel, types
from models import enums


@dataclass
class Audit(faust.Record, AvroModel):
    trace_id: str
    timestamp: datetime
    stage: types.Enum = types.Enum(
        enums.Stages.choices(), default=enums.Stages.extraction.value
    )

    class Meta:
        namespace = "triller.avro"


@dataclass
class ExtractionAudit(Audit, serializer="avro_extraction_audit"):
    num_frames: int = 0
    strategy: types.Enum = types.Enum(
        enums.ExtractionStrategy.choices(),
        default=enums.ExtractionStrategy.memory.value,
    )


@dataclass
class CategoryTagAudit(Audit, serializer="avro_category_tag_audit"):
    category: str = None
    confidence: int = 0
    strategy: types.Enum = types.Enum(
        enums.PredictionStrategy.choices(),
        default=enums.PredictionStrategy.autotag.value,
    )
