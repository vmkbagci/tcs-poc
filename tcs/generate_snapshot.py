import os
from pathlib import Path

def generate_encapsulated_snapshot(root_folder, output_filename="project_snapshot.txt"):
    """
    Recursively finds all files and appends them to a snapshot file.
    
    Encapsulation Pattern:
    <File--- filePath + fileName --->
    fileContent
    <empty-line>
    """
    root_path = Path(root_folder).resolve()
    
    if not root_path.is_dir():
        print(f"Error: {root_folder} is not a directory.")
        return

    print(f"Creating snapshot of: {root_path}")
    
    # We open in 'w' mode to start fresh, or 'a' if you strictly want to append
    with open(output_filename, 'w', encoding='utf-8') as snapshot:
        file_count = 0
        
        # rglob('*') recursively finds all files and directories
        for path in root_path.rglob('*'):
            if path.is_file():
                # Avoid self-referencing the snapshot file if it's in the same folder
                if path.name == output_filename:
                    continue
                
                try:
                    # Calculate relative path to keep the root name (e.g., tcs-poc/...)
                    # as seen in the sources [1-3]
                    relative_path = path.relative_to(root_path.parent)
                    
                    # Write the requested encapsulation tag
                    snapshot.write(f"<File--- {relative_path} --->\n")
                    
                    # Read and write the content
                    # 'errors=replace' handles any non-UTF8 characters in binary files
                    with open(path, 'r', encoding='utf-8', errors='replace') as f:
                        snapshot.write(f.read())
                    
                    # Add trailing empty line as per the pattern
                    snapshot.write("\n\n")
                    
                    print(f"Archived: {relative_path}")
                    file_count += 1
                    
                except Exception as e:
                    print(f"Error reading {path}: {e}")

    print(f"\nSuccessfully created {output_filename} with {file_count} files.")

if __name__ == "__main__":
    # You can change 'tcs-poc' to the folder you wish to process
    target_folder = input("Enter the name of the folder to snapshot: ").strip()
    generate_encapsulated_snapshot(target_folder)

