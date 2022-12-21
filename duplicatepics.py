"""
So I did a takeout from Google Photos which was about 33GB of data. But my Google Drive was still showing 13GB
used or something even though it should have been showing 5GB or something. So I did my Google Drive takeout as well.
Turned out Google Drive had a bunch of my pics too. Same ones at that. I'm not sure why or how that is. Probably
due to some old setting or something where Google wanted Google Photos to appear on Google Drive as well. Its kinda
weird but whatever. So this script is to find duplicates, find the one which is better in quality and keep that one
and delete the other one.
"""
import os
from os import path
from PIL import Image

# folderPath = input("Enter your value: ")
# print(folderPath)

for subdir, dirs, files in os.walk("/Volumes/WarpDrive/Google Drive/Takeout/Drive/Google Photos"):
    for file in files:
        # print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        for subdir2, dirs2, files2 in os.walk("/Volumes/WarpDrive/Google Photos/Takeout/Google Photos"):
            for file2 in files2:
                filepath2 = subdir2 + os.sep + file2

                if file == file2 and file.endswith(".jpg"):
                    print(filepath)
                    print(filepath2)
                    size1 = os.stat(filepath).st_size
                    size2 = os.stat(filepath2).st_size

                    sizeSame = size1 == size2
                    print("size = " + str(sizeSame))

                    if not sizeSame:
                        if size1 > size2:
                            print("drive")
                        else:
                            print("photos")

                    isSame = open(filepath, "rb").read() == open(filepath2, "rb").read()
                    print("same = " + str(isSame))

                    with Image.open(filepath) as img:
                        width, height = img.size
                    with Image.open(filepath2) as img2:
                        width2, height2 = img2.size
                    sameRes = width == width2 and height == height2
                    print("res = " + str(sameRes))
                    print("\n")
