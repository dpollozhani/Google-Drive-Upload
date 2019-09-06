import utility_functions as uf
from os import listdir
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import googleapiclient.errors
from sys import exit
import ast
from datetime import date


def authenticate():
    """ 
		Authenticate to Google API. Based on the settings.yaml file.
	"""
    gauth = GoogleAuth()
    
    return GoogleDrive(gauth)
###############################################################
class DryveFolder():
    """ Class that makes it easier to handle google drive folders """

    def __init__(self, google_service, parent_dir_id, folder_name):
        """ Initialize Dryvefolder instance """
        self.google_service = google_service #pydrive.drive.GoogleDrive instance!
        self.parent_dir_id = parent_dir_id
        self.folder_name = folder_name 

    def get_folder_id(self):
        """ 
            Check if destination folder exists and return it's ID
        """

        # Auto-iterate through all files in the parent folder.
        try:
            file_list_drive = self.google_service.ListFile(
                {'q': f"'{self.parent_dir_id}' in parents and trashed=false"}
            ).GetList()
        # Exit if the parent folder doesn't exist
        except googleapiclient.errors.HttpError as err:
            # Parse error message
            message = ast.literal_eval(err.content)['error']['message']
            if message == 'File not found: ':
                print(message + self.folder_name)
                exit(1)
            # Exit with stacktrace in case of other error
            else:
                raise

        # Find the the destination folder in the parent folder's files
        for file in file_list_drive:
            if file['title'] == self.folder_name:
                file_id = file['id']
                return file_id

    def get_content(self, recursive=True, parent=None, calls=1):
        
        """ 
            Iterate through content and returns a list with it. If a folder is found, it is recursively traversed, 
            given that recursive==True, else only first level is returned.
        """
        content = []
    
        if calls == 1:
            parent = self.get_folder_id()
        
        file_list_drive = self.google_service.ListFile(
                {'q': f"'{parent}' in parents and trashed=false"}
            ).GetList()

        for file in file_list_drive:
            if recursive:
                if file['mimeType'] == 'application/vnd.google-apps.folder': #if subfolder
                    content.append({'id': file['id'], 'title': file['title'], 'list': self.get_content(parent=file['id'], calls=+1)})
                else:
                    content.append({'id': file['id'], 'title': file['title'], 'title1': file['alternateLink']})
            else:
                content.append({'id': file['id'], 'title': file['title']})

        return content

    def isempty(self):

        """ 
            Check whether folder folder_name is empty
        """
        file_list_drive = self.google_service.ListFile(
                {'q': f"'{self.get_folder_id()}' in parents and trashed=false"}
            ).GetList()
        
        content_list = [file['title'] for file in file_list_drive]

        if len(content_list) == 0:
            return True
        return False

    def add_folder(self, new_folder, root=True): 
        """ 
            Create new subfolder under root (self.parent_dir_id) or optionally under current folder (self.folder_name)
        """
        parent_id = self.parent_dir_id if root else self.get_folder_id()
        folder_metadata = {'title': new_folder,
            # Define the file type as folder 
            'mimeType': 'application/vnd.google-apps.folder',
            # ID of the parent folder 
            'parents': [{"kind": "drive#fileLink", "id": parent_id}]
        }

        file_list_drive = self.google_service.ListFile(
                {'q': f"'{parent_id}' in parents and trashed=false"}
            ).GetList()
        
        for file in file_list_drive:
            if file['title'] == new_folder:
                print('f{new_folder} already exists!')
                return file['id']

        folder = self.google_service.CreateFile(folder_metadata)
        folder.Upload()

        folder_id = folder['id']

        return folder_id

    def get_permissions(self):
        
        file_permissions={}

        file_list_drive = self.google_service.ListFile(
                {'q': f"'{self.get_folder_id()}' in parents and trashed=false"}
            ).GetList()
        
        for file in file_list_drive:
            file_permissions[file['title']] = file.GetPermissions()
            
        return file_permissions

    def delete_permissions(self):

        file_list_drive = self.google_service.ListFile(
                {'q': f"'{self.get_folder_id()}' in parents and trashed=false"}
            ).GetList()
        
        for file in file_list_drive:
            permissions = file.GetPermissions()
            for perm in permissions:
                if perm['role'] != 'owner':
                    print('Deleting', perm['id'])
                    file.DeletePermission(perm['id'])
            
    def backup_content(self):

        today_date = date.today()
        backup_folder_id = self.add_folder(f'{self.folder_name} backup {today_date}')
        
        print(f'Backing up to {self.folder_name} backup {today_date}...')
        
        files = self.google_service.auth.service.files() #the below functionality is not available/not efficient directly with PyDrive wrapper as of 190826
        
        for f in self.get_content(recursive=False):
            file = files.get(fileId=f['id'], 
                             fields='parents').execute()
            prev_parents = ','.join(p['id'] for p in file.get('parents'))
            file = files.update(fileId=f['id'], 
                                addParents = backup_folder_id, 
                                removeParents = prev_parents,
                                fields='id, parents').execute()
###############################################################
class Dyrectory():
    """ Class that enables you to upload a complete directory structure to google drive """

    def __init__(self, directory_path, DryveFolder_obj=None):
        """Initialize Dyrectory"""
        self.directory_path = directory_path
        self.DryveFolder_obj = DryveFolder_obj

    def create_google_drive_tree(self, google_drive_folder='', google_service=False, parent_dir_id='', file_permissions=''):
        
        """Creates the same tree in google drive that is in the Dyrectory
        object, with 'google_drive_folder' as the ROOT directory
        (== Dyrectory obj)
        Optionally add existing folder permissions for backup, using DryveFolder object.get_permissions()"""
        
        # google_drive_folder = name of the current directory
        # google_service = Google API resource
        # parent_dir_id = id of the parent dir on Google drive

        # create the files_and_dirs list in the current directory
        files_and_dirs = [files_and_dirs for files_and_dirs in listdir(self.directory_path)]            
        print(files_and_dirs)
        
        # sorts the files and dirs so their alphabetical and files come first
        files_and_dirs = uf.sort_files_and_dirs(self.directory_path, files_and_dirs)        
        
        # loop through files and directories, outputting if its a file or dir
        # if its a dir and full_tree==true, make a recursive call by creating 
        # new Directory instance then listing the contents of that as well
        for fd in files_and_dirs:
            abs_path = uf.abs_path_from_local_dir(self.directory_path, fd)
            if uf.check_file_or_dir(abs_path) == "file":
                # its a file
                # need to copy the file to Google Drive
                file_metadata = {"title": fd,
                                "parents": [{"kind": "drive#fileLink", "id": parent_dir_id}]}
                file = google_service.CreateFile(file_metadata)
                file.Upload()
            else:
                # its a directory
                # create the directory in google drive
                file_metadata = {'title': fd,
                                'mimeType': 'application/vnd.google-apps.folder',
                                'parents': [{"kind": "drive#fileLink", "id": parent_dir_id}]}
                file = google_service.CreateFile(file_metadata)
                file.Upload()
                
                #transfer permissions from existing google drive folders
                if isinstance(file_permissions, dict):
                    if file['title'] in list(file_permissions.keys()):
                        for perm in file_permissions[file['title']]:
                            user, role = perm['emailAddress'], perm['role']
                            if role != 'owner':
                                perm_type = 'user'
                                new_permission = {
                                        'value': user,
                                        'type': perm_type,
                                        'role': role
                                        }
                                file.InsertPermission(new_permission)
    
                print(f'Folder: {file}')
                
                # create a new Dyrectory obj with the current directory
                # which is a subdirectory of the current directory
                sub_dir = Dyrectory(abs_path)                
                # Recursively build tree inside the subdirectory
                sub_dir.create_google_drive_tree(
                    fd, 
                    google_service, 
                    file['id'])


        
        



    
        
        




