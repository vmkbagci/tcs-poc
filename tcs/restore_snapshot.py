import os
import re
from pathlib import Path

def extract_from_encapsulated_snapshot(input_filename):
    """
    Parses a snapshot file with encapsulated headers and extracts files.
    Pattern:
    <File--- filePath + fileName --->
    fileContent
    <empty-line>
    """
    if not os.path.exists(input_filename):
        print(f"Error: {input_filename} not found.")
        return

    # Regular expression to find the encapsulated path
    # Matches: <File--- path/to/file.ext --->
    header_pattern = re.compile(r"^<File--- (.*) --->$")

    with open(input_filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_file_path = None
    current_content = []
    file_count = 0

    for line in lines:
        stripped_line = line.strip()
        match = header_pattern.match(stripped_line)

        if match:
            # If we were already processing a file, save it before starting the next
            if current_file_path:
                save_file(current_file_path, current_content)
                file_count += 1

            # Extract the new path from the regex group
            current_file_path = match.group(1).strip()
            current_content = []
            print(f"Extracting: {current_file_path}")
        else:
            # Add line to content if we have an active file path
            if current_file_path is not None:
                current_content.append(line)

    # Save the final file in the snapshot
    if current_file_path:
        save_file(current_file_path, current_content)
        file_count += 1

    print(f"\nFinished: Extracted {file_count} files into their proper folders.")

def save_file(file_path, content_lines):
    """Creates directory tree and writes content to the target path."""
    path_obj = Path(file_path)
    
    # Create parent directories (e.g., tcs-poc/tcs-api/src/trade_api/validation/)
    path_obj.parent.mkdir(parents=True, exist_ok=True)

    # Join lines and remove the trailing empty line from the snapshot format
    content = "".join(content_lines).rstrip()

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Set executable permissions for shell scripts found in the TCS project
    # Examples: run-api.sh, setup.sh, docker-setup.sh
    if file_path.endswith('.sh'):
        os.chmod(file_path, 0o755)

if __name__ == "__main__":
    # Update this filename if your snapshot is named differently
    extract_from_encapsulated_snapshot('project_snapshot.txt')

