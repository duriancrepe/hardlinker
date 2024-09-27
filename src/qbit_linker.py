import sys
import os
import json

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from raw_hardlinker import create_hardlinks

# Default path to the configuration file
DEFAULT_CONFIG_FILE = '/media/hardlinker/config.json'

def load_config(config_path=None, config_data=None):
    if config_data:
        return json.loads(config_data)
    
    config_path = config_path or DEFAULT_CONFIG_FILE
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Invalid JSON in configuration file: {config_path}")
        sys.exit(1)

def get_destination_folder(config, category):
    category_parts = category.split('/')
    current_map = config['category_map']
    path_parts = []

    for i, part in enumerate(category_parts):
        lower_part = part.lower()
        if lower_part in [k.lower() for k in current_map.keys()]:
            key = next(k for k in current_map.keys() if k.lower() == lower_part)
            if isinstance(current_map[key], str):
                # If it's a string (leaf node), use it and add remaining parts
                return os.path.join(current_map[key], *category_parts[i+1:])
            else:
                path_parts.append(part)  # Use original casing
                current_map = current_map[key]
        else:
            # If part not found, use the path we've built so far or root_default_directory
            if path_parts:
                return os.path.join(config['root_default_directory'], *path_parts, *category_parts[i:])
            else:
                return os.path.join(config['root_default_directory'], *category_parts)
    
    # If we've gone through all parts and ended up in a dict, use what we've built so far
    if path_parts:
        return os.path.join(config['root_default_directory'], *path_parts)
    else:
        return os.path.join(config['root_default_directory'], *category_parts)

def main(config_path=None, config_data=None):
    if len(sys.argv) != 3:
        print("Usage: python qbit_linker.py <content_path> <category>")
        sys.exit(1)

    content_path = sys.argv[1]
    category = sys.argv[2]

    config = load_config(config_path, config_data)
    
    # Get the destination folder based on the category
    dest_folder = get_destination_folder(config, category)

    # Create the full destination path
    full_dest_path = os.path.join(dest_folder, os.path.basename(content_path))

    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)

    # Call the raw_hardlinker function
    create_hardlinks(content_path, full_dest_path)

    print(f"Hardlinks created: {content_path} -> {full_dest_path}")

if __name__ == "__main__":
    main()

