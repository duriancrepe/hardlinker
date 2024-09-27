import unittest
import os
import shutil
import tempfile
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from raw_hardlinker import create_hardlinks

class TestRawHardlinker(unittest.TestCase):

    def setUp(self):
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.test_dir, 'source')
        self.dest_dir = os.path.join(self.test_dir, 'dest')
        os.mkdir(self.source_dir)
        os.mkdir(self.dest_dir)

    def tearDown(self):
        # Clean up temporary directories after testing
        shutil.rmtree(self.test_dir)

    def test_directory_to_directory(self):
        # Create test files in source directory
        with open(os.path.join(self.source_dir, 'file1.txt'), 'w') as f:
            f.write('Test content 1')
        os.mkdir(os.path.join(self.source_dir, 'subdir'))
        with open(os.path.join(self.source_dir, 'subdir', 'file2.txt'), 'w') as f:
            f.write('Test content 2')

        # Run raw_hardlinker
        create_hardlinks(self.source_dir, self.dest_dir)

        # Check if files are hardlinked correctly
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, 'file1.txt')))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, 'subdir', 'file2.txt')))
        self.assertTrue(os.path.samefile(
            os.path.join(self.source_dir, 'file1.txt'),
            os.path.join(self.dest_dir, 'file1.txt')
        ))
        self.assertTrue(os.path.samefile(
            os.path.join(self.source_dir, 'subdir', 'file2.txt'),
            os.path.join(self.dest_dir, 'subdir', 'file2.txt')
        ))

    def test_file_to_directory(self):
        # Create test file
        source_file = os.path.join(self.test_dir, 'test_file.txt')
        with open(source_file, 'w') as f:
            f.write('Test content')

        # Run raw_hardlinker
        create_hardlinks(source_file, self.dest_dir)

        # Check if file is hardlinked correctly
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, 'test_file.txt')))
        self.assertTrue(os.path.samefile(source_file, os.path.join(self.dest_dir, 'test_file.txt')))

    def test_file_to_file(self):
        # Create test file
        source_file = os.path.join(self.test_dir, 'source_file.txt')
        with open(source_file, 'w') as f:
            f.write('Test content')

        dest_file = os.path.join(self.dest_dir, 'dest_file.txt')

        # Run raw_hardlinker
        create_hardlinks(source_file, dest_file)

        # Check if file is hardlinked correctly
        self.assertTrue(os.path.exists(dest_file))
        self.assertTrue(os.path.samefile(source_file, dest_file))

    def test_nonexistent_source(self):
        with self.assertRaises(SystemExit):
            create_hardlinks('/nonexistent/path', self.dest_dir)

if __name__ == '__main__':
    unittest.main()

