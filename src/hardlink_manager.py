import argparse
import hashlib
import json
import os
import time

def build_inode_map(target_folders, debug_inode_map_file=None):
    """Build a map of inodes to lists of files in the target folders."""
    inode_map = {}
    total_files = 0

    # Traverse the target folders and build inode map
    for target_folder in target_folders:
        for dirpath, _, filenames in os.walk(target_folder):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    inode = os.stat(filepath).st_ino
                    if inode not in inode_map:
                        inode_map[inode] = []
                    inode_map[inode].append(filepath)
                    total_files += 1
                    if total_files % 1000 == 0:
                        print(f"Processed {total_files} files...")
                except Exception as e:
                    print(f"Error processing file {filepath}: {e}")
    
    print(f"Finished building inode map for {total_files} files.")
    
    # Optionally save the inode map to a debug file
    if debug_inode_map_file:
        try:
            with open(debug_inode_map_file, 'w') as debug_file:
                json.dump(inode_map, debug_file, indent=2)
            print(f"Inode map saved to {debug_inode_map_file}")
        except Exception as e:
            print(f"Failed to save inode map: {e}")
    
    return inode_map


def create_snapshot(source_folder, inode_map, snapshot_file):
    """Create a snapshot of hard links from source folder based on inode map."""
    snapshot = {}
    total_files = 0

    # Traverse the source folder and check each file's inode
    for dirpath, _, filenames in os.walk(source_folder):
        for filename in filenames:
            source_file = os.path.join(dirpath, filename)
            try:
                inode = os.stat(source_file).st_ino
                if inode in inode_map:
                    # Found matching hard links in the target folders
                    target_hardlinks = inode_map[inode]
                    snapshot[source_file] = target_hardlinks
                    total_files += 1
                    if total_files % 1000 == 0:
                        print(f"Processed {total_files} source files...")
            except Exception as e:
                print(f"Error processing file {source_file}: {e}")

    # Write the snapshot to the output file in JSON format
    try:
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot, f, indent=4)
        print(f"Snapshot saved to {snapshot_file}")
    except Exception as e:
        print(f"Error saving snapshot to {snapshot_file}: {e}")

def hash_file(file_path):
    """Generate a SHA256 hash for the given file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in 4K chunks to avoid loading large files into memory all at once
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def restore_hardlinks(snapshot_file, non_restored_file="non_restored_hardlinks.json"):
    """Restore hard links based on the snapshot, check file attributes and skip if they do not match."""
    
    non_restored_links = []  # List to store non-restored links for review
    
    with open(snapshot_file, 'r') as f:
        snapshot_data = json.load(f)

    for source_file, target_files in snapshot_data.items():
        for target_file in target_files:
            try:
                # Check if the target file exists
                if os.path.exists(target_file):
                    source_stat = os.stat(source_file)
                    target_stat = os.stat(target_file)

                    # Check if source and target are already hardlinked (same inode)
                    if source_stat.st_ino == target_stat.st_ino:
                        print(f"Source {source_file} and target {target_file} are already hardlinked, skipping.")
                        continue  # Skip creating the link if they are already hardlinked

                    # Check if the file sizes and modification times match
                    if source_stat.st_size == target_stat.st_size and source_stat.st_mtime == target_stat.st_mtime:
                        # Hash the contents of both the source and target files
                        source_hash = hash_file(source_file)
                        target_hash = hash_file(target_file)

                        # If hashes do not match, skip restoration and add to non-restored list
                        if source_hash != target_hash:
                            print(f"Source {source_file} and target {target_file} have different contents, skipping restoration.")
                            non_restored_links.append({
                                "source_file": source_file,
                                "target_file": target_file,
                                "reason": "Content mismatch (hashes do not match)"
                            })
                            continue  # Skip restoration if contents are different

                        # If hashes match, delete the target file and create the hard link
                        os.remove(target_file)
                        os.link(source_file, target_file)
                        print(f"Deleted {target_file} and created hardlink from {source_file} -> {target_file}")
                    else:
                        # If attributes don't match, skip this link and add to non-restored list
                        print(f"Attributes do not match for {target_file}, skipping restoration.")
                        non_restored_links.append({
                            "source_file": source_file,
                            "target_file": target_file,
                            "reason": "Attributes do not match"
                        })
                else:
                    # If the target file doesn't exist, ensure parent directories exist and create the hard link
                    parent_dir = os.path.dirname(target_file)

                    # Ensure the parent directory exists (create it if it doesn't)
                    if not os.path.exists(parent_dir):
                        os.makedirs(parent_dir)
                        print(f"Created parent directory: {parent_dir}")
    
                    os.link(source_file, target_file)
                    print(f"Created hardlink: {source_file} -> {target_file}")
            
            except Exception as e:
                print(f"Error processing link from {source_file} to {target_file}: {e}")
    
    # After processing, save the list of non-restored links to a file if any
    if non_restored_links:
        with open(non_restored_file, 'w') as f:
            json.dump(non_restored_links, f, indent=4)
        print(f"Non-restored hardlinks saved to {non_restored_file}")
    else:
        print("All hardlinks were restored successfully.")

    print("Restoration complete.")
    
    
def main():
    parser = argparse.ArgumentParser(description="Snapshot and restore hardlinks.")
    parser.add_argument('action', choices=['snapshot', 'restore'], help="Action to perform")
    parser.add_argument('source_folder', help="Path to the source folder")
    parser.add_argument('target_folders', nargs='+', help="List of target folders to track hard links")
    parser.add_argument('snapshot_file', help="Snapshot file path (for restore or save)")
    parser.add_argument('--debug_inode_map_file', help="File to save the inode map for debugging", default=None)

    args = parser.parse_args()

    if args.action == 'snapshot':
        inode_map = build_inode_map(args.target_folders, args.debug_inode_map_file)
        create_snapshot(args.source_folder, inode_map, args.snapshot_file)
    elif args.action == 'restore':
        restore_hardlinks(args.snapshot_file)


if __name__ == '__main__':
    main()

