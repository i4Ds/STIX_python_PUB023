#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[36]:


import numpy as np
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
filename='lightcurve.csv'
df = pd.read_csv(filename)


# In[ ]:





# In[37]:


len(df.utc)


# In[38]:


dim=len(df.utc)
t=np.linspace(0, (dim-1)*4, dim)


# In[39]:


pprint(df.columns)


# In[40]:



plt.plot(t, df['ebin1'])
plt.xlabel('Time [s]')
plt.ylabel('Signal amplitude');
plt.show()


# In[41]:


from scipy import fftpack
fs=0.25
X=fftpack.fft(df['ebin1'])
freqs=fftpack.fftfreq(dim)*fs


# In[50]:


plt.xlim(-fs/2., fs/2.)
plt.plot(freqs, np.abs(X))
plt.xlabel('Frequency in Hz')
plt.ylabel('Amplitude')

plt.show()

# In[51]:


pprint(np.abs(X))


# In[52]:


X


# In[ ]:




