import os
import re
import configparser

# Load configuration from config.ini (INI format)
config = configparser.ConfigParser()
config.read('config.ini')

# Extract keywords from the configuration file
KEYWORDS = [kw.strip().lower() for kw in config.get('Settings', 'filterwords').split(',')]
MAP_FILE = config.get('Settings', 'destination_map_file', fallback='hardlink_mappings.txt')  # Destination map file

# Function to clean the name by removing text in square brackets, parentheses, and specified keywords
def clean_name(name):
    # Strip text within square brackets (e.g., [text]) and text within parentheses (e.g., (text))
    name = re.sub(r'\[[^]]*\]', '', name)
    name = re.sub(r'\([^)]*\)', '', name)

    # Remove specified keywords (case insensitive)
    for keyword in KEYWORDS:
        name = re.sub(re.escape(keyword), '', name, flags=re.IGNORECASE)

    # Trim leading and trailing whitespace
    name = name.strip()

    # Remove invalid filesystem characters and trailing dots/spaces
    name = re.sub(r'[\/:*?"<>|]', '', name)
    name = re.sub(r'[. ]*$', '', name)

    return name

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

        # Clean the name
        cleaned_name = clean_name(name)

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
