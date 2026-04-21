# mayan.sync.mappings

Herramienta para capturar puertos MIDI de entrada y salida con `mido`, guardar perfiles como archivos `.json`, y enviar notas MIDI al OLED de teclados SteelSeries (Apex Pro) usando GameSense.

## 🚀 Requisitos

- Python 3.8+
- SteelSeries GG / Engine ejecutándose (con GameSense activo)
- Dispositivo MIDI de entrada (por ejemplo Maschine MK2 o Hercules DJ Controller)

Instala las dependencias con:

```bash
pip install -r requirements.txt
```

## ⚙️ Uso

### 1) Gestión de perfiles MIDI

```bash
# Guardar un perfil actual
python midi_profile.py --save nombre_perfil

# Listar perfiles guardados
python midi_profile.py --list
```

Los perfiles se guardan en la carpeta `profiles/`.

### 2) Bridge MIDI -> OLED (SteelSeries Apex Pro / GameSense plugin flow)

```bash
# Listar puertos MIDI disponibles
python steelseries_midi_oled.py --list-midi

# Escuchar un puerto y mostrar notas en OLED
python steelseries_midi_oled.py --midi-port "Maschine Controller MK2"

# Escuchar todos los dispositivos MIDI conectados
python steelseries_midi_oled.py --all-midi

# Modo fácil: usar puertos de Bome MIDI Network automáticamente
python steelseries_midi_oled.py --bome-network
```

Opciones útiles:

- `--prefix "DJ"` cambia el prefijo del texto mostrado.
- `--line 0` selecciona la línea OLED usada.
- `--core-props "C:/ProgramData/SteelSeries/SteelSeries Engine 3/coreProps.json"` fuerza ruta de configuración GameSense.
- `--all-midi` permite escuchar Maschine MK2 + Hercules al mismo tiempo.
- `--bome-network` prioriza puertos `Bome MIDI Network` (recomendado para ruteo sencillo).

> Si no pasas `--midi-port` ni `--all-midi`, el script intentará usar Bome MIDI Network automáticamente.

## 🧪 Pruebas

Ejecuta las pruebas con:

```bash
pytest -q
```

## 📄 Documento de referencia

- Guía conceptual y operativa de `::::fifa::2026::::`: `docs/fifa_2026_base_conceptual.md`
- Blueprint técnico en JSON: `schemas/fifa_2026.blueprint.json`
