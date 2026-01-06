import unittest

from mayan_midi import (
    LOCATION_CODES,
    MayanMidiControlBoard,
    MayanMidiMapping,
    PROTOCOL_COLORS,
)


class TestMayanMidi(unittest.TestCase):
    def test_mapping_key_and_color_are_built_from_spec(self):
        mapping = MayanMidiMapping(
            index=0,
            location="center",
            controller="MainDeck",
            protocol="midi",
        )

        self.assertEqual(mapping.key, "00C")
        self.assertEqual(mapping.protocol_color, PROTOCOL_COLORS["midi"])
        self.assertEqual(LOCATION_CODES["center"], "C")

    def test_dual_use_appends_dual_marker(self):
        mapping = MayanMidiMapping(
            index=1,
            location="left",
            controller="AuxDeck",
            protocol="ndi",
            is_dual_use=True,
            keystroke="win+shift+a",
        )

        self.assertTrue(mapping.key.endswith("D"))
        self.assertEqual(mapping.key, "01LD")
        self.assertEqual(mapping.protocol_color, "silver")
        self.assertEqual(mapping.keystroke, "win+shift+a")

    def test_control_board_rejects_duplicate_keys(self):
        board = MayanMidiControlBoard()
        primary = MayanMidiMapping(
            index=2,
            location="above",
            controller="Mixer",
            protocol="asio",
        )
        duplicate = MayanMidiMapping(
            index=2,
            location="above",
            controller="Recorder",
            protocol="asio",
        )

        board.add_mapping(primary)
        with self.assertRaises(ValueError):
            board.add_mapping(duplicate)

    def test_control_board_converter_payload_includes_mayan_note(self):
        board = MayanMidiControlBoard()
        mapping = MayanMidiMapping(
            index=3,
            location="backoffice",
            controller="Backline",
            protocol="midi",
            keystroke="ctrl+alt+g",
            note="MayanMIDI-BackOffice",
        )

        board.add_mapping(mapping)
        payload = board.to_converter_payload()

        self.assertEqual(
            payload,
            [
                {
                    "key": "03B",
                    "controller": "Backline",
                    "location": "backoffice",
                    "protocol": "midi",
                    "protocol_color": "blue",
                    "dual_use": False,
                    "keystroke": "ctrl+alt+g",
                    "note": "MayanMIDI-BackOffice",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
