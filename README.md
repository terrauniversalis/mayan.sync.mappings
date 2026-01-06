# mayan.sync.mappings

Herramienta para capturar puertos MIDI de entrada y salida con `mido`, y guardar perfiles como archivos `.json`.

## 🪶 Nomenclatura Mayan MIDI 2

El módulo `mayan_midi.py` define la nomenclatura **Mayan MIDI 2**:

- Los identificadores comienzan en `00` y combinan un número con una letra de ubicación:
  - `C` centro, `L` izquierda, `R` derecha, `A` arriba, `B` abajo, `W` completo y `B` BackOffice.
- Los protocolos mantienen su color de referencia: `midi` (azul), `ndi` (plateado), `asio` (gris).
- Las asignaciones son únicas; si se marca como uso dual se añade una `D` al final de la clave.
- Cada asignación puede llevar el nombre del controlador, el protocolo, el color asociado y una secuencia opcional de teclas para disparos híbridos (por ejemplo `win+shift+a`).

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
