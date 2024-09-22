
import subprocess
import configparser
import os
import shutil

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

def clean_output_dir(folder):
    """Remove all contents of the specified folder if it exists."""
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
        print(f"Output directory cleaned: {folder}")
    else:
        print(f"Output directory does not exist, will be created: {folder}")

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
        
def run_map_hardlinker(source_folder, destination_folder):
    """Run the map_hardlinker.py script."""
    try:
        subprocess.run(['python', 'map_hardlinker.py', source_folder, destination_folder], check=True)
        print("Mapped hardlinker completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error in mapped hardlinker: {e}")

def run_raw_hardlinker(source_folder, destination_folder):
    """Run the raw_hardlinker.py script."""
    try:
        subprocess.run(['python', 'raw_hardlinker.py', source_folder, destination_folder], check=True)
        print("Raw hardlinker completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error in raw hardlinker: {e}")
        
def main():
    create_output_directories()  # Ensure output directories exist

    source_folder = config.get('Settings', 'source_folder')
    destination_folder = config.get('Settings', 'destination_folder')
    use_raw_hardlinker = config.getboolean('Settings', 'use_raw_hardlinker', fallback=False)
    clean_output = config.getboolean('Settings', 'clean_output_dir', fallback=False)

    if clean_output:
        clean_output_dir(destination_folder)

    # Ensure the destination folder exists
    os.makedirs(destination_folder, exist_ok=True)

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

