# -*- coding: utf-8 -*-
import json
import os
import sys

try:
    from mido import get_input_names, get_output_names
except ModuleNotFoundError as e:
    print("\n[ERROR] No se encontró la librería 'mido'.")
    print("Instálala con: pip install mido\n")
    sys.exit(1)

def save_profile(profile_name, directory='profiles'):
    os.makedirs(directory, exist_ok=True)
    profile_path = os.path.join(directory, f'{profile_name}.json')
    profile_data = {
        'inputs': get_input_names(),
        'outputs': get_output_names()
    }
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile_data, f, indent=2)
    print(f"Perfil guardado en: {profile_path}")

def list_profiles(directory='profiles'):
    if not os.path.isdir(directory):
        print("No hay perfiles guardados.")
        return
    profiles = [f for f in os.listdir(directory) if f.endswith('.json')]
    if not profiles:
        print("No se encontraron perfiles.")
    else:
        print("Perfiles disponibles:")
        for p in profiles:
            print(f"- {p}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Gestor de perfiles MIDI.')
    parser.add_argument('--save', metavar='NOMBRE', help='Guardar un perfil con el nombre dado')
    parser.add_argument('--list', action='store_true', help='Listar perfiles guardados')
    args = parser.parse_args()

    if args.save:
        save_profile(args.save)
    elif args.list:
        list_profiles()
    else:
        parser.print_help()
