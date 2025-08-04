# File: backend-python/utils/fortnite_replay_parser/__init__.py

import os
import struct
import json
from typing import Dict, List, Optional

CHUNK_TYPE_MAP = {
    1: "Checkpoint",
    2: "Event",
    3: "ReplayData"
}

class ReplayParser:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.metadata = {}
        self.chunks = []

    def parse(self):
        with open(self.filepath, 'rb') as f:
            self._parse_header(f)
            self._parse_chunks(f)

    def _parse_header(self, f):
        f.seek(0)
        header_data = f.read(32)
        if len(header_data) < 32:
            raise ValueError("Incomplete replay header")

        magic, version_major, version_minor = struct.unpack('<8sII', header_data[:16])
        self.metadata['magic'] = magic.decode('utf-8', errors='ignore').strip('\x00')
        self.metadata['version_major'] = version_major
        self.metadata['version_minor'] = version_minor

    def _parse_chunks(self, f):
        f.seek(32)
        while True:
            chunk_header = f.read(12)
            if len(chunk_header) < 12:
                break
            try:
                chunk_type, size, time = struct.unpack('<III', chunk_header)
                data = f.read(size)
                chunk_info = {
                    'type': chunk_type,
                    'type_name': CHUNK_TYPE_MAP.get(chunk_type, f"Unknown_{chunk_type}"),
                    'size': size,
                    'time': time,
                }

                # Optional decoding for ReplayData
                if chunk_type == 3:  # ReplayData
                    chunk_info['summary'] = self._decode_replay_data(data)

                elif chunk_type == 2:  # Event
                    chunk_info['event'] = self._decode_event_chunk(data)

                self.chunks.append(chunk_info)
            except struct.error:
                break

    def _decode_replay_data(self, data: bytes) -> Dict:
        # Placeholder - binary inspection, look for string blocks
        summary = {
            "byte_length": len(data),
            "example_bytes": list(data[:16])  # Show first 16 bytes
        }
        return summary

    def _decode_event_chunk(self, data: bytes) -> Dict:
        try:
            text = data.decode('utf-8', errors='ignore')
            return {
                'text_preview': text[:100].replace('\n', ' '),
                'raw_bytes': list(data[:16])
            }
        except Exception:
            return {'error': 'Could not decode event data'}

    def to_dict(self) -> Dict:
        return {
            'metadata': self.metadata,
            'chunks': self.chunks
        }

    def save_json(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
