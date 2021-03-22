import settings
from models import audit, video
from schema_registry.client import SchemaRegistryClient
from schema_registry.serializers import FaustSerializer

# Initialize Schema Registry Client
client = SchemaRegistryClient(url=settings.SCHEMA_REGISTRY_URL)

# example of how to use it with dataclasses-avroschema
avro_video_serializer = FaustSerializer(
    client, "video", video.VideoModel.avro_schema_to_python()
)
avro_extraction_audit_serializer = FaustSerializer(
    client, "extraction_audit", audit.ExtractionAudit.avro_schema_to_python()
)
avro_category_tag_audit_serializer = FaustSerializer(
    client, "category_tag_audit", audit.CategoryTagAudit.avro_schema_to_python()
)


def avro_video_codec():
    return avro_video_serializer


def avro_audit_codec():
    return avro_video_serializer


def avro_extraction_audit_codec():
    return avro_extraction_audit_serializer


def avro_category_tag_audit_codec():
    return avro_category_tag_audit_serializer
