import os
import sys

# Define a list of common video file extensions
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.mpeg', '.mpg', '.webm'}

def find_video_files_with_no_hardlinks(target_directory):
    if not os.path.isdir(target_directory):
        print(f"Error: {target_directory} is not a valid directory.")
        return

    print(f"Checking for video files with no hardlinks in '{target_directory}'...\n")

    for root, dirs, files in os.walk(target_directory):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Check if the file has a video extension
            if os.path.splitext(filename)[1].lower() in VIDEO_EXTENSIONS:
                try:
                    # Get file stats
                    file_stat = os.stat(file_path)

                    # Check the number of hard links (st_nlink)
                    if file_stat.st_nlink == 1:
                        print(f"Video file with no hardlinks: {file_path}")
                
                except FileNotFoundError:
                    print(f"Warning: File not found (possibly a broken symlink): {file_path}")
                except Exception as e:
                    print(f"Error checking {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_no_hardlinks.py <target_directory>")
        sys.exit(1)

    target_directory = sys.argv[1]
    find_video_files_with_no_hardlinks(target_directory)
