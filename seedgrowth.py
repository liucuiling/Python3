#!/usr/bin/env python
# coding: utf-8

# In[19]:


# Description: Seedgrowth simulation platform using nighttime light data
# Author: Cuiling Liu, cuilingliu36@gmail.com, Shenzhen University
# All right reserved, please do not ditribute it without author's permission
# Updated Date: 2022-07-10

from osgeo import gdal, ogr
import os
import numpy as np
import cv2
import gdal
import matplotlib.pyplot as plt


# In[20]:


# Open a shp File of seeds
driver = ogr.GetDriverByName('ESRI Shapefile')
shp = "G:\\research\\neiborhood identification\\data\\seeeds\\max5\\peak.shp"
ds = driver.Open(shp, 0)
if ds is None:
    print('Open File Failed')
    sys.exit(1)
else:
    print('Open File sucecesfully')


# In[44]:


#get Feature count
layer = ds.GetLayer(0) #only one layer
FeaN=layer.GetFeatureCount()


# In[52]:


# extract coodinates of seeds
xValues = []
yValues = []
for i in range(FeaN):
    feature = layer.GetFeature(i)
    geometry = feature.GetGeometryRef()
    x = geometry.GetX()
    y = geometry.GetY() 
    xValues.append(x)
    yValues.append(y)   


# In[46]:


#read image
dataset=gdal.Open('G:\\research\\neiborhood identification\\data\\prontl5.tif')
if dataset is None:
    print ("Could not open data")
    sys.exit(1)
img_array= dataset.ReadAsArray()
plt.imshow(img_array)


# In[53]:


seed_list=[[]] 

transform = dataset.GetGeoTransform()  # get coordinates information of dataset
x_origin = transform[0]  # X-coordinate
y_origin = transform[3]  # Y-coordinates
proj = dataset.GetProjection()

# pixel number
cols_Red = dataset.RasterXSize  # 
rows_Red = dataset.RasterYSize  # 

#pixel size
pixel_width = transform[1]  
pixel_height = transform[5]
#print(len(xValues))

# obtain the relative location of the pixels
for i in range(FeaN):
    x = xValues[i]
    y = yValues[i]
    x_offset = int((x - x_origin) / pixel_width)
    y_offset = int((y - y_origin) / pixel_height)
    subseed=(x_offset,y_offset)
    seed_list.append(subseed)


# In[56]:


# order the seeds based on pixel value
for i in range (1,n):
    for j in range(1,n-i):
        x1_off=seed_list[j][0]
        y1_off=seed_list[j][1]
        x2_off=seed_list[j+1][0]
        y2_off=seed_list[j+1][1]
        order1= img_array[y1_off, x1_off]
        order2= img_array[y2_off, x2_off]
        if order1<order2:
            (seed_list[j],seed_list[j+1])=(seed_list[j+1],seed_list[j])   

for i in range(1,len(seed_list)):
    a=img_array[seed_list[i][1],seed_list[i][0]]
    print(a)


# In[28]:


#define Point class
class Point(object):
    def __init__(self,x,y):
        self.x = x
        self.y = y
     
    def getX(self):
        return self.x
    def getY(self):
        return self.y
    
#get the pixels' difference
def getGrayDiff(img,currentPoint,tmpPoint): 
    count=img[currentPoint.x,currentPoint.y] - img[tmpPoint.x,tmpPoint.y] 
    return count

# define connection neighbors 
def selectConnects(p): 
    if p != 0:
        connects = [Point(-1, -1), Point(0, -1), Point(1, -1), Point(1, 0), Point(1, 1), Point(0, 1), Point(-1, 1), Point(-1, 0)]
    else:
        connects = [ Point(0, -1),  Point(1, 0),Point(0, 1), Point(-1, 0)]
    return connects

#seed growth method
def regionGrow(img,seeds,thresh,p = 1):  
    height = img.shape[0] # X collum number 606
    width = img.shape[1] # Y row number 453
    print(height, width)
    seedMark = np.zeros([height,width]) 
    
    seedList = [] #original seeds
    subseedList = [] # new candidate seeds
    for seed in seeds:
        seedList.append(seed)
   
    label = 1
    connects = selectConnects(p)
   
    while(len(seedList)>0):
        currentPoint = seedList.pop(0)#remove the first seed
        print(currentPoint)
        subseedList.append(currentPoint)
        
        seedMark[currentPoint.x,currentPoint.y] = label
        
        while(len(subseedList)>0):     
            subcurrentPoint = subseedList.pop(0) #remove the first candidate seed from the seedlist
            for i in range(8):
                tmpX = subcurrentPoint.x + connects[i].x
                tmpY = subcurrentPoint.y + connects[i].y
                print(tmpX, tmpY)
                if tmpX < 0 or tmpY < 0 or tmpX >=height or tmpY >=width :
                    continue
                grayDiff = getGrayDiff(img,subcurrentPoint,Point(tmpX,tmpY))
                print('difference',grayDiff)
                if grayDiff > thresh and seedMark[tmpX,tmpY] == 0:
                    seedMark[tmpX,tmpY] = label
                    subseedList.append(Point(tmpX,tmpY))
        label=label+1 
    return (seedMark)  


# In[29]:


seedss=[] 
for i in range(1,len(seed_list)):
    a=seed_list[i][0]
    b=seed_list[i][1]
    p=Point(b,a)
    seedss.append(p) 
binaryImg = regionGrow(img_array,seedss,0,p = 1)


# In[30]:


#display region growth result
import matplotlib.pyplot as plt
plt.imshow(binaryImg)


# In[31]:


# save result to tif 
driver = gdal.GetDriverByName('GTiff')
raster_file='G:\\research\\neiborhood identification\\data\\afterpront5by5.tif'
dst_ds = driver.Create(raster_file, binaryImg.shape[1], binaryImg.shape[0], 1, gdal.GDT_Int32)
dst_ds.SetProjection(proj)
dst_ds.SetGeoTransform(transform)  
dst_ds.GetRasterBand(1).WriteArray( binaryImg)  
dst_ds.FlushCache()
dst_ds = None
print("successfully convert array to raster")


# In[ ]:





# In[ ]:




