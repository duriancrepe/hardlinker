import unittest
import os
import tempfile
import shutil
import json
import sys
from pathlib import Path

# Add the src directory to sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(0, src_path)

# Now import the necessary functions from src
from hardlink_manager import build_inode_map, create_snapshot, restore_hardlinks

class TestHardlinkManager(unittest.TestCase):

    def setUp(self):
        """Set up the test environment with fixed temporary directories and files."""
        # Fixed names for the temporary directories and files
        self.source_dir = '/tmp/test_source_dir'
        self.target_dir = '/tmp/test_target_dir'
        self.inode_map_file = '/tmp/test_inode_map.json'  # Add the inode map file
        self.snapshot_file = '/tmp/test_snapshot.json'    # Add the snapshot file
        self.non_restored_file = '/tmp/non_restored_hardlinks.json'  # Non-restored file

        # Clean up any existing directories and files before creating new ones
        if os.path.exists(self.source_dir):
            shutil.rmtree(self.source_dir)
        if os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir)
        
        # Clean up any existing temporary files
        for temp_file in [self.inode_map_file, self.snapshot_file, self.non_restored_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # Create the source and target directories
        os.makedirs(self.source_dir)
        os.makedirs(self.target_dir)
        
        # Create sample files in the source directory
        self.source_files = []
        for i in range(5):
            file_path = os.path.join(self.source_dir, f"file{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Content of file {i}")
            self.source_files.append(file_path)
        
        # Create multiple hard links for each source file in different subfolders of the target directory
        self.target_links = []
        for i, source_file in enumerate(self.source_files):
            # Create multiple subdirectories to store the hard links
            subfolder1 = os.path.join(self.target_dir, f"subfolder1")
            subfolder2 = os.path.join(self.target_dir, f"subfolder2")
            os.makedirs(subfolder1, exist_ok=True)
            os.makedirs(subfolder2, exist_ok=True)

            # Create the hard links in these subfolders
            target_link1 = os.path.join(subfolder1, f"link_to_file{i}.txt")
            target_link2 = os.path.join(subfolder2, f"link_to_file{i}.txt")
            os.link(source_file, target_link1)
            os.link(source_file, target_link2)
            self.target_links.extend([target_link1, target_link2])

    def tearDown(self):
        """Clean up temporary directories and files."""
        shutil.rmtree(self.source_dir)
        shutil.rmtree(self.target_dir)
        
        # Clean up any temporary files that were created during the test
        for temp_file in [self.inode_map_file, self.snapshot_file, self.non_restored_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_inode_map_saved_correctly(self):
        """Test saving the inode map to a debug file."""
        # Build inode map for the target directory and save it to a file
        inode_map_file = '/tmp/test_inode_map.json'
        inode_map = build_inode_map([self.target_dir], debug_inode_map_file=inode_map_file)
        
        # Check that the inode map file exists and contains data
        self.assertTrue(os.path.exists(inode_map_file))
        
        with open(inode_map_file, 'r') as f:
            inode_map_content = json.load(f)
        
        # Ensure the inode map contains entries for the target files
        for target_link in self.target_links:
            inode = os.stat(target_link).st_ino
            # Ensure inode is in the map (it might be stored as a string in the JSON file)
            self.assertIn(str(inode), inode_map_content)
            self.assertIn(target_link, inode_map_content[str(inode)])
    
    def test_snapshot_creation(self):
        """Test the creation of a snapshot of hard links."""
        # Build inode map for the target directory
        inode_map_file = '/tmp/test_inode_map.json'
        inode_map = build_inode_map([self.target_dir], debug_inode_map_file=inode_map_file)

        # Create snapshot
        snapshot_file = '/tmp/test_snapshot.json'
        create_snapshot(self.source_dir, inode_map, snapshot_file)
        
        # Check that the snapshot file exists and has content
        self.assertTrue(os.path.exists(snapshot_file))
        
        with open(snapshot_file, 'r') as f:
            snapshot_content = json.load(f)
        
        # Ensure that the snapshot contains the correct source -> target links
        for source_file in self.source_files:
            self.assertIn(source_file, snapshot_content, f"Source file {source_file} not found in snapshot")
            
            # Retrieve the target links for the source file
            target_links_from_snapshot = snapshot_content[source_file]
            
            # Get the expected target links for the source file from the global setup (stem is just the file name without extension)
            expected_target_links = [link for link in self.target_links if os.path.basename(link).startswith(f"link_to_{Path(source_file).stem}")]
            
            # Ensure the snapshot contains all expected target links for this source file
            for target_link in expected_target_links:
                self.assertIn(target_link, target_links_from_snapshot, f"Target link {target_link} for {source_file} not found in snapshot")

    def test_restore_hardlinks(self):
        """Test restoring the hard links from the snapshot."""
        # Build inode map for the target directory
        inode_map_file = '/tmp/test_inode_map.json'
        inode_map = build_inode_map([self.target_dir], debug_inode_map_file=inode_map_file)

        # Create snapshot
        snapshot_file = '/tmp/test_snapshot.json'
        create_snapshot(self.source_dir, inode_map, snapshot_file)

        # Delete existing hard links in the target directory before restoring
        for target_link in self.target_links:
            if os.path.exists(target_link):
                os.remove(target_link)
        
        # Now restore the links using the snapshot to the original target directory
        restore_hardlinks(snapshot_file)
        
        # Verify that the hard links were restored correctly in the original target directory
        for target_link in self.target_links:
            self.assertTrue(os.path.exists(target_link), f"Hardlink not found: {target_link}")
            
    def test_non_restored_hardlinks(self):
        """Test the creation of a non-restored hard links report."""
        # Create a snapshot with a target that will fail restoration (e.g., by tampering with the target file)
        snapshot_file = '/tmp/test_snapshot.json'
        inode_map_file = '/tmp/test_inode_map.json'
        inode_map = build_inode_map([self.target_dir], debug_inode_map_file=inode_map_file)
        create_snapshot(self.source_dir, inode_map, snapshot_file)

        # Break the hard link by removing one of the target links
        target_link = self.target_links[0]  # Take the first target link
        os.remove(target_link)  # This simulates breaking the hard link
        
        # Recreate the target link, but with different content (simulate a mismatch)
        with open(target_link, 'w') as f:
            f.write("Modified content that differs from the source file.")

        # Run the restore process and generate the non-restored file
        non_restored_file = '/tmp/non_restored_hardlinks.json'
        restore_hardlinks(snapshot_file, non_restored_file)

        # Check that the non-restored file exists and contains the correct entries
        self.assertTrue(os.path.exists(non_restored_file))
        
        with open(non_restored_file, 'r') as f:
            non_restored_content = json.load(f)

        # Ensure the non-restored link is listed
        self.assertGreater(len(non_restored_content), 0)
        self.assertIn("source_file", non_restored_content[0])
        self.assertIn("target_file", non_restored_content[0])
        self.assertIn("reason", non_restored_content[0])

    def test_non_restored_hardlinks_content_diff(self):
        """Test the creation of a non-restored hard links report with only content change."""
        # Create a snapshot with a target that will fail restoration (e.g., by tampering with the target file)
        snapshot_file = '/tmp/test_snapshot.json'
        inode_map_file = '/tmp/test_inode_map.json'
        inode_map = build_inode_map([self.target_dir], debug_inode_map_file=inode_map_file)
        create_snapshot(self.source_dir, inode_map, snapshot_file)

        # Break the hard link by removing one of the target links
        target_link = self.target_links[0]  # Take the first target link
        os.remove(target_link)  # This simulates breaking the hard link
        
        # Recreate the target link with the exact same content and size as the source
        source_file = self.source_files[0]
        with open(source_file, 'rb') as src_f:
            source_content = src_f.read()  # Read source file content
            
        with open(target_link, 'wb') as tgt_f:
            tgt_f.write(source_content)  # Copy content from source to target

        # Ensure the modified file has the same size and timestamp as the original
        source_file = self.source_files[0]
        source_stat = os.stat(source_file)
        target_stat = os.stat(target_link)
        
        # Now let's ensure the content is different while keeping the size the same
        # Overwrite specific bytes of the file to ensure the content is different but the size is unchanged
        file_size = os.path.getsize(target_link)
        
        # Calculate a safe position to seek (e.g., 10% into the file, but no greater than the file size)
        seek_position = min(file_size // 10, file_size - 2)  # Ensures we're within bounds

        with open(target_link, 'r+b') as f:  # Open for reading and writing binary
            f.seek(seek_position)  # Seek to the calculated safe byte position
            f.write(b'X')  # Overwrite a byte with a different character

        # Match size and modification time, but different content
        os.utime(target_link, (source_stat.st_atime, source_stat.st_mtime))  # Same modification time
        
        # Now, explicitly check that the size and attributes (timestamps) match before proceeding
        target_stat = os.stat(target_link)
        self.assertEqual(source_stat.st_size, target_stat.st_size, "File size does not match after modification")
        self.assertEqual(source_stat.st_mtime, target_stat.st_mtime, "Modification time does not match after restoration")

        # Run the restore process and generate the non-restored file
        non_restored_file = '/tmp/non_restored_hardlinks.json'
        restore_hardlinks(snapshot_file, non_restored_file)

        # Check that the non-restored file exists and contains the correct entries
        self.assertTrue(os.path.exists(non_restored_file))
        
        with open(non_restored_file, 'r') as f:
            non_restored_content = json.load(f)

        # Ensure the non-restored link is listed
        self.assertGreater(len(non_restored_content), 0)
        self.assertIn("source_file", non_restored_content[0])
        self.assertIn("target_file", non_restored_content[0])
        self.assertIn("reason", non_restored_content[0])

        # Ensure the modified target file is added to the non-restored list because of content mismatch
        modified_target_link_entry = next(
            (entry for entry in non_restored_content if entry["target_file"] == target_link), None)
        self.assertIsNotNone(modified_target_link_entry)
        self.assertEqual(modified_target_link_entry["reason"], "Content mismatch (hashes do not match)")

    def test_restore_broken_hardlink_with_same_file(self):
        """Test restoring a broken hard link where the file is recreated with the same content, size, and attributes."""
        snapshot_file = '/tmp/test_snapshot.json'
        inode_map_file = '/tmp/test_inode_map.json'
        inode_map = build_inode_map([self.target_dir], debug_inode_map_file=inode_map_file)
        create_snapshot(self.source_dir, inode_map, snapshot_file)

        # Break the hard link by removing one of the target links
        target_link = self.target_links[0]  # Take the first target link
        os.remove(target_link)  # This simulates breaking the hard link
        
        # Recreate the target link with the same content, size, and attributes
        source_file = self.source_files[0]  # Corresponding source file
        shutil.copy2(source_file, target_link)  # Recreate the file with the same content and attributes
        
        # Run the restore process and verify no issues are raised
        non_restored_file = '/tmp/non_restored_hardlinks.json'
        restore_hardlinks(snapshot_file, non_restored_file)

        # Check that the non-restored file does not contain any entries
        self.assertFalse(os.path.exists(non_restored_file), "Non-restored hardlinks file should not exist.")

        # Verify that the restored hard link has the correct attributes and content
        self.assertTrue(os.path.exists(target_link), f"Restored hardlink not found: {target_link}")
        
        # Check that the source and restored target link have the same inode (indicating it's the same file)
        source_stat = os.stat(source_file)
        target_stat = os.stat(target_link)
        
        self.assertEqual(source_stat.st_ino, target_stat.st_ino, "Inodes do not match; hardlink was not restored correctly.")
        
        # Also, ensure the content matches exactly
        with open(source_file, 'r') as f:
            source_content = f.read()
        
        with open(target_link, 'r') as f:
            target_content = f.read()
        
        self.assertEqual(source_content, target_content, "Content of restored hardlink does not match source file.")

        # Verify that the attributes are the same (permissions, timestamps, etc.)
        self.assertEqual(source_stat.st_mode, target_stat.st_mode, "Permissions do not match.")
        self.assertEqual(source_stat.st_mtime, target_stat.st_mtime, "Modification time does not match.")
        self.assertEqual(source_stat.st_atime, target_stat.st_atime, "Access time does not match.")
        self.assertEqual(source_stat.st_ctime, target_stat.st_ctime, "Change time does not match.")
        
        
if __name__ == '__main__':
    unittest.main()

