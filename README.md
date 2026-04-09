# mayan.sync.mappings

Herramienta para capturar puertos MIDI de entrada y salida con `mido`, y guardar perfiles como archivos `.json`.

## 🪶 Nomenclatura Mayan MIDI 2

El módulo `mayan_midi.py` define la nomenclatura **Mayan MIDI 2**:

- Los identificadores comienzan en `00` y combinan un número con una letra de ubicación:
  - `C` centro, `L` izquierda, `R` derecha, `A` arriba, `B` abajo, `W` completo y `B` BackOffice.
- Los protocolos mantienen su color de referencia: `midi` (azul), `ndi` (plateado), `asio` (gris).
- Las asignaciones son únicas; si se marca como uso dual se añade una `D` al final de la clave.
- Cada asignación puede llevar el nombre del controlador, el protocolo, el color asociado y una secuencia opcional de teclas para disparos híbridos (por ejemplo `win+shift+a`).

### Inventario interactivo y en vivo (SharePoint directo)

El tablero Mayan MIDI 2 valida que el controlador esté en inventario antes de mapearlo
consultando la lista de SharePoint **en vivo**. Para el inventario de
`https://terrauniversalis.sharepoint.com/Lists/terrauniversalis_audio_equipment`, el flujo
recomendado es usar Microsoft Graph con un token de acceso y los IDs del sitio y la lista.

```python
from mayan_midi import (
    InventoryRegistry,
    MayanMidiControlBoard,
    MayanMidiMapping,
    SharePointInventoryClient,
)

client = SharePointInventoryClient(
    access_token="TOKEN_GRAPH",
    site_id="SITE_ID",
    list_id="LIST_ID",
    field_name="device_name",
)

inventory = InventoryRegistry.from_sharepoint(client)
inventory.connect_device("MainDeck", auto_register=True)

board = MayanMidiControlBoard(inventory=inventory)
board.add_mapping(
    MayanMidiMapping(
        index=0,
        location="center",
        controller="MainDeck",
        protocol="midi",
    )
)
```

Si necesitas encontrar rápidamente los IDs del sitio/lista o preparar columnas en SharePoint,
usa el script de descubrimiento en `scripts/sharepoint_inventory_discovery.ps1`. Ese script usa
Microsoft Graph para enumerar sitios/listas y crear campos en la lista de mappings cuando faltan.

Ejemplo rápido:

```python
from mayan_midi import MayanMidiControlBoard, MayanMidiMapping

board = MayanMidiControlBoard()
board.add_mapping(
    MayanMidiMapping(
        index=0,
        location="center",
        controller="MainDeck",
        protocol="midi",
        keystroke="win+shift+a",
    )
)
print(board.to_converter_payload())
# [{'key': '00C', 'controller': 'MainDeck', 'location': 'center', 'protocol': 'midi',
#   'protocol_color': 'blue', 'dual_use': False, 'keystroke': 'win+shift+a',
#   'note': 'MayanMIDI-00C'}]
```

## 🚀 Requisitos

- Python 3.7+
- Paquete [`mido`](https://pypi.org/project/mido/)

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## ⚙️ Uso

```bash
# Guardar un perfil actual
python midi_profile.py --save nombre_perfil

# Listar perfiles guardados
python midi_profile.py --list
```

Los perfiles se guardan en la carpeta `profiles/`.

## 🧪 Pruebas

Ejecuta las pruebas con:

```bash
python -m unittest discover -s tests
```

## 📄 Documento de referencia

- Guía conceptual y operativa de `::::fifa::2026::::`: `docs/fifa_2026_base_conceptual.md`
- Blueprint técnico en JSON: `schemas/fifa_2026.blueprint.json`
