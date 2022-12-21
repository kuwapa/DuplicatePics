"""
This script was meant to do what temp.py did for me.
"""

import os
import json
from os import path
from datetime import datetime as _datetime
import piexif as _piexif
from fractions import Fraction  # piexif requires some values to be stored as rationals
import math
from loguru import logger

# folderPath = input("Enter your value: ")
# print(folderPath)

# current file extensions
# ['', '.json', '.jpg', '.mp4', '.m4v', '.png', '.MP4', '.JPG', '.jpeg', '.3gp', '.gif', '.MOV', '.PNG']
# all JSONs contain photoTakenTime and all of those contain timestamp value

TAG_DATE_TIME_ORIGINAL = _piexif.ExifIFD.DateTimeOriginal
TAG_DATE_TIME_DIGITIZED = _piexif.ExifIFD.DateTimeDigitized
TAG_DATE_TIME = 306

fileExtensions = [".json",
                  '.jpg.json', '.jpg(1).json', '.jpg(2).json', '.jpg(3).json', '.jpg(4).json', '.jpg(5).json',
                  '.mp4.json', '.mp4(1).json', '.mp4(2).json', '.mp4(3).json', '.mp4(4).json',
                  '.m4v.json', '.m4v(1).json',
                  '.jp.json',
                  '.png.json', '.png(1).json', '.PNG.json',
                  '.MP4.json', '.JPG.json', '.3gp.json', '.j.json',
                  '.jpeg.json', '.gif.json'
                  ]


def fix_metadata(file1, google_json):
    # logger.info(file)
    try:
        date = get_date_str_from_json(google_json)
        set_file_geo_data(file1, google_json)
        set_file_exif_date(file1, date)
        set_creation_date_from_str(file1, date)
        return True
    except FileNotFoundError as e:
        logger.debug(e)


def get_date_str_from_json(json1):
    return _datetime.fromtimestamp(
        int(json1['photoTakenTime']['timestamp'])
    ).strftime('%Y:%m:%d %H:%M:%S')


def set_file_geo_data(file11, json11):
    """
    Reads the geoData from google and saves it to the EXIF. This works assuming that the geodata looks like -100.12093, 50.213143. Something like that.

    Written by DalenW.
    """

    # prevents crashes
    try:
        exif_dict = _piexif.load(str(file11))
    except:
        exif_dict = {'0th': {}, 'Exif': {}}

    # converts a string input into a float. If it fails, it returns 0.0
    def _str_to_float(num):
        if type(num) == str:
            return 0.0
        else:
            return float(num)

    # fallbacks to GeoData Exif if it wasn't set in the photos editor.
    # https://github.com/TheLastGimbus/GooglePhotosTakeoutHelper/pull/5#discussion_r531792314
    longitude = _str_to_float(json11['geoData']['longitude'])
    latitude = _str_to_float(json11['geoData']['latitude'])
    altitude = _str_to_float(json11['geoData']['altitude'])

    # Prioritise geoData set from GPhotos editor. If it's blank, fall back to geoDataExif
    if longitude == 0 and latitude == 0:
        longitude = _str_to_float(json11['geoDataExif']['longitude'])
        latitude = _str_to_float(json11['geoDataExif']['latitude'])
        altitude = _str_to_float(json11['geoDataExif']['altitude'])

    # latitude >= 0: North latitude -> "N"
    # latitude < 0: South latitude -> "S"
    # longitude >= 0: East longitude -> "E"
    # longitude < 0: West longitude -> "W"

    if longitude >= 0:
        longitude_ref = 'E'
    else:
        longitude_ref = 'W'
        longitude = longitude * -1

    if latitude >= 0:
        latitude_ref = 'N'
    else:
        latitude_ref = 'S'
        latitude = latitude * -1

    # referenced from https://gist.github.com/c060604/8a51f8999be12fc2be498e9ca56adc72
    gps_ifd = {
        _piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0)
    }

    # skips it if it's empty
    if latitude != 0 or longitude != 0:
        gps_ifd.update({
            _piexif.GPSIFD.GPSLatitudeRef: latitude_ref,
            _piexif.GPSIFD.GPSLatitude: degToDmsRational(latitude),

            _piexif.GPSIFD.GPSLongitudeRef: longitude_ref,
            _piexif.GPSIFD.GPSLongitude: degToDmsRational(longitude)
        })

    if altitude != 0:
        gps_ifd.update({
            _piexif.GPSIFD.GPSAltitudeRef: 1,
            _piexif.GPSIFD.GPSAltitude: change_to_rational(round(altitude))
        })

    gps_exif = {"GPS": gps_ifd}
    exif_dict.update(gps_exif)

    try:
        _piexif.insert(_piexif.dump(exif_dict), str(file11))
    except Exception as e:
        logger.debug("Couldn't insert geo exif!")
        # local variable 'new_value' referenced before assignment means that one of the GPS values is incorrect
        logger.debug(e)


# got this here https://github.com/hMatoba/piexifjs/issues/1#issuecomment-260176317
def degToDmsRational(degFloat):
    min_float = degFloat % 1 * 60
    sec_float = min_float % 1 * 60
    deg = math.floor(degFloat)
    deg_min = math.floor(min_float)
    sec = round(sec_float * 100)

    return [(deg, 1), (deg_min, 1), (sec, 100)]


def change_to_rational(number):
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return f.numerator, f.denominator


def set_file_exif_date(fileK, creation_date):
    try:
        exif_dict = _piexif.load(str(fileK))
    except:  # Sorry but Piexif is too unpredictable
        exif_dict = {'0th': {}, 'Exif': {}}

    creation_date = creation_date.encode('UTF-8')
    exif_dict['0th'][TAG_DATE_TIME] = creation_date
    exif_dict['Exif'][TAG_DATE_TIME_ORIGINAL] = creation_date
    exif_dict['Exif'][TAG_DATE_TIME_DIGITIZED] = creation_date

    try:
        _piexif.insert(_piexif.dump(exif_dict), str(fileK))
    except Exception as e:
        logger.debug("Couldn't insert exif!")
        logger.debug(e)


def set_creation_date_from_str(fileM, str_datetime):
    try:
        # Turns out exif can have different formats - YYYY:MM:DD, YYYY/..., YYYY-... etc
        # God wish that americans won't have something like MM-DD-YYYY
        # The replace ': ' to ':0' fixes issues when it reads the string as 2006:11:09 10:54: 1.
        # It replaces the extra whitespace with a 0 for proper parsing
        str_datetime = str_datetime.replace('-', ':').replace('/', ':').replace('.', ':').replace('\\', ':').replace(
            ': ', ':0')[:19]
        timestamp = _datetime.strptime(
            str_datetime,
            '%Y:%m:%d %H:%M:%S'
        ).timestamp()
        os.utime(fileM, (timestamp, timestamp))
    except Exception as e:
        logger.debug('Error setting creation date from string:')
        logger.debug(e)
        raise ValueError(f"Error setting creation date from string: {str_datetime}")


for subdir, dirs, files in os.walk("/Users/abhimanyu/Desktop/2017-10-03"):
    for file in files:
        # print os.path.join(subdir, file)
        filepath = subdir + os.sep + file

        filename, file_extension = os.path.splitext(filepath)

        # File is not Json
        if file_extension != ".json":
            # Checking is the corresponding JSON file for this photo exists or not
            # looping through all the .json extensions I found. Google Photos added .jp, .jpeg etc between the file
            # name and the .json extension so all json files not not simply filename + .json
            for ext in fileExtensions:
                jsonFileName = filename + ext
                if path.exists(jsonFileName):
                    # Checking if the JSON has the title same as the file name
                    with open(jsonFileName) as f:
                        data = json.load(f)
                        file_name = os.path.basename(filepath)
                        if data['title'] == file_name:
                            if fix_metadata(filepath, data):
                                os.remove(jsonFileName)
                    break
