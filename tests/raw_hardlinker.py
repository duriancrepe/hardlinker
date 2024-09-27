import os
import sys
import logging
from datetime import datetime

# Set up logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw_hardlinker.log')
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def create_hardlink(src, dest):
    """Create a hardlink from source to destination."""
    logging.info(f"Attempting to create hardlink: {src} -> {dest}")
    try:
        os.link(src, dest)
        logging.info(f"Hardlink created successfully: {src} -> {dest}")
        print(f"Hardlinked: {src} -> {dest}")
    except FileExistsError:
        logging.warning(f"Hardlink already exists: {dest}")
        print(f"Skipped (already exists): {dest}")
    except Exception as e:
        logging.error(f"Error creating hardlink: {src} -> {dest}")
        logging.error(f"Error message: {str(e)}")
        print(f"Error creating hardlink: {src} -> {dest}")
        print(f"Error message: {str(e)}")
        raise

def create_hardlinks(src, dest):
    """Create hardlinks from source to destination, handling both files and directories."""
    logging.info(f"Starting hardlink creation process: {src} -> {dest}")
    
    if not os.path.exists(src):
        logging.error(f"Error: Source '{src}' does not exist.")
        print(f"Error: Source '{src}' does not exist.")
        sys.exit(1)

    logging.info(f"Source exists: {src}")

    if os.path.isfile(src):
        logging.info(f"Source is a file: {src}")
        if os.path.isdir(dest):
            dest_file = os.path.join(dest, os.path.basename(src))
            logging.info(f"Destination is a directory. Using filename: {dest_file}")
        else:
            dest_file = dest
            logging.info(f"Destination is a file path: {dest_file}")

        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        logging.info(f"Ensured destination directory exists: {os.path.dirname(dest_file)}")
        create_hardlink(src, dest_file)
    
    elif os.path.isdir(src):
        logging.info(f"Source is a directory: {src}")
        if not os.path.exists(dest):
            os.makedirs(dest)
            logging.info(f"Created destination directory: {dest}")
            print(f"Created destination directory: {dest}")

        for root, dirs, files in os.walk(src):
            relative_path = os.path.relpath(root, src)
            dest_subdir = os.path.join(dest, relative_path)
            logging.info(f"Processing subdirectory: {dest_subdir}")
            
            if not os.path.exists(dest_subdir):
                os.makedirs(dest_subdir)
                logging.info(f"Created subdirectory: {dest_subdir}")
                print(f"Created subdirectory: {dest_subdir}")


            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_subdir, file)
                logging.info(f"Processing file: {src_file} -> {dest_file}")
                create_hardlink(src_file, dest_file)

    logging.info("Hardlink creation process completed.")

def main():
    logging.info("raw_hardlinker script started")
    if len(sys.argv) != 3:
        logging.error("Incorrect number of arguments provided")
        print("Usage: python raw_hardlinker.py <source> <destination>")
        print("\nExamples:")
        print("  1. Directory to directory:")
        print("     python raw_hardlinker.py /path/to/source_dir /path/to/dest_dir")
        print("\n  2. File to directory:")
        print("     python raw_hardlinker.py /path/to/source_file.txt /path/to/dest_dir/")
        print("\n  3. File to file (rename):")
        print("     python raw_hardlinker.py /path/to/source_file.txt /path/to/dest_file.txt")
        sys.exit(1)

    src = sys.argv[1]
    dest = sys.argv[2]
    logging.info(f"Arguments received - Source: {src}, Destination: {dest}")

    create_hardlinks(src, dest)
    logging.info("raw_hardlinker script completed")

if __name__ == "__main__":
    main()


