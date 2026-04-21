import json
from pathlib import Path
from unittest import mock

from steelseries_midi_oled import (
    GameSenseClient,
    GameSenseConfig,
    load_gamesense_config,
    midi_note_to_text,
    resolve_input_ports,
)


def test_midi_note_to_text_known_note():
    assert midi_note_to_text(60) == "C4 (60)"


def test_midi_note_to_text_invalid_note_fallback():
    assert midi_note_to_text(130) == "NOTE 130"


def test_load_gamesense_config_from_explicit_path(tmp_path: Path):
    core_props = tmp_path / "coreProps.json"
    core_props.write_text(json.dumps({"address": "127.0.0.1:12345"}), encoding="utf-8")

    cfg = load_gamesense_config(str(core_props))

    assert cfg.address == "127.0.0.1:12345"


def test_send_note_text_posts_expected_payload():
    client = GameSenseClient(GameSenseConfig(address="127.0.0.1:12345"))

    with mock.patch("steelseries_midi_oled.requests.post") as post:
        post.return_value.raise_for_status.return_value = None

        client.send_note_text("MIDI2OLED", "NOTE", "MIDI: C4 (60)")

        assert post.called
        call = post.call_args
        assert call.kwargs["json"]["game"] == "MIDI2OLED"
        assert call.kwargs["json"]["event"] == "NOTE"
        assert call.kwargs["json"]["data"]["frame"]["note"] == "MIDI: C4 (60)"


def test_resolve_input_ports_explicit():
    with mock.patch("steelseries_midi_oled.mido.get_input_names", return_value=["A", "B"]):
        assert resolve_input_ports("B", auto_all=False, prefer_bome=False) == ["B"]


def test_resolve_input_ports_prefers_bome():
    with mock.patch(
        "steelseries_midi_oled.mido.get_input_names",
        return_value=["Controller A", "Bome Network 1", "Bome Network 2"],
    ):
        assert resolve_input_ports(None, auto_all=False, prefer_bome=True) == [
            "Bome Network 1",
            "Bome Network 2",
        ]
