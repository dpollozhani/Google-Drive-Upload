from os.path import realpath, exists, join, isfile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def abs_path_from_user_input(start_path):
    if start_path[:1] == '/':
        path_type = "absolute"
    else:
        path_type = "relative"
    if path_type != "absolute":
        start_path = realpath(start_path)
    return start_path

def abs_path_from_local_dir(directory, content):
    abs_path = realpath(join(directory, content))    
    return abs_path

def sort_files_and_dirs(curr_path, files_and_dirs):
    files = []
    dirs = []
    for file_dir in files_and_dirs:
        abs_path = abs_path_from_local_dir(curr_path, file_dir)
        if check_file_or_dir(abs_path) == "file":
            files.append(file_dir)
        else:
            dirs.append(file_dir)
    files.sort()
    dirs.sort()
    combined = []
    for f in files:
        combined.append(f)
    for d in dirs:
        combined.append(d)
    return combined         

def check_file_or_dir(path):
    if not exists(path):
        print("ERROR: PATH IS NOT VALID: " + path)
        return False
    else:
        if isfile(path):
            return "file"
        else:
            return "dir"


def is_valid_dir(path):
    if exists(path):
        # the path is a valid path
        if not isfile(path):
            # its a valid directory
            return True
        else:
            # its a valid file, but we want directories
            return False
    else:
        # the path doesnt exist
        return False

#def authenticate():
#    """ 
#		Authenticate to Google API
#	"""
#    gauth = GoogleAuth()
    
#    return GoogleDrive(gauth)