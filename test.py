from drive_folder_manager import Dyrectory, DryveFolder
from drive_folder_manager import authenticate as google_auth
import utility_functions as uf
from pathlib import Path
import os

print(os.listdir(str(Path.cwd())))