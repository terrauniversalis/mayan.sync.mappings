# mayan.sync.mappings

Herramienta para capturar puertos MIDI de entrada y salida con `mido`, y guardar perfiles como archivos `.json`.

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
python -m unittest discover
```

## 📄 Documento de referencia

- Base conceptual de `::::fifa::2026::::`: `docs/fifa_2026_base_conceptual.md`
