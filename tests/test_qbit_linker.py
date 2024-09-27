
import unittest
from unittest.mock import patch, mock_open
import json
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from src.qbit_linker import load_config, get_destination_folder, main

class TestQbitLinker(unittest.TestCase):

    def setUp(self):
        self.mock_config = {
            'root_default_directory': '/root/default',
            'category_map': {
                'Movies': '/dest/movies',
                'TV_Shows': {
                    'Sitcoms': '/dest/tv/sitcoms',
                    'Drama': '/dest/tv/drama'
                }
            },
            'default_destination': '/dest/default'
        }
        self.mock_config_json = json.dumps(self.mock_config)

    def test_load_config(self):
        config = load_config(config_data=self.mock_config_json)
        self.assertEqual(config['root_default_directory'], '/root/default')
        self.assertEqual(config['category_map']['Movies'], '/dest/movies')
        self.assertEqual(config['category_map']['TV_Shows']['Sitcoms'], '/dest/tv/sitcoms')
        self.assertEqual(config['default_destination'], '/dest/default')

    def test_get_destination_folder(self):
        config = self.mock_config
        
        self.assertEqual(get_destination_folder(config, 'movies'), '/dest/movies')
        self.assertEqual(get_destination_folder(config, 'MOVIES'), '/dest/movies')
        self.assertEqual(get_destination_folder(config, 'tv_shows/sitcoms'), '/dest/tv/sitcoms')
        self.assertEqual(get_destination_folder(config, 'TV_Shows/Drama'), '/dest/tv/drama')
        self.assertEqual(get_destination_folder(config, 'books'), '/root/default/books')
        self.assertEqual(get_destination_folder(config, 'books/fiction'), '/root/default/books/fiction')
        self.assertEqual(get_destination_folder(config, 'TV_Shows/reality'), '/root/default/TV_Shows/reality')
        self.assertEqual(get_destination_folder(config, 'movies/action'), '/dest/movies/action')
        self.assertEqual(get_destination_folder(config, 'TV_Shows/Sitcoms/Friends'), '/dest/tv/sitcoms/Friends')


    @patch('src.qbit_linker.create_hardlinks')
    @patch('os.makedirs')
    def test_main(self, mock_makedirs, mock_create_hardlinks):
        # Test with a movie (lowercase)
        sys.argv = ['qbit_linker.py', '/downloads/great_movie.mkv', 'movies']
        main(config_data=self.mock_config_json)
        mock_create_hardlinks.assert_called_with('/downloads/great_movie.mkv', '/dest/movies/great_movie.mkv')
        
        # Test with a TV show sitcom (mixed case)
        sys.argv = ['qbit_linker.py', '/downloads/funny_series', 'Tv_Shows/SitComs']
        main(config_data=self.mock_config_json)
        mock_create_hardlinks.assert_called_with('/downloads/funny_series', '/dest/tv/sitcoms/funny_series')
        
        # Test with an unknown category
        sys.argv = ['qbit_linker.py', '/downloads/unknown_content', 'UnKnOwN']
        main(config_data=self.mock_config_json)
        mock_create_hardlinks.assert_called_with('/downloads/unknown_content', '/root/default/UnKnOwN/unknown_content')
        
        # Test with an unknown subcategory
        sys.argv = ['qbit_linker.py', '/downloads/new_show.mkv', 'TV_Shows/Reality']
        main(config_data=self.mock_config_json)
        mock_create_hardlinks.assert_called_with('/downloads/new_show.mkv', '/root/default/TV_Shows/Reality/new_show.mkv')

        # Verify that os.makedirs was called for each destination
        mock_makedirs.assert_called()

if __name__ == '__main__':
    unittest.main()

