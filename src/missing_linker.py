import os
import shutil

# Define the source and target directories
source_dir = "/mnt/storage/media/downloads"
target_dir = "/mnt/storage/media/hardlinks/missing/"

# Iterate over all subdirectories and files in the source directory
for root, dirs, files in os.walk(source_dir):
    # Extract the first level of subdirectory
    relative_path = os.path.relpath(root, source_dir).split(os.sep)[0]

    # Only process files in subdirectories, not the root
    if relative_path == '.':
        continue

    # Check each file in the subdirectory
    for file in files:
        if file.endswith(".mkv"):
            # Get the full path of the file
            file_path = os.path.join(root, file)

            # Check if the file has no hardlinks (link count == 1)
            if os.stat(file_path).st_nlink == 1:
                # Create the corresponding target subdirectory
                target_subdir = os.path.join(target_dir, relative_path)
                os.makedirs(target_subdir, exist_ok=True)

                # Define the target hardlink path
                target_file_path = os.path.join(target_subdir, file)

                # Create a hardlink in the target directory
                try:
                    os.link(file_path, target_file_path)
                    print(f"Created hardlink: {target_file_path}")
                except FileExistsError:
                    print(f"Hardlink already exists: {target_file_path}")
                except Exception as e:
                    print(f"Error creating hardlink for {file_path}: {e}")
