import os
import sys
import shutil
from datetime import datetime

def create_unique_destination_path(destination_dir: str, filename: str) -> str:
    
    # Split the filename into name and extension (e.g., 'config.ini' -> ('config', '.ini'))
    base_name, extension = os.path.splitext(filename)
    
    destination_path = os.path.join(destination_dir, filename)
    
    # Check if the file already exists in the destination
    if os.path.exists(destination_path):
        # File exists, generate a timestamp and insert it into the filename
        timestamp = datetime.now().strftime("_%Y%m%d_%H%M%S")
        new_filename = f"{base_name}{timestamp}{extension}"
        destination_path = os.path.join(destination_dir, new_filename)
        print(f"    [INFO] Conflict detected. Renaming to: {new_filename}")
        
    return destination_path

def backup_files(source_dir: str, destination_dir: str):
    print("-" * 50)
    print(f"Starting Backup Operation...")
    print(f"Source: {source_dir}")
    print(f"Destination: {destination_dir}")
    print("-" * 50)
    
    # --- 1. Validate Source Directory ---
    if not os.path.isdir(source_dir):
        print(f"❌ ERROR: Source directory not found: '{source_dir}'")
        return
        
    # --- 2. Validate and Create Destination Directory ---
    if not os.path.isdir(destination_dir):
        try:
            os.makedirs(destination_dir)
            print(f"✅ Created destination directory: '{destination_dir}'")
        except OSError as e:
            print(f"❌ ERROR: Could not create destination directory '{destination_dir}': {e}")
            return

    files_copied_count = 0
    
    try:
        # Iterate over all entries in the source directory
        for item in os.listdir(source_dir):
            source_path = os.path.join(source_dir, item)
            
            if os.path.isfile(source_path):
                
                destination_path = create_unique_destination_path(destination_dir, item)
                
                shutil.copy2(source_path, destination_path) # copy2 attempts to preserve metadata
                
                print(f"  --> Copied: {item}")
                files_copied_count += 1

    except Exception as e:
        print(f"❌ ERROR: An unexpected error occurred during copy: {e}")
        return

    print("-" * 50)
    print(f"✅ Backup complete! Total files copied: {files_copied_count}")
    print("-" * 50)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <source_directory> <destination_directory>")
        print("\nExample: python backup.py /var/www/html/config /mnt/backups/web-config")
        sys.exit(1)
        
    # Extract arguments
    source_path = sys.argv[1]
    destination_path = sys.argv[2]
    
    backup_files(source_path, destination_path)