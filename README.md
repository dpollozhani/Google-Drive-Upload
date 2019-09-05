# Google-Drive-Upload
This repo contains a program that enables you to upload full directories from your local environment to your Google Drive account, preserving the existing tree structure, with possibilities to create automatic back-ups and transfer existing Google Drive folder permissions.

## Dependencies
Python 3.6 or later recommended.
- The program is heavily dependant on the PyDryve library (a wrapper for the Google Drive API), which needs to be installed e.g via `pip install pydrive` (check out more details on the library's web site).
- Other than that only standard Python libraries are used. Using Anaconda should provide all that is needed.

## Short walkthrough

The `drive_folder_manager.py` file contains the bulk of the content of the program. First there is an authentication function which creates an authenticated Google Service instance that in turn will be used to initialize a Google Drive instance, which is used for managing all Google Drive content. 

The authentication is configured solely via the `settings.yaml` file, which can be modified. The given configurations are that the user credentials are saved, meaning that only a one-time authentication is needed. 

In the `drive_folder_manager.py` file also reside the two classes that make this whole thing work: Dyrectory and DryveFolder (cheesy names, I know). The former is responsible for mirroring the tree structure in a given path to the Google Drive environment; it recursively traverses the directory and uploads the content. The latter contains helper methods, e.g to get file/folder ids, add subfolders, backup content, get permissions and so forth. Permissions can be fed to the Dyrectory.create_google_drive_tree() method so that the (at this time) top level permissions are passed from existing folders to those that are to be uploaded. Both classes also make use of additional utility functions which reside in `utility_functions.py`.

Note that the main file, `gdrive_upload_main.py` is centered around user command inputs, but this can be changed to suit a more streamlined approach. For instance it could be used for periodically uploading and backing up the same directory by scheduling the program to run via any conveniently available task scheduler.

## Thanks
This could not have been completed without the help of the wonderful community. As a matter of fact, this repo is not a result of one person, but a collection of ideas and code from users that were kind enough to share the results of their craftsmanship on Stackoverflow and forums of the like. I take no credit other than bringing these different parts to a (somewhat) united form. Thank you.
