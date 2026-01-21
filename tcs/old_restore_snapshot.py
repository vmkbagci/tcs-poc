import os
from pathlib import Path

def extract_tcs_poc(input_filename):
    """
    Parses a snapshot file and extracts files into their respective directories.
    Pattern:
    filePath + fileName
    filecontent
    <empty-line>
    """
    if not os.path.exists(input_filename):
        print(f"Error: {input_filename} not found.")
        return

    with open(input_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_file_path = None
    current_content = []
    file_count = 0

    for line in lines:
        # The sources indicate all paths start with the root 'tcs-poc/'
        # Examples: tcs-poc/tcs-api/pyproject.toml [3] or 
        # tcs-poc/tcs-api/src/trade_api/main.py [1]
        if line.strip().startswith('tcs-poc/'):
            # If we were processing a file, save it before starting the next one
            if current_file_path:
                save_extracted_file(current_file_path, current_content)
                file_count += 1

            current_file_path = line.strip()
            current_content = []
            print(f"Processing: {current_file_path}")
        else:
            # Accumulate content lines for the current file
            current_content.append(line)

    # Save the final file in the snapshot
    if current_file_path:
        save_extracted_file(current_file_path, current_content)
        file_count += 1

    print(f"\nSuccessfully extracted {file_count} files.")

def save_extracted_file(file_path, content_lines):
    """Creates directories and writes content to the file path."""
    # Create the folder structure automatically
    # Examples include: tcs-poc/tcs-api/templates/v1/core/ [4]
    path_obj = Path(file_path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Join the lines and strip the trailing empty line mandated by the format
    content = "".join(content_lines).strip()

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # If the file is a shell script, ensure it is executable (useful for Pop_OS)
    # Examples: tcs-poc/tcs-api/run-api.sh [5] or setup.sh [6]
    if file_path.endswith('.sh'):
        os.chmod(file_path, 0o755)

if __name__ == "__main__":
    # Ensure 'snapshot.txt' is in the same directory as this script
    extract_tcs_poc('snapshot.txt')

