import sys
import os
import json
import logging
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from raw_hardlinker import create_hardlinks

# Default path to the configuration file
DEFAULT_CONFIG_FILE = '/media/hardlinker/config.json'
LOG_FILE = 'qbit_linker.log'

# Set up logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), LOG_FILE),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_config(config_path=None, config_data=None):
    logging.info("Loading configuration...")
    if config_data:
        logging.info("Using provided config data")
        return json.loads(config_data)
    
    config_path = config_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), DEFAULT_CONFIG_FILE)
    logging.info(f"Loading config from file: {config_path}")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            logging.info("Configuration loaded successfully")
            return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in configuration file: {config_path}")
        sys.exit(1)

def get_destination_folder(config, category):
    logging.info(f"Getting destination folder for category: {category}")
    category_parts = category.split('/')
    current_map = config['category_map']
    path_parts = []

    for i, part in enumerate(category_parts):
        logging.debug(f"Processing part: {part}")
        lower_part = part.lower()
        if lower_part in [k.lower() for k in current_map.keys()]:
            key = next(k for k in current_map.keys() if k.lower() == lower_part)
            logging.debug(f"Match found in config: {key}")
            if isinstance(current_map[key], str):
                result = os.path.join(current_map[key], *category_parts[i+1:])
                logging.info(f"Leaf node reached. Final path: {result}")
                return result
            else:
                path_parts.append(part)
                logging.debug(f"Added to path: {part}")
                current_map = current_map[key]
        else:
            logging.debug(f"No match found for: {part}")
            if path_parts:
                result = os.path.join(config['root_default_directory'], *path_parts, *category_parts[i:])
            else:
                result = os.path.join(config['root_default_directory'], *category_parts)
            logging.info(f"Using default directory. Final path: {result}")
            return result
    
    if path_parts:
        result = os.path.join(config['root_default_directory'], *path_parts)
    else:
        result = os.path.join(config['root_default_directory'], *category_parts)
    logging.info(f"Reached end of category parts. Final path: {result}")
    return result

def apply_root_mapping(config, path):
    for source, dest in config.get('root_mapping', {}).items():
        if path.startswith(source):
            mapped_path = path.replace(source, dest, 1)
            logging.info(f"Applied root mapping: {path} -> {mapped_path}")
            return mapped_path
    return path

def main(config_path=None, config_data=None):
    logging.info("Starting qbit_linker...")
    if len(sys.argv) != 3:
        logging.error("Incorrect number of arguments")
        logging.error("Usage: python qbit_linker.py <content_path> <category>")
        sys.exit(1)

    content_path = sys.argv[1]
    category = sys.argv[2]
    logging.info(f"Original content path: {content_path}")
    logging.info(f"Category: {category}")

    config = load_config(config_path, config_data)
    logging.info("Configuration loaded")

    # Apply root mapping to content_path
    mapped_content_path = apply_root_mapping(config, content_path)
    logging.info(f"Mapped content path: {mapped_content_path}")
    
    dest_folder = get_destination_folder(config, category)
    logging.info(f"Destination folder: {dest_folder}")

    full_dest_path = os.path.join(dest_folder, os.path.basename(mapped_content_path))
    logging.info(f"Full destination path: {full_dest_path}")

    logging.info(f"Creating destination directory: {os.path.dirname(full_dest_path)}")
    os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)

    logging.info("Calling raw_hardlinker to create hardlinks...")
    create_hardlinks(mapped_content_path, full_dest_path)

    logging.info(f"Hardlinks created: {mapped_content_path} -> {full_dest_path}")
    logging.info("qbit_linker completed successfully")

if __name__ == "__main__":
    main()

