import os

def get_directory_files(directory: str = '.') -> dict:
    """
    Retrieve a dictionary of files in a specified directory and its subdirectories.

    Args:
        directory (str): The path of the directory to search. Defaults to the current directory.

    Returns:
        dict: A dictionary where keys are directory paths and values are lists of file details,
              each containing the file name and size.
    """
    files_by_directory = {}  # Initialize a dictionary to hold files organized by directory
    for root, _, files in os.walk(directory):  # Walk through the directory tree
        file_details = []  # Initialize a list to hold details of files in the current directory
        for filename in files:  # Iterate through each file in the current directory
            file_path = os.path.join(root, filename)  # Construct the full file path
            file_size = os.path.getsize(file_path)  # Get the size of the file
            # Append a dictionary with file name and size to the list
            file_details.append({'name': filename, 'size': file_size})
        files_by_directory[root] = file_details  # Add the list of file details to the dictionary
    return files_by_directory  # Return the dictionary of files organized by directory

if __name__ == "__main__":
    # Prompt the user for a directory path, defaulting to the current directory if none is provided
    path = input("Enter the directory path (default is current directory):\n") or '.'
    files_info = get_directory_files(path)  # Get the files information from the specified directory
    print(files_info)  # Print the dictionary of files and their sizes

