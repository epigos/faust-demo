import settings
from faust.serializers import codecs
from models import audit, video
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import FaustSerializer

# Initialize Schema Registry Client
client = SchemaRegistryClient(url=settings.SCHEMA_REGISTRY_URL)

# example of how to use it with dataclasses-avroschema
avro_video_serializer = FaustSerializer(
    client, "avro_video", video.VideoModel.avro_schema()  # noqa
)
avro_extraction_audit_serializer = FaustSerializer(
    client, "avro_extraction_audit", audit.ExtractionAudit.avro_schema()  # noqa
)
avro_category_tag_audit_serializer = FaustSerializer(
    client, "avro_category_tag_audit", audit.CategoryTagAudit.avro_schema()  # noqa
)


def avro_video_codec():
    return avro_video_serializer


def avro_extraction_audit_codec():
    return avro_extraction_audit_serializer


def avro_category_tag_audit_codec():
    return avro_category_tag_audit_serializer


codecs.register("avro_video", avro_video_codec())
codecs.register("avro_extraction_audit", avro_extraction_audit_codec())
codecs.register("avro_category_tag_audit", avro_category_tag_audit_codec())
