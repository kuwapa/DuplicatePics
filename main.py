"""
This script was for deleting duplicates which had (1) at the end in the Google Photos
takeout.
"""

import os
from os import path

# folderPath = input("Enter your value: ")
# print(folderPath)

for subdir, dirs, files in os.walk("/Users/abhimanyu/Google Drive/Photos/Family Photo Collection"):
    for file in files:
        # print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        if filepath.endswith(" (1).JPG") or filepath.endswith(" (1).jpg"):
            originalFilePath = filepath.replace(" (1)", "")
            if path.exists(originalFilePath) and open(filepath, "rb").read() == open(originalFilePath, "rb").read():
                print(filepath)
                os.remove(filepath)
