import os

def get_directory_files(directory: str = '.') -> dict:
    files_by_directory = {}
    for root, _, files in os.walk(directory):
        file_details = []
        for filename in files:
            file_path = os.path.join(root, filename)
            file_size = os.path.getsize(file_path)
            file_details.append({'name': filename, 'size': file_size})
        files_by_directory[root] = file_details
    return files_by_directory

if __name__ == "__main__":
    path = input("Enter the directory path (default is current directory):\n") or '.'
    files_info = get_directory_files(path)
    print(files_info)
