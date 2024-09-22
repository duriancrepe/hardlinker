
import subprocess
import configparser
import os

# Load configuration from config.ini (INI format)
config = configparser.ConfigParser()
config.read('config.ini')

def create_output_directories():
    """Create output directories for logs and intermediate files."""
    output_dir = os.path.dirname(config.get('OMDb', 'source_map_file', fallback='hardlink_mappings.txt'))
    os.makedirs(output_dir, exist_ok=True)
    
    output_dir = os.path.dirname(config.get('OMDb', 'destination_map_file', fallback='hardlink_mappings_omdb.txt'))
    os.makedirs(output_dir, exist_ok=True)

    output_dir = os.path.dirname(config.get('Settings', 'hardlink_log_file', fallback='hardlink_log.txt'))
    os.makedirs(output_dir, exist_ok=True)

    output_dir = os.path.dirname(config.get('Settings', 'unknown_items_map_file', fallback='unknown_items_map.txt'))
    os.makedirs(output_dir, exist_ok=True)

def run_mapper(source_folder):
    """Run the mapper.py script."""
    try:
        subprocess.run(['python', 'mapper.py', source_folder], check=True)
        print("Mapper completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error in mapper: {e}")

def run_multi_db_mapper():
    """Run the multi_db_mapper.py script."""
    try:
        subprocess.run(['python', 'multi_db_mapper.py'], check=True)
        print("Multi-database mapper completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error in multi-database mapper: {e}")

def main():
    create_output_directories()  # Ensure output directories exist

    source_folder = config.get('Settings', 'source_folder')
    destination_folder = config.get('Settings', 'destination_folder')
    use_raw_hardlinker = config.getboolean('Settings', 'use_raw_hardlinker', fallback=False)

    if not use_raw_hardlinker:
        # Run the mapping process
        run_mapper(source_folder)
        
        # Run the multi-database mapping
        run_multi_db_mapper()
        
        # Run the mapped hardlinking process
        run_map_hardlinker(source_folder, destination_folder)
    else:
        # Run the raw hardlinking process
        run_raw_hardlinker(source_folder, destination_folder)

if __name__ == "__main__":
    main()
