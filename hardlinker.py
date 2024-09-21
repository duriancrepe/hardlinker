import os
import shutil
import configparser

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Configuration
MAP_FILE = config.get('OMDb', 'destination_map_file', fallback='hardlink_mappings_omdb.txt')
HARDLINK_LOG_FILE = config.get('Settings', 'hardlink_log_file', fallback='hardlink_log.txt')
UNKNOWN_ITEMS_MAP_FILE = config.get('Settings', 'unknown_items_map_file', fallback='unknown_items_map.txt')

def load_map_file(map_file):
    """Load the file-folder map from a text file."""
    file_folder_map = {}
    with open(map_file, 'r') as f:
        for line in f:
            original_name, cleaned_name = line.strip().split(':')
            file_folder_map[original_name] = cleaned_name
    return file_folder_map

def create_hardlink(src, dest):
    """Create a hardlink for a file."""
    if os.path.isfile(src):
        os.link(src, dest)
        return True
    return False

def create_hardlinks_for_folder(src_folder, dest_folder):
    """Recursively create hardlinks for all files in a folder."""
    for root, _, files in os.walk(src_folder):
        relative_root = os.path.relpath(root, src_folder)
        dest_root = os.path.join(dest_folder, relative_root)
        os.makedirs(dest_root, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)
            os.link(src_file, dest_file)

def main(source_folder, destination_root_folder):
    # Check if the source folder exists
    if not os.path.exists(source_folder):
        print(f"Error: Source folder does not exist: {source_folder}")
        return

    # Check if the map file exists
    if not os.path.exists(MAP_FILE):
        print(f"Error: Map file does not exist: {MAP_FILE}")
        return

    # Load the file-folder map
    file_folder_map = load_map_file(MAP_FILE)

    # Create the destination root folder if it doesn't exist
    os.makedirs(destination_root_folder, exist_ok=True)

    unknown_items = []  # List to track unknown items
    occurrence_count = {}  # Dictionary to track occurrences of each destination item

    with open(HARDLINK_LOG_FILE, 'w') as hardlink_log:
        for item in os.listdir(source_folder):
            item_path = os.path.join(source_folder, item)

            if item in file_folder_map:
                dest_name = file_folder_map[item]
                dest_folder_path = os.path.join(destination_root_folder, dest_name)

                # Count occurrences for folder naming (only for folders)
                occurrence_count[dest_name] = occurrence_count.get(dest_name, 0) + 1
                count = occurrence_count[dest_name]

                # Modify the folder destination name by occurrence, but keep the original file name
                dest_folder_path = f"{dest_folder_path} ({count})" if count > 1 else dest_folder_path

                if os.path.isdir(item_path):
                    # Skip if the destination folder already exists
                    if os.path.exists(dest_folder_path):
                        print(f"Skipping existing folder: {dest_folder_path}")
                        continue
                    # Create hardlinks for all files in the folder recursively
                    create_hardlinks_for_folder(item_path, dest_folder_path)
                    hardlink_log.write(f"Hardlinked folder: {item_path} -> {dest_folder_path}\n")
                else:
                    # Ensure the destination folder for the file exists
                    os.makedirs(dest_folder_path, exist_ok=True)

                    # For files, always use the original file name, without adding occurrences
                    dest_file_path = os.path.join(dest_folder_path, item)

                    if create_hardlink(item_path, dest_file_path):
                        hardlink_log.write(f"Hardlinked file: {item_path} -> {dest_file_path}\n")
            else:
                # Track unmapped items with the original name
                unknown_items.append(item)

    # Create the unknown items file only if there are unknown items
    if unknown_items:
        with open(UNKNOWN_ITEMS_MAP_FILE, 'w') as unknown_map:
            for unknown_item in unknown_items:
                unknown_map.write(f"{unknown_item}:{unknown_item}\n")
        print(f"Unknown items are listed in {UNKNOWN_ITEMS_MAP_FILE}. Please update your map file.")
    else:
        print("No unknown items found.")

    print(f"Operation completed. Hardlinks created are logged in {HARDLINK_LOG_FILE}.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python hardlinker.py <source_folder> <destination_root_folder>")
    else:
        main(sys.argv[1], sys.argv[2])
