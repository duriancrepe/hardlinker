
import os
import sys

def create_hardlink(src, dest):
    """Create a hardlink from source to destination."""
    try:
        os.link(src, dest)
        print(f"Hardlinked: {src} -> {dest}")
    except FileExistsError:
        print(f"Skipped (already exists): {dest}")
    except Exception as e:
        print(f"Error creating hardlink: {src} -> {dest}")
        print(f"Error message: {str(e)}")

def create_hardlinks(src, dest):
    """Create hardlinks from source to destination, handling both files and directories."""
    
    if not os.path.exists(src):
        print(f"Error: Source '{src}' does not exist.")
        sys.exit(1)

    if os.path.isfile(src):
        if os.path.isdir(dest):
            # If dest is a directory, use the same filename
            dest_file = os.path.join(dest, os.path.basename(src))
        else:
            # If dest doesn't end with '/', assume it's a full file path
            dest_file = dest

        # Create the destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dest_file), exist_ok=True)
        create_hardlink(src, dest_file)
    
    elif os.path.isdir(src):
        if not os.path.exists(dest):
            os.makedirs(dest)
            print(f"Created destination directory: {dest}")

        for root, dirs, files in os.walk(src):
            relative_path = os.path.relpath(root, src)
            dest_subdir = os.path.join(dest, relative_path)
            
            if not os.path.exists(dest_subdir):
                os.makedirs(dest_subdir)
                print(f"Created subdirectory: {dest_subdir}")

            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_subdir, file)
                create_hardlink(src_file, dest_file)

def main():
    if len(sys.argv) != 3:
        print("Usage: python hardlinker.py <source> <destination>")
        print("\nExamples:")
        print("  1. Directory to directory:")
        print("     python hardlinker.py /path/to/source_dir /path/to/dest_dir")
        print("\n  2. File to directory:")
        print("     python hardlinker.py /path/to/source_file.txt /path/to/dest_dir/")
        print("\n  3. File to file (rename):")
        print("     python hardlinker.py /path/to/source_file.txt /path/to/dest_file.txt")
        sys.exit(1)

    src = sys.argv[1]
    dest = sys.argv[2]

    create_hardlinks(src, dest)

if __name__ == "__main__":
    main()
