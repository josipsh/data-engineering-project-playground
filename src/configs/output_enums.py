from enum import Enum


class OutputFormat(Enum):
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    AVRO = "avro"
    JSON_WITH_BINARY_PAYLOAD = "json-with-binary-payload"
    XML_WITH_BINARY_PAYLOAD = "xml-with-binary-payload"
    CSV_WITH_BINARY_PAYLOAD = "csv-with-binary-payload"
    AVRO_WITH_BINARY_PAYLOAD = "avro-with-binary-payload"

class OutputType(Enum):
    KAFKA_ONLY = "kafka-only"
    RABBITMQ_ONLY = "rabbitmq-only"
    S3_ONLY = "s3-only"
    S3_WITH_KAFKA = "s3-with-kafka"
    S3_WITH_RABBITMQ = "s3-with-rabbitmq"
