
import os
import re
import configparser

# Load configuration from config.ini (INI format)
config = configparser.ConfigParser()
config.read('config.ini')

# Extract keywords from the configuration file
KEYWORDS = [kw.strip().lower() for kw in config.get('Settings', 'filterwords').split(',')]
MAP_FILE = config.get('Settings', 'destination_map_file', fallback='hardlink_mappings.txt')  # Destination map file

def clean_name(name, is_file):
    # Separate extension if it's a file
    root, ext = os.path.splitext(name) if is_file else (name, '')

    # Strip text within square brackets (e.g., [text]) and text within parentheses (e.g., (text))
    root = re.sub(r'\[[^]]*\]', '', root)
    root = re.sub(r'\([^)]*\)', '', root)

    # Remove specified keywords (case insensitive)
    for keyword in KEYWORDS:
        root = re.sub(re.escape(keyword), '', root, flags=re.IGNORECASE)

    # Convert periods to spaces in the root part of the name
    root = root.replace('.', ' ')

    # Trim leading and trailing whitespace
    root = root.strip()

    # Remove invalid filesystem characters
    root = re.sub(r'[\/:*?"<>|]', '', root)

    # Normalize spaces (replace multiple spaces with a single space)
    root = re.sub(r'\s+', ' ', root)

    # Combine cleaned root with original extension if it's a file
    if is_file:
        return root + ext
    else:
        return root

def main(source_folder=None):
    # If no source folder provided, read from the config file
    if source_folder is None:
        source_folder = config.get('Settings', 'source_folder')

    # Check if the source folder exists
    if not os.path.isdir(source_folder):
        print(f"Error: Source folder does not exist: {source_folder}")
        return

    # Clean the mappings file for each run
    with open(MAP_FILE, 'w') as f:
        pass  # Truncate the file

    # Iterate over all top-level files and directories in the source folder
    for item in os.listdir(source_folder):
        item_path = os.path.join(source_folder, item)
        name = os.path.basename(item_path)
        is_file = os.path.isfile(item_path)

        # Clean the name
        cleaned_name = clean_name(name, is_file)

        # Log the mapping: original name to cleaned name
        with open(MAP_FILE, 'a') as map_file:
            map_file.write(f"{name}:{cleaned_name}\n")

    print(f"Mapping file created: {MAP_FILE}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        # Use the source folder from the command line argument
        main(sys.argv[1])
    else:
        # If no argument is provided, use the source folder from the config file
        main()

