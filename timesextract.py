# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 00:37:23 2021

@author: mariu
"""

import time
import os
import fnmatch
import re
import json
import matplotlib.pyplot as plt
import numpy as np
import csv
import pandas as pd
import statistics as stat
import seaborn as sns
import matplotlib.ticker as tick

df2=pd.DataFrame(columns=['original', 'defaultclique', 'default', 'ext1', 'ext3', 'cover', 'coverpart', 'coverext'])

for file2 in os.listdir('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents'):   
    if fnmatch.fnmatch(file2, '*.json'):
        print(file2)
        pattern=re.search('g=(\d+)', file2)
        gam=pattern.group(1)
        print(pattern.group(1))
        pattern=re.search('d=(\d+)', file2)
        lb=pattern.group(1)
        print(pattern.group(1))
        #csvres=csv.reader(res, delimiter=';')
        f=open('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents/'+file2)
        i+=1
        data=json.load(f)

        t1=data["original"]["Computation Time"]
        t2= data["defaultwithcliques"]["Computation Time"]
        t3=data["default"]["Computation Time"]
        t4= data["ext1"]["Computation Time"]
        t6= data["ext3"]["Computation Time"]
        t5= data["cover"]["Computation Time"]
        t7=data["partitioncover"]["Computation Time"]
        t8=data["savecover"]["Computation Time"]
        tmax=max(t1, t2, t3, t4, t5, t6, t7, t8)
        tmin=min(t1, t2, t3, t4, t5, t6, t7, t8)
        df2.loc[len(df2)]=[t1, t2, t3,  t4, t6,  t5, t7, t8]
        pattern=re.search(r'([^/]+)\.', file2)
        #pattern=re.search('\/[^\/]+[^\.]+', file2)
        a=len(df2)-1
        df2=df2.rename(index={a: pattern.group(1)})
        #plt.savefig('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Grafiken/'+pattern.group(0))
        #plt.close()
        f.close()
