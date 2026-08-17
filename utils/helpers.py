import os

def get_unique_filename(filepath):
    """
    Checks if a file exists. If it does, appends _1, _2, etc. to the filename
    before the extension to ensure it is unique.
    """
    if not os.path.exists(filepath):
        return filepath
        
    directory, filename = os.path.split(filepath)
    name, ext = os.path.splitext(filename)
    
    counter = 1
    while True:
        new_name = f"{name}_{counter}{ext}"
        new_filepath = os.path.join(directory, new_name)
        if not os.path.exists(new_filepath):
            return new_filepath
        counter += 1
