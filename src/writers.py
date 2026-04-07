from __future__ import annotations

import base64
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree

from src.generator_core import GeneratedRecord


_AVRO_SCHEMA = {
    "type": "record",
    "name": "device_payload",
    "fields": [
        {"name": "received_at", "type": "string"},
        {"name": "payload", "type": "bytes"},
        {"name": "format_version", "type": "int"},
        {"name": "fw_version", "type": "int"},
        {"name": "fleet_id", "type": "int"},
        {"name": "device_id", "type": "int"},
        {"name": "sequence_id", "type": "long"},
    ],
}


def write_records(
    records: Iterable[GeneratedRecord],
    output_format: str,
    output_path: str,
) -> Path:
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    extension = _extension_for_format(output_format)
    output_file = output_dir / f"device_payload_{timestamp}.{extension}"

    if output_format == "json":
        _write_ndjson(output_file, records)
    elif output_format == "csv":
        _write_csv(output_file, records)
    elif output_format == "xml":
        _write_xml(output_file, records)
    elif output_format == "avro":
        _write_avro(output_file, records)
    else:
        raise ValueError("output_format must be one of json,csv,xml,avro")

    return output_file


def _extension_for_format(output_format: str) -> str:
    mapping = {"json": "ndjson", "csv": "csv", "xml": "xml", "avro": "avro"}
    if output_format not in mapping:
        raise ValueError("output_format must be one of json,csv,xml,avro")
    return mapping[output_format]


def _record_to_text_dict(record: GeneratedRecord) -> dict[str, object]:
    payload_b64 = base64.b64encode(record.payload).decode("ascii")
    return {
        "received_at": record.received_at,
        "payload": payload_b64,
        "format_version": record.format_version,
        "fw_version": record.fw_version,
        "fleet_id": record.fleet_id,
        "device_id": record.device_id,
        "sequence_id": record.sequence_id,
    }


def _write_ndjson(output_file: Path, records: Iterable[GeneratedRecord]) -> None:
    with output_file.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(
                json.dumps(_record_to_text_dict(record), separators=(",", ":"))
            )
            handle.write("\n")


def _write_csv(output_file: Path, records: Iterable[GeneratedRecord]) -> None:
    fieldnames = [
        "received_at",
        "payload",
        "format_version",
        "fw_version",
        "fleet_id",
        "device_id",
        "sequence_id",
    ]
    with output_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(_record_to_text_dict(record))


def _write_xml(output_file: Path, records: Iterable[GeneratedRecord]) -> None:
    root = ElementTree.Element("records")
    for record in records:
        record_el = ElementTree.SubElement(root, "record")
        record_dict = _record_to_text_dict(record)
        for key, value in record_dict.items():
            child = ElementTree.SubElement(record_el, key)
            child.text = str(value)
    tree = ElementTree.ElementTree(root)
    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def _write_avro(output_file: Path, records: Iterable[GeneratedRecord]) -> None:
    try:
        avro_writer = __import__("fastavro").writer
    except ImportError as exc:
        raise RuntimeError("fastavro is required for avro output") from exc

    def avro_records() -> Iterable[dict[str, object]]:
        for record in records:
            yield {
                "received_at": record.received_at,
                "payload": record.payload,
                "format_version": record.format_version,
                "fw_version": record.fw_version,
                "fleet_id": record.fleet_id,
                "device_id": record.device_id,
                "sequence_id": record.sequence_id,
            }

    with output_file.open("wb") as handle:
        avro_writer(handle, _AVRO_SCHEMA, avro_records())
