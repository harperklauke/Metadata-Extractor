#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from os import walk 
from PIL import Image #Opens images and retrieves exif
from PIL.ExifTags import TAGS #Convert exif tags from digits to names
import csv 
from os.path import join 

import datetime
from fractions import Fraction


# In[40]:


#image_filepath = "/Users/harpe/OneDrive/Documents/HARPER STUFF/CCBER-capstone/All"
#csvfile = 'exifdatatest.csv'


# In[66]:


def create_lookups():
    lookups = {}

    lookups["MeteringMode"] = ("Undefined",
                                 "Average",
                                 "Center-weighted average",
                                 "Spot",
                                 "Multi-spot",
                                 "Multi-segment",
                                 "Partial")

    lookups["ExposureProgram"] = ("Undefined",
                                    "Manual",
                                    "Program AE",
                                    "Aperture-priority AE",
                                    "Shutter speed priority AE",
                                    "Creative (Slow speed)",
                                    "Action (High speed)",
                                    "Portrait ",
                                    "Landscape",
                                    "Bulb")

    lookups["ResolutionUnit"] = ("",
                                   "Undefined",
                                   "Inches",
                                   "Centimetres")

    lookups["Orientation"] = ("",
                               "Horizontal",
                               "Mirror horizontal",
                               "Rotate 180",
                               "Mirror vertical",
                               "Mirror horizontal and rotate 270 CW",
                               "Rotate 90 CW",
                               "Mirror horizontal and rotate 90 CW",
                               "Rotate 270 CW")
    
    lookups["ColorSpace"] = ("","sRBG","Adobe RGB")
    
    lookups["WhiteBalance"] = ("Auto","Manual")
    
    lookups["ExposureMode"] = ("Auto","Manual","Auto bracket")
    
    lookups["YCbCrPositioning"] = ("","Centered","Co-sited")
    
    lookups["SceneCaptureType"] = ("Standard","Landscape","Portrait","Night","Other")
    
    lookups["Flash"] = ("No Flash","Off, Did not fire","No flash Function")
    
    return lookups


# In[68]:


def process_exif_dict(exif_dict): # defines function to make exif info human-readable
    date_format = "%Y:%m:%d %H:%M:%S"

    lookups = create_lookups()
    
    # Reformatting from tag encodings:
    for key in exif_dict:
        if key in lookups:
            try:
                exif_dict[key] = lookups[key][exif_dict[key]] # basic lookup conversions
            except LookupError:
                pass
    
    # Reformatting manually:
    try:
        exif_dict["DateTimeOriginal"] = datetime.datetime.strptime(exif_dict["DateTimeOriginal"], date_format)
        exif_dict["DateTimeDigitized"] = datetime.datetime.strptime(exif_dict["DateTimeDigitized"], date_format)
    except LookupError:
        pass
    try:
        exif_dict["FNumber"] = "f/{}".format(exif_dict["FNumber"])
    except LookupError:
        pass
    try:
        exif_dict["MaxApertureValue"] = float(exif_dict["MaxApertureValue"])
        exif_dict["MaxApertureValue"] = "f/{:2.1f}".format(exif_dict["MaxApertureValue"])
    except LookupError:
        pass
    try:
        exif_dict["FocalLength"] = float(exif_dict["FocalLength"])
        exif_dict["FocalLength"] = "{}mm".format(exif_dict["FocalLength"])
    except LookupError:
        pass
    try:
        exif_dict["FocalLengthIn35mmFilm"] = "{}mm".format(exif_dict["FocalLengthIn35mmFilm"])
    except LookupError:
        pass
    try:
        exif_dict["ExposureBiasValue"] = format(float(exif_dict["ExposureBiasValue"]),".2f")
        exif_dict["ExposureBiasValue"] = "{} EV".format(exif_dict["ExposureBiasValue"])
    except LookupError:
        pass
    
    return exif_dict


# In[42]:


exifdataobjs = ["ExifVersion","FNumber","MaxApertureValue","DateTimeOriginal", "DateTimeDigitized","DateTime","BrightnessValue","MeteringMode","Flash",
    "FocalLength","FocalLengthIn35mmFilm","ColorSpace","SceneCaptureType","ExifImageWidth","ExifImageHeight","Make","Model","Orientation","YCbCrPositioning", 
     "ShutterSpeedValue","ExposureTime","ExposureMode","ExposureBiasValue","XResolution","YResolution","ResolutionUnit","ISOSpeedRatings","ExifOffset",
    "WhiteBalance" ,"Software"]


# In[62]:


def get_exif(fn): #Defining a function that opens an image, retrieves the exif data, corrects the exif tags from digits to names and puts the data into a dictionary
    i = Image.open(fn)   
    info = i._getexif()
    if info: 
        ret = {TAGS.get(tag, tag): value for tag, value in info.items()}
        exif_processed = process_exif_dict(ret)
        return exif_processed
    else: 
        res = dict(zip(exifdataobjs, [None]*len(exifdataobjs)))
        print("Sorry", fn, "has no exif data.")
        return res


# In[69]:


if __name__ == "__main__":
    image_filepath = sys.argv[1] # establish image file/folder location
    
    if os.path.exists(image_filepath):
        
        file_input = input("Name of CSV output file:") # prompt user to provide intended filename
        if file_input.endswith(('.csv','.CSV')) == False:
            file_input += '.csv'   # if name does not end with .csv, append to filename
        csvfile = file_input # assign input to csvfile
        
        num_lists = int(len(exifdataobjs))
        lists = [[] for i in range(num_lists+1)]
        lists[0].extend(Filenames)
        
        Paths = [join(root, f).replace(os.sep,"/") for root, dirs, files in walk(image_filepath, topdown=True) for f in files if f.endswith(('.JPG' ,'.jpg'))] #Creates list of paths for images
        Filenames = [f for root, dirs, files in walk(image_filepath, topdown=True) for f in files if f.endswith(('.JPG' ,'.jpg'))] #Creates list of filenames for images
        ExifData = list(map(get_exif, Paths)) # might have to iterate over files differently
        
        print("Processing images...")
        i = 1
        for obj in exifdataobjs:
            for j in ExifData:
                if obj in j: # trying to get rid of na error
                    lists[i].append(j[obj])
                else:
                    lists[i].append('na')
            i+=1
            if i == (len(exifdataobjs)+1):
                break
        exifdataobjs.insert(0, "File")
        
        print("Writing csv...")
        zipped = zip(*lists) #Combines the lists to be written into a csv.

        with open(csvfile, "w", newline='') as f: #Writes a csv-file with the exif data
            writer = csv.writer(f)
            writer.writerow(exifdataobjs) # add exifdataobjs
            for row in zipped:
                writer.writerow(row)
        print(csvfile,"successfully created.")


# In[70]:


# iterate through diff exif variables and to prepare data for csv
# num_lists = int(len(exifdataobjs))
# lists = [[] for i in range(num_lists+1)]
# lists[0].extend(Filenames)

# i = 1
# for obj in exifdataobjs:
#     for j in ExifData:
#         if obj in j: # trying to get rid of na error
#             lists[i].append(j[obj])
#         else:
#             lists[i].append('na')
#     i+=1
#     if i == (len(exifdataobjs)+1):
#         break
# exifdataobjs.insert(0, "File")


# In[71]:


# zipped = zip(*lists) #Combines the lists to be written into a csv.

# with open(csvfile, "w", newline='') as f: #Writes a csv-file with the exif data
#     writer = csv.writer(f)
#     writer.writerow(exifdataobjs) # add exifdataobjs
#     for row in zipped:
#         writer.writerow(row)

