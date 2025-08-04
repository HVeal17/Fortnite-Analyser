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
        self.event_texts = []

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

                # Decode based on type
                if chunk_type == 3:  # ReplayData
                    chunk_info['summary'] = self._decode_replay_data(data)

                elif chunk_type == 2:  # Event
                    decoded = self._decode_event_chunk(data)
                    chunk_info['event'] = decoded
                    if 'raw_text' in decoded:
                        self.event_texts.append(decoded['raw_text'])

                self.chunks.append(chunk_info)
            except struct.error:
                break

    def _decode_replay_data(self, data: bytes) -> Dict:
        return {
            "byte_length": len(data),
            "example_bytes": list(data[:16])
        }

    def _decode_event_chunk(self, data: bytes) -> Dict:
        try:
            text = data.decode('utf-8', errors='ignore')
            return {
                'text_preview': text[:100].replace('\n', ' '),
                'raw_text': text
            }
        except Exception:
            return {'error': 'Could not decode event data'}

    # -----------------------------
    # Gameplay-specific extraction
    # -----------------------------

    def parse_kills(self) -> int:
        return sum(1 for text in self.event_texts if "Elimination" in text or "Kill" in text)

    def parse_zone_entries(self) -> int:
        return sum(1 for text in self.event_texts if "SafeZone" in text)

    def parse_damage_dealt(self) -> int:
        total = 0
        for text in self.event_texts:
            if "DamageDealt" in text:
                try:
                    # Naively extract digits after DamageDealt:
                    start = text.find("DamageDealt")
                    number = ''.join(c for c in text[start:] if c.isdigit())
                    if number:
                        total += int(number)
                except:
                    pass
        return total

    def parse_jump_count(self) -> int:
        return sum(1 for text in self.event_texts if "Jump" in text)

    def parse_structures_built(self) -> int:
        return sum(1 for text in self.event_texts if "Build" in text or "Structure" in text)

    def to_dict(self) -> Dict:
        return {
            'metadata': self.metadata,
            'analysis': {
                'combat': {
                    'eliminations': self.parse_kills(),
                    'damage_given': self.parse_damage_dealt(),
                    'accuracy': 0.0,  # Placeholder
                    'headshots': 0,
                    'damage_taken': 0
                },
                'movement': {
                    'distance_traveled': 0.0,
                    'sprint_time': 0.0,
                    'walk_time': 0.0,
                    'jump_count': self.parse_jump_count(),
                    'zipline_used': 0
                },
                'positioning': {
                    'time_in_cover': 0,
                    'time_in_open': 0,
                    'time_on_high_ground': 0,
                    'exposed_time': 0,
                    'score': 0
                },
                'rotation': {
                    'rotations': [],
                    'avg_rotation_distance': 0.0,
                    'avg_rotation_speed': 0.0,
                    'score': 0
                },
                'zone': {
                    'time_in_zone': 0,
                    'time_in_storm': 0,
                    'zone_entries': self.parse_zone_entries(),
                    'storm_damage_taken': 0,
                    'storm_exposure_ratio': 0.0
                },
                'loadout': {},
                'enemy_proximity': {
                    'encounters': 0,
                    'avg_distance': 0.0,
                    'close_encounters': 0
                },
                'building': {
                    'structures_built': self.parse_structures_built(),
                    'materials_used': {
                        'wood': 0,
                        'brick': 0,
                        'metal': 0
                    },
                    'defensive_builds': 0,
                    'aggressive_builds': 0,
                    'edits_made': 0,
                    'build_fights': 0
                },
                'summary': {
                    'kills': self.parse_kills(),
                    'accuracy': 0.0,
                    'rotation_score': 0,
                    'positioning_score': 0,
                    'zone_safety': 0
                }
            },
            'events': self.event_texts
        }

    def save_json(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
