# -*- coding: utf-8 -*-
"""
Created on Sat Sep 25 12:44:08 2021

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

i=0
#res=open('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/ComputationalResults.csv')
#csvres=csv.reader(res, delimiter=';')
csvres=pd.read_csv('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/ComputationalResults.csv', delimiter=';')
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
        for line in csvres.index:
            if not fnmatch.fnmatch(file2, csvres['Instance'][line] + '*'):
                continue
            if fnmatch.fnmatch(file2, csvres['Instance'][line] + '*') and float(gam)==float(csvres['Gamma Percentage Used Variables'][line]) and float(lb)==float(csvres['Lower Percentage Deviation'][line]):
                try:
                    y0=float(csvres['Dual Bound'][line])
                    print('match: ', csvres['Instance'][line])
                except:
                    print(csvres['Dual Bound'][line])
                    continue
                
        print("Dual Bound: ",  y0)        
        f=open('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents/'+file2)
        i+=1
        data=json.load(f)
        t1=data["original"]["Building Time"] + data["original"]["Computation Time"]
        y1=data["original"]["Objective value"]
        t2=data["defaultwithcliques"]["Building Time"] + data["defaultwithcliques"]["Computation Time"]
        y2=data["defaultwithcliques"]["Objective value"]
        t3=data["default"]["Building Time"] + data["default"]["Computation Time"]
        y3=data["default"]["Objective value"]
        t4=data["ext1"]["Building Time"] + data["ext1"]["Computation Time"]
        y4=data["ext1"]["Objective value"]
        t6=data["ext3"]["Building Time"] + data["ext3"]["Computation Time"]
        y6=data["ext3"]["Objective value"]
        t5=data["cover"]["Building Time"] + data["cover"]["Computation Time"]
        y5=data["cover"]["Objective value"]  
        tmax=max(t1, t2, t3, t4, t5, t6)
        tmin=min(t1, t2, t3, t4, t5, t6)
        plt.plot([t1], [y1], 'rx', label='original robust')
        plt.plot([t2], [y2], 'yx', label='default reduction')
        plt.plot([t3], [y3], color='orange', marker='x', label='default')
        plt.plot([t4], [y4], color='indigo', marker='x', label='extended 1x')
        plt.plot([t5], [y5], color='violet', marker='x', label='extended 3x')
        plt.plot([t6], [y6], color='deeppink', marker='x', label='cover')
        #plt.plot([t1, t2, t3, t4, t5, t6], [y1, y2, y3, y4, y5, y6], 'rx')
        # plt.text(t1, y1, 'original')
        # plt.text(t2, y2, 'defwithcli')
        # plt.text(t3, y3, 'def')
        # plt.text(t4, y4, 'ext1')
        # plt.text(t6, y6, 'ext3')
        # plt.text(t5, y5, 'cover')
        plt.hlines(y1, 0, tmax, colors='b')
        plt.hlines(y0, 0, tmax, colors='g')
        plt.xlabel('time [s]')
        plt.ylabel('obj. value')
        plt.legend(loc='upper right')
        pattern=re.search('[^\.]+', file2)
        plt.savefig('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents/'+pattern.group(0))
        plt.close()
        f.close()
        break