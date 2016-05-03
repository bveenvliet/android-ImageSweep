#!/usr/bin/env python

"""ImageSweep.py: Deletes unnecessary image drawables.."""

__author__      = "Josh Ruesch"
__copyright__   = "Copyright 2014, Instructure Inc"

import os
import re
import sys

#Global variables.
used_drawable_files = set()
used_mipmap_files = set()
files_deleted = 0
mega_bytes_deleted = 0

#Naive method to determine if a directory is an android /res folder.
def isResourceRoot(directory):
  return (
  (os.path.exists(directory+"/drawable"))         or
  (os.path.exists(directory+"/drawable-ldpi"))    or
  (os.path.exists(directory+"/drawable-mdpi"))    or
  (os.path.exists(directory+"/drawable-hdpi"))    or
  (os.path.exists(directory+"/drawable-xhdpi"))   or
  (os.path.exists(directory+"/drawable-xxhdpi"))  or
  (os.path.exists(directory+"/drawable-xxxhdpi")) or
  (os.path.exists(directory+"/mipmap"))           or
  (os.path.exists(directory+"/mipmap-ldpi"))      or
  (os.path.exists(directory+"/mipmap-mdpi"))      or
  (os.path.exists(directory+"/mipmap-hdpi"))      or
  (os.path.exists(directory+"/mipmap-xhdpi"))     or
  (os.path.exists(directory+"/mipmap-xxhdpi")))

#We only want to remove unused PICTURES (pngs)
def addDrawableFile(fileName):
  fileName = fileName.replace("R.drawable.", "").replace("@drawable/","")
  used_drawable_files.add(fileName)

def addMipmapFile(fileName):
  fileName = fileName.replace("R.mipmap.", "").replace("@mipmap/","")
  used_mipmap_files.add(fileName)

#Check to see what drawable resources are referenced in this function.
def checkFileForDrawableResources(fileAsString):
  file = open(fileAsString, 'r')
  contents = file.read()
  file.close()

  #Handle drawable code files.
  drawablePattern = re.compile('R.drawable.[a-zA-Z0-9_]*')
  drawableResults = drawablePattern.findall(contents)
  for result in drawableResults:
    addDrawableFile(result)

  #Handle drawable layout files.
  drawablePattern = re.compile('@drawable/[a-zA-Z0-9_]*')
  drawableResults = drawablePattern.findall(contents)
  for result in drawableResults:
    addDrawableFile(result)

#Check to see what mipmap resources are referenced in this function.
def checkFileForMipmapResources(fileAsString):
  file = open(fileAsString, 'r')
  contents = file.read()
  file.close()

  #Handle mipmap code files.
  mipmapPattern = re.compile('R.mipmap.[a-zA-Z0-9_]*')
  mipmapResults = mipmapPattern.findall(contents)
  for result in mipmapResults:
    addMipmapFile(result)

  #Handle mipmap layout files.
  mipmapPattern = re.compile('@mipmap/[a-zA-Z0-9_]*')
  mipmapResults = mipmapPattern.findall(contents)
  for result in mipmapResults:
    addMipmapFile(result)

#We only want to if it's an unreferenced PNG.
def deleteIfUnusedPNG(directory, fileName):
    if fileName.endswith(".png"):
      fileNameWithoutExt = os.path.splitext(fileName)[0]
      if fileName.endswith(".9.png"):
        fileNameWithoutExt = os.path.splitext(fileNameWithoutExt)[0]
      if fileNameWithoutExt not in used_drawable_files:
        if fileNameWithoutExt not in used_mipmap_files:
          global files_deleted
          global mega_bytes_deleted

          #Do stats tracking.
          files_deleted += 1
          current_file_size = os.path.getsize(directory+"/"+fileName) / 1024.0 / 1024.0
          mega_bytes_deleted += current_file_size

          #Actually delete the file.
          os.unlink(directory+"/"+fileName)
          print ("Deleted (%.2f Mbs): " + directory+"/"+fileName) % current_file_size

##########
## MAIN ##
##########

#Make sure they passed in a project source directory.
if not len(sys.argv) == 2:
  print 'Usage: "python ImageSweep.py project_src_directory"'
  quit()

rootDirectory = sys.argv[1]
resDirectory = rootDirectory

#Figure out which resources are actually used.
for root, dirs, files in os.walk(rootDirectory):
  if isResourceRoot(root):
    resDirectory = root

  for file in files:
    checkFileForDrawableResources(root+"/"+file)

  for file in files:
	checkFileForMipmapResources(root+"/"+file)
	
#Delete the unused pngs.
for root, dirs, files in os.walk(resDirectory):
    for file in files:
      deleteIfUnusedPNG(root, file)

#Print out how many files were actually deleted.
print ""
print "%d file(s) deleted" % (files_deleted)
print "%.2f megabytes freed" % (mega_bytes_deleted)
