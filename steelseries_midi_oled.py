# -*- coding: utf-8 -*-
"""Forward MIDI note events to SteelSeries GameSense OLED devices.

This script listens to a MIDI input device and pushes note messages to the
SteelSeries Engine GameSense local HTTP API so they can be shown on OLED
screens (e.g., Apex Pro keyboard).
"""

from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import requests

try:
    import mido
except ModuleNotFoundError as exc:
    raise SystemExit(
        "[ERROR] Missing dependency 'mido'. Install with: pip install -r requirements.txt"
    ) from exc

DEFAULT_GAME = "MIDI2OLED"
DEFAULT_EVENT = "NOTE"
DEFAULT_ICON = 1
DEFAULT_LINE = 0
DEFAULT_PREFIX = "MIDI"

NOTE_NAMES = [
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
]


@dataclass
class GameSenseConfig:
    address: str


class GameSenseClient:
    def __init__(self, config: GameSenseConfig, timeout: float = 1.5) -> None:
        self.base_url = f"http://{config.address}"
        self.timeout = timeout

    def _post(self, path: str, payload: dict) -> None:
        response = requests.post(
            f"{self.base_url}/{path.lstrip('/')}",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

    def register_game(self, game: str, display_name: str, developer: str) -> None:
        self._post(
            "game_metadata",
            {
                "game": game,
                "game_display_name": display_name,
                "developer": developer,
            },
        )

    def bind_oled_event(self, game: str, event: str, line: int, icon_id: int) -> None:
        self._post(
            "bind_game_event",
            {
                "game": game,
                "event": event,
                "handlers": [
                    {
                        "device-type": "screened",
                        "zone": "one",
                        "mode": "screen",
                        "datas": [
                            {
                                "has-text": True,
                                "context-frame-key": "note",
                                "bold": True,
                                "line": line,
                                "icon-id": icon_id,
                            }
                        ],
                    }
                ],
            },
        )

    def send_note_text(self, game: str, event: str, text: str) -> None:
        payload = {
            "game": game,
            "event": event,
            "data": {
                "value": 0,
                "frame": {"note": text},
            },
        }
        self._post("game_event", payload)


def load_gamesense_config(core_props_path: Optional[str] = None) -> GameSenseConfig:
    """Load SteelSeries Engine coreProps.json and return API address."""
    if core_props_path:
        candidate_paths = [Path(core_props_path)]
    else:
        candidate_paths = [
            Path(os.getenv("PROGRAMDATA", "C:/ProgramData"))
            / "SteelSeries"
            / "SteelSeries Engine 3"
            / "coreProps.json",
            Path(os.getenv("PROGRAMDATA", "C:/ProgramData"))
            / "SteelSeries"
            / "GG"
            / "coreProps.json",
            Path.home() / ".steelseries" / "coreProps.json",
        ]

    for path in candidate_paths:
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        address = data.get("address")
        if address:
            return GameSenseConfig(address=address)

    attempted = ", ".join(str(p) for p in candidate_paths)
    raise FileNotFoundError(
        f"Could not find GameSense coreProps.json with a valid address. Tried: {attempted}"
    )


def midi_note_to_text(note: int) -> str:
    if note < 0 or note > 127:
        return f"NOTE {note}"
    octave = (note // 12) - 1
    name = NOTE_NAMES[note % 12]
    return f"{name}{octave} ({note})"


def resolve_input_ports(explicit_port: Optional[str], auto_all: bool, prefer_bome: bool) -> list[str]:
    inputs = mido.get_input_names()
    bome_inputs = [name for name in inputs if "bome" in name.lower()]
    if explicit_port:
        if explicit_port not in inputs:
            raise ValueError(
                f"MIDI port '{explicit_port}' was not found. Available: {', '.join(inputs) or '(none)'}"
            )
        return [explicit_port]
    if prefer_bome and bome_inputs:
        return bome_inputs
    if auto_all:
        if not inputs:
            raise ValueError("No MIDI input ports were found.")
        return inputs
    raise ValueError(
        "No Bome MIDI Network port found. Specify --midi-port or use --all-midi to listen on every device."
    )


def run(
    midi_port: Optional[str],
    all_midi: bool,
    prefer_bome: bool,
    game: str,
    event: str,
    display_name: str,
    developer: str,
    line: int,
    icon_id: int,
    prefix: str,
    core_props_path: Optional[str],
) -> None:
    config = load_gamesense_config(core_props_path)
    client = GameSenseClient(config)

    client.register_game(game, display_name=display_name, developer=developer)
    client.bind_oled_event(game, event, line=line, icon_id=icon_id)

    ports = resolve_input_ports(midi_port, auto_all=all_midi, prefer_bome=prefer_bome)
    print(f"[INFO] Listening on MIDI input(s): {', '.join(ports)}")
    print(f"[INFO] Sending note text to GameSense game='{game}' event='{event}'")
    open_ports = [mido.open_input(name) for name in ports]
    try:
        while True:
            for inport in open_ports:
                for message in inport.iter_pending():
                    if message.type != "note_on" or getattr(message, "velocity", 0) <= 0:
                        continue
                    note_text = midi_note_to_text(message.note)
                    full_text = f"{prefix}: {note_text}" if prefix else note_text
                    print(f"[MIDI] {inport.name} -> {full_text}")
                    try:
                        client.send_note_text(game, event, full_text)
                    except requests.RequestException as exc:
                        print(f"[WARN] Failed to push event to SteelSeries Engine: {exc}")
            time.sleep(0.01)
    finally:
        for inport in open_ports:
            inport.close()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Listen to a MIDI input (e.g., Maschine MK2 / Hercules DJ Controller) "
            "and display note names on SteelSeries OLED via GameSense."
        )
    )
    parser.add_argument("--list-midi", action="store_true", help="List available MIDI input ports and exit")
    parser.add_argument("--midi-port", help="MIDI input port name to open")
    parser.add_argument("--all-midi", action="store_true", help="Listen on all available MIDI input ports")
    parser.add_argument(
        "--bome-network",
        action="store_true",
        help="Prefer Bome MIDI Network input ports when --midi-port is not provided",
    )
    parser.add_argument("--game", default=DEFAULT_GAME, help=f"GameSense game id (default: {DEFAULT_GAME})")
    parser.add_argument("--event", default=DEFAULT_EVENT, help=f"GameSense event id (default: {DEFAULT_EVENT})")
    parser.add_argument("--display-name", default="MIDI OLED Bridge", help="GameSense display name")
    parser.add_argument("--developer", default="Local User", help="GameSense developer string")
    parser.add_argument("--line", type=int, default=DEFAULT_LINE, help="OLED line index for text rendering")
    parser.add_argument("--icon-id", type=int, default=DEFAULT_ICON, help="GameSense icon id")
    parser.add_argument("--prefix", default=DEFAULT_PREFIX, help="Text prefix before note name")
    parser.add_argument("--core-props", help="Optional explicit path to coreProps.json")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.list_midi:
        for name in mido.get_input_names():
            print(name)
        return 0

    run(
        midi_port=args.midi_port,
        all_midi=args.all_midi,
        prefer_bome=args.bome_network or (not args.midi_port and not args.all_midi),
        game=args.game,
        event=args.event,
        display_name=args.display_name,
        developer=args.developer,
        line=args.line,
        icon_id=args.icon_id,
        prefix=args.prefix,
        core_props_path=args.core_props,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
