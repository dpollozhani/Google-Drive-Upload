from drive_folder_manager import Dyrectory, DryveFolder
from drive_folder_manager import authenticate as google_auth
import utility_functions as uf
from pathlib import Path

# specify the start path
start_path = Path(input('Enter source path:'))
print(f'START PATH: {start_path}')

# specify Drive folder (in this verison, must be under root) and create a google drive service resource upon authentication
google_drive_folder = input('Enter Drive folder name:')
google_service = google_auth()

# create a DryveFolder object with given name, under root Drive folder
drive_folder = DryveFolder(google_service, 'root', google_drive_folder)
# gets drive instance's parent_dir_id attribute
google_drive_folder_id = drive_folder.get_folder_id()

# if folder has existing content, extract folder permissions, create a backup, and empty
if not drive_folder.isempty():
    google_drive_folder_permissions = drive_folder.get_permissions()
    drive_folder.backup_content()
else: 
    google_drive_folder_permissions=''

# create a directory object with start path
start_directory = Dyrectory(start_path)

# create the directory tree on google drive
start_directory.create_google_drive_tree(
    google_drive_folder, 
    google_service, 
    google_drive_folder_id,
    google_drive_folder_permissions)

print("FINISHED")