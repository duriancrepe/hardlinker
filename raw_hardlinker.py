import os
import sys

def create_hardlinks(src_dir, dest_dir):
    """Recursively create hardlinks for all files in the source directory to the destination directory."""
    
    if not os.path.exists(src_dir):
        print(f"Error: Source directory '{src_dir}' does not exist.")
        sys.exit(1)

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created destination directory: {dest_dir}")

    for root, dirs, files in os.walk(src_dir):
        relative_path = os.path.relpath(root, src_dir)
        dest_subdir = os.path.join(dest_dir, relative_path)
        
        if not os.path.exists(dest_subdir):
            os.makedirs(dest_subdir)
            print(f"Created subdirectory: {dest_subdir}")

        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_subdir, file)
            
            if not os.path.exists(dest_file):
                os.link(src_file, dest_file)
                print(f"Hardlinked: {src_file} -> {dest_file}")
            else:
                print(f"Skipped (already exists): {dest_file}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python hardlinker.py <source_directory> <destination_directory>")
        sys.exit(1)

    src_dir = sys.argv[1]
    dest_dir = sys.argv[2]

    create_hardlinks(src_dir, dest_dir)

if __name__ == "__main__":
    main()
