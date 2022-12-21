import os
import time
from os import path
from PIL import Image

# folderPath = input("Enter your value: ")
# print(folderPath)

for subdir, dirs, files in os.walk("/Volumes/WarpDrive/Google Drive/Takeout/Drive/Google Photos"):
    for file in files:
        # print os.path.join(subdir, file)
        filepath = subdir + os.sep + file
        cTime = os.stat(filepath).st_birthtime
        timeToShow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cTime))
        print(filepath)
        print(str(timeToShow))
