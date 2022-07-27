#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Description: download data from website

import requests
from bs4 import BeautifulSoup
import pandas as pd


# In[11]:


CN='http://www.citypopulation.de/en/china/'
page = requests.get(CN).text
soup = BeautifulSoup(page, 'html.parser')
pro = soup.find('div',id="prov_div")


# In[12]:


prov=[]
urls=pro.find_all('a')
for link in urls:
    href=link.get('href')
    if 'admin'in href:
        if 'townships' not in href and 'xinjiang'not in href:
            pre_href=CN+href
            prov.append(pre_href)
print(prov)


# In[26]:



popdata = pd.DataFrame({'Name':[], 'Status':[], 'Native':[], 'Population2000':[], 'Population2010':[], 'Population2020':[]})
a=0
for i in prov:
    page = requests.get(i).text
    soup = BeautifulSoup(page, 'html.parser')
    #pro = soup.find('div',id="prov_div")
    for county in soup.find_all(class_='admin2'):
            for row in county.find_all('tr'):
                col = row.find_all("td")
                name = col[0].text
                status = col[1].text
                native = col[2].text
                Pop2000 = col[3].text
                Pop2010 = col[4].text
                Pop2020 = col[5].text
                a=a+1
                #save the extracted data into DataFrame
                popdata = popdata.append({"Name":name, "Status":status, "Native":native, "Population2000":Pop2000, "Population2010":Pop2010, "Population2020":Pop2020}, ignore_index=True)  

popdata.head()#  


# In[9]:


#export data into csv
popdata.to_csv('G:\\research\\census.csv',index=False,encoding='utf_8_sig') 


# In[ ]:




