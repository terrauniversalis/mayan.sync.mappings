# -*- coding: utf-8 -*-
"""Herramientas para la nomenclatura Mayan MIDI 2 y su tablero de control."""
from dataclasses import dataclass
from typing import Dict, List, Optional

PROTOCOL_COLORS: Dict[str, str] = {
    "midi": "blue",
    "ndi": "silver",
    "asio": "grey",
}

LOCATION_CODES: Dict[str, str] = {
    "center": "C",
    "left": "L",
    "right": "R",
    "above": "A",
    "below": "B",
    "whole": "W",
    # Se mantiene la letra B para BackOffice tal como indica la nomenclatura original.
    "backoffice": "B",
}


@dataclass
class MayanMidiMapping:
    """Modelo para una asignación de la nomenclatura Mayan MIDI 2."""

    index: int
    location: str
    controller: str
    protocol: str
    is_dual_use: bool = False
    keystroke: Optional[str] = None
    note: Optional[str] = None

    def __post_init__(self) -> None:
        if self.index < 0:
            raise ValueError("El índice debe iniciar en 00 y ser un número positivo.")
        if self.location not in LOCATION_CODES:
            raise ValueError(f"Ubicación no reconocida: {self.location}")
        if self.protocol not in PROTOCOL_COLORS:
            raise ValueError(f"Protocolo no reconocido: {self.protocol}")

    @property
    def key(self) -> str:
        base_key = f"{self.index:02d}{LOCATION_CODES[self.location]}"
        if self.is_dual_use:
            return f"{base_key}D"
        return base_key

    @property
    def protocol_color(self) -> str:
        return PROTOCOL_COLORS[self.protocol]

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "key": self.key,
            "controller": self.controller,
            "location": self.location,
            "protocol": self.protocol,
            "protocol_color": self.protocol_color,
            "dual_use": self.is_dual_use,
            "keystroke": self.keystroke,
            "note": self.note or f"MayanMIDI-{self.key}",
        }


class MayanMidiControlBoard:
    """Tablero mapeable para gestionar asignaciones Mayan MIDI."""

    def __init__(self) -> None:
        self._mappings: List[MayanMidiMapping] = []

    def add_mapping(self, mapping: MayanMidiMapping) -> None:
        existing_keys = {item.key for item in self._mappings}
        if mapping.key in existing_keys:
            raise ValueError(f"La clave {mapping.key} ya está asignada en el tablero.")
        self._mappings.append(mapping)

    @property
    def mappings(self) -> List[MayanMidiMapping]:
        return list(self._mappings)

    def to_converter_payload(self) -> List[Dict[str, Optional[str]]]:
        """Devuelve la carga para el conversor/recorder de Mayan MIDI."""
        return [mapping.to_dict() for mapping in self._mappings]
