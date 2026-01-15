import tempfile
import unittest
from pathlib import Path

from mayan_midi import (
    LOCATION_CODES,
    InventoryRegistry,
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


class TestMayanMidiInventory(unittest.TestCase):
    def test_inventory_registry_connects_known_device(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "inventory.csv"
            csv_path.write_text("device_name\nDeckA\n", encoding="utf-8")

            inventory = InventoryRegistry.from_csv(csv_path)
            inventory.connect_device("DeckA")

            self.assertIn("DeckA", inventory.connected)

    def test_inventory_registry_auto_registers_missing_device(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "inventory.csv"
            csv_path.write_text("device_name\nDeckB\n", encoding="utf-8")

            inventory = InventoryRegistry.from_csv(csv_path)
            inventory.connect_device("DeckC", auto_register=True)

            self.assertIn("DeckC", inventory.inventory)
            self.assertIn("DeckC", inventory.connected)

    def test_control_board_requires_connected_controller(self):
        inventory = InventoryRegistry(["MainDeck"])
        board = MayanMidiControlBoard(inventory=inventory)
        mapping = MayanMidiMapping(
            index=4,
            location="right",
            controller="MainDeck",
            protocol="midi",
        )

        with self.assertRaises(ValueError):
            board.add_mapping(mapping)

        inventory.connect_device("MainDeck")
        board.add_mapping(mapping)
        self.assertEqual(len(board.mappings), 1)


if __name__ == "__main__":
    unittest.main()
