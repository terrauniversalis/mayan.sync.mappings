# -*- coding: utf-8 -*-
"""Herramientas para la nomenclatura Mayan MIDI 2 y su tablero de control."""
from dataclasses import dataclass
import csv
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

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


class InventoryRegistry:
    """Registro en vivo de inventario para dispositivos Mayan MIDI."""

    DEFAULT_FIELDS = (
        "device_name",
        "name",
        "device",
        "equipo",
        "equipment",
        "asset",
    )

    def __init__(
        self,
        inventory_items: Iterable[str],
        csv_path: Optional[Path] = None,
        field_name: Optional[str] = None,
    ) -> None:
        self._inventory: Set[str] = {item.strip() for item in inventory_items if item.strip()}
        self._connected: Set[str] = set()
        self._csv_path = csv_path
        self._field_name = field_name

    @classmethod
    def from_csv(
        cls,
        csv_path: Path,
        field_name: Optional[str] = None,
    ) -> "InventoryRegistry":
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError("El CSV de inventario no contiene encabezados.")
            selected_field = field_name or cls._pick_field(reader.fieldnames)
            if selected_field is None:
                raise ValueError(
                    "No se encontró una columna reconocible para el nombre del dispositivo."
                )
            items = [row.get(selected_field, "") for row in reader]
        return cls(items, csv_path=csv_path, field_name=selected_field)

    @classmethod
    def _pick_field(cls, fieldnames: Iterable[str]) -> Optional[str]:
        normalized = {name.lower(): name for name in fieldnames}
        for option in cls.DEFAULT_FIELDS:
            if option in normalized:
                return normalized[option]
        return None

    @property
    def inventory(self) -> Set[str]:
        return set(self._inventory)

    @property
    def connected(self) -> Set[str]:
        return set(self._connected)

    def verify_device(self, device_name: str) -> bool:
        return device_name in self._inventory

    def register_device(self, device_name: str, persist: bool = False) -> None:
        if not device_name.strip():
            raise ValueError("El nombre del dispositivo no puede estar vacío.")
        if device_name not in self._inventory:
            self._inventory.add(device_name)
            if persist and self._csv_path and self._field_name:
                self._append_to_csv(device_name)

    def connect_device(self, device_name: str, auto_register: bool = False) -> None:
        if device_name not in self._inventory:
            if auto_register:
                self.register_device(device_name, persist=True)
            else:
                raise ValueError(
                    f"El dispositivo '{device_name}' no está en inventario."
                )
        self._connected.add(device_name)

    def disconnect_device(self, device_name: str) -> None:
        self._connected.discard(device_name)

    def _append_to_csv(self, device_name: str) -> None:
        if not self._csv_path or not self._field_name:
            return
        with self._csv_path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[self._field_name])
            writer.writerow({self._field_name: device_name})


class MayanMidiControlBoard:
    """Tablero mapeable para gestionar asignaciones Mayan MIDI."""

    def __init__(self, inventory: Optional[InventoryRegistry] = None) -> None:
        self._mappings: List[MayanMidiMapping] = []
        self._inventory = inventory

    def add_mapping(self, mapping: MayanMidiMapping) -> None:
        if self._inventory and mapping.controller not in self._inventory.connected:
            raise ValueError(
                "El controlador debe estar conectado y verificado en inventario."
            )
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
