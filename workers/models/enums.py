from enum import Enum


class BaseEnum(str, Enum):
    @classmethod
    def choices(cls):
        return [e.value for e in cls]


class ExtractionStrategy(BaseEnum):
    memory = "memory"
    legacy = "legacy"


class Stages(BaseEnum):
    extraction = "extraction"
    prediction = "prediction"


class PredictionStrategy(BaseEnum):
    autotag = "autotag"
    scaleai = "scaleai"
