import json
import os
import shutil
from unittest import mock
from midi_profile import save_profile

def test_save_profile_creates_correct_json():
    test_dir = 'test_profiles'
    test_file = os.path.join(test_dir, 'test_profile.json')
    mock_inputs = ['Input A', 'Input B']
    mock_outputs = ['Output X']

    with mock.patch('midi_profile.get_input_names', return_value=mock_inputs), \
         mock.patch('midi_profile.get_output_names', return_value=mock_outputs):
        save_profile('test_profile', directory=test_dir)

        with open(test_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data['inputs'] == mock_inputs
        assert data['outputs'] == mock_outputs

    shutil.rmtree(test_dir)
