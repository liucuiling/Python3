#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd


from dbfread import DBF
from pandas import DataFrame

#dbf = DBF("C:\\Users\\yapingxu.ASURITE\\Documents\\Allen Coral Atlas\\Oahu\\bottom_reprocess\\kanbay\\CoralClip\\ShpData\\ValidLocationsMean.dbf", load=True)
dbf = DBF("D:\\LCL\\LCL\\yaping coral reef\\ShpData\\ShpData\\ValidLocationsMean.dbf", load=True)
df = DataFrame(iter(dbf))

#from simpledbf import Dbf5
# dbf = Dbf5("C:\\Users\\LCL\\Allen Coral Atlas\\ShpData\\ValidLocationsMax.dbf")

#import geopandas as gpd
#gpddf = gpd.read_file("C:\\Users\\yapingxu.ASURITE\\Documents\\Allen Coral Atlas\\Oahu\\bottom_reprocess\\kanbay\\CoralClip\\ShpData\\ValidLocationsMean.dbf",float_precision='high') 
#df=pd.DataFrame(gpddf)


#df1 = gpd.GeoDataFrame.from_file(u"C:\\Users\\yapingxu.ASURITE\\Documents\\Allen Coral Atlas\\Oahu\\bottom_reprocess\\kanbay\\CoralClip\\ShpData\\ValidLocationsMean.dbf")
#df = pd.DataFrame(df1)

##df = dbf.to_dataframe()
#df


# In[5]:


import sys
'geopandas' in sys.modules


# In[6]:


table = pd.pivot_table(df, values=['20190429','20190506','20190513','20190520'], index=['Id', 'ORIG_FID','POINT_X', 'POINT_Y']
                   )


# In[20]:


#table


# In[8]:


df.melt(id_vars=['ORIG_FID','POINT_X', 'POINT_Y'], 
        var_name="Date", 
        value_name="Value")


# In[9]:


#print(df.ix[10, 'POINT_X'])


# In[10]:


df2=df.melt(id_vars=['Id','ORIG_FID','POINT_X', 'POINT_Y'], 
        var_name="ds", 
        value_name="y")


# In[11]:


df2.head()


# In[12]:


len(df2)


# In[13]:


df2['y']=df2['y']/10000


# In[14]:


df2.head()


# In[18]:


import pandas as pd
from fbprophet import Prophet
import matplotlib
import altair as alt
alt.renderers.enable('notebook')
from vega_datasets import data

from altair import pipe, limit_rows, to_values
t = lambda data: pipe(data, limit_rows(max_rows=110000), to_values) # default is 5000 rows, changed to 6000 to display total rows.
alt.data_transformers.register('custom', t)
alt.data_transformers.enable('custom')

#df1 = pd.read_excel("C:\\Users\\yapingxu\\Documents\\TimeSeriesPython\\Oahu\\DataCSV - Copy.xlsx")
def fit_predict_model(dataframe, interval_width = 0.999999999, changepoint_range = 0.99):
    m = Prophet(daily_seasonality = False, yearly_seasonality = False, weekly_seasonality = False,
                seasonality_mode = 'multiplicative', 
                interval_width = interval_width,
                changepoint_range = changepoint_range)
    m = m.fit(dataframe)
    forecast = m.predict(dataframe)
    forecast['fact'] = dataframe['y'].reset_index(drop = True)
    forecast['Id'] = dataframe['Id']
    return forecast
    
pred = fit_predict_model(df2)


# In[19]:


def detect_anomalies(forecast):
    forecasted = forecast[['ds','trend', 'yhat', 'yhat_lower', 'yhat_upper', 'fact','Id']].copy()
    #forecast['fact'] = df['y']

    forecasted['anomaly'] = 0
    forecasted.loc[forecasted['fact'] > 1.5*forecasted['yhat_upper'], 'anomaly'] = 1
    forecasted.loc[forecasted['fact'] < 1.5*forecasted['yhat_lower'], 'anomaly'] = -1

    #anomaly importances, define the size of the red points
    forecasted['importance'] = 0
    forecasted.loc[forecasted['anomaly'] ==1, 'importance'] =         (forecasted['fact'] - forecasted['yhat_upper'])/forecast['fact']
    forecasted.loc[forecasted['anomaly'] ==-1, 'importance'] =         (forecasted['yhat_lower'] - forecasted['fact'])/forecast['fact']
    
    return forecasted

pred = detect_anomalies(pred)


# In[17]:


def plot_anomalies(forecasted):
    interval = alt.Chart(forecasted).mark_area(interpolate="basis", color = '#7FC97F').encode(
    x=alt.X('ds:T',  title ='date'),
    y='yhat_upper',
    y2='yhat_lower',
    tooltip=['ds', 'fact', 'yhat_lower', 'yhat_upper','Id']
    ).interactive().properties(
        title='Anomaly Detection'
    )

    fact = alt.Chart(forecasted[forecasted.anomaly==0]).mark_circle(size=15, opacity=0.7, color = 'Black').encode(
        x='ds:T',
        y=alt.Y('fact', title='bottom reflectance'),    
        tooltip=['ds', 'fact', 'yhat_lower', 'yhat_upper','Id']
    ).interactive()

    anomalies = alt.Chart(forecasted[forecasted.anomaly!=0]).mark_circle(size=30, color = 'Red').encode(
        x='ds:T',
        y=alt.Y('fact', title='bottom reflectance'),    
        tooltip=['ds', 'fact', 'yhat_lower', 'yhat_upper','Id'],
        size = alt.Size( 'importance', legend=None)
    ).interactive()

    return alt.layer(interval, fact, anomalies)              .properties(width=870, height=450)              .configure_title(fontSize=20)
              
plot_anomalies(pred)


# In[48]:


upper = pred[pred['fact']>pred['yhat_upper']] 
lower = pred[pred['fact']<pred['yhat_lower']] 
abnorm=pred[pred['anomaly']==0]


# In[51]:


print(pred)


# In[50]:


print(abnorm)


# In[46]:


print(upper)


# In[47]:


print(lower)


# In[ ]:




