#!/usr/bin/env python
# coding: utf-8

# In[14]:


import os


# In[15]:


path="D:/LCL/LCL/Raster Examples"
filenames= os.listdir(path)
print(filenames)


# In[16]:


for filename in filenames:
    subpath=os.path.join(path,filename)
    data=os.path.abspath(subpath)
    for i, f in enumerate(os.listdir(data)):
        new=str(filename)+"_"+str(f)
        print(new)
        type(f)
        src = os.path.join(data, f)
        dst = os.path.join(data, new)
        os.rename(src,dst)


# In[13]:


merge=path+"all"
os.mkdir(merge)


# In[ ]:


for filename in filenames:
    

