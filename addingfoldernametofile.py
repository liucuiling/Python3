#!/usr/bin/env python
# coding: utf-8

# In[88]:


import os


# In[90]:


path=os.path.dirname("D:\LCL\LCL\Raster Examples\descending_20190506_to_20190513/")
date=os.path.basename(path)
print (date)
type(date)


# In[91]:



data = os.path.abspath("D:\LCL\LCL\Raster Examples\descending_20190506_to_20190513")
print(data)
for i, f in enumerate(os.listdir(data)):
    
    print (f)
    new=str(date)+"_"+str(f)
    print(new)
    type(f)
    src = os.path.join(data, f)
    dst = os.path.join(data, new)
    os.rename(src,dst)
   


# In[ ]:





# In[ ]:




