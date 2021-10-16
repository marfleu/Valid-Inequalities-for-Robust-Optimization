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
import statistics as stat
import seaborn as sns
import matplotlib.ticker as tick

i=0
#res=open('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/ComputationalResults.csv')
#csvres=csv.reader(res, delimiter=';')
bound={}
orig={}
defau={}
defaucli={}
ext1={}
ext3={}
cover={}
coverext={}
covercli={}

csvres=pd.read_csv('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Ergebnisse/ComputationalResults.csv', delimiter=';')
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
        primal=False
        for line in csvres.index:
            if not fnmatch.fnmatch(file2, csvres['Instance'][line] + '*'):
                continue
            if fnmatch.fnmatch(file2, csvres['Instance'][line] + '*') and float(gam)==float(csvres['Gamma Percentage Used Variables'][line]) and float(lb)==float(csvres['Lower Percentage Deviation'][line]):
                try:
                    y=float(csvres['Primal Bound'][line])
                    if csvres['Optimal'][line]==True:
                        primal=True
                        y0=float(csvres['Primal Bound'][line])
                    print('match: ', csvres['Instance'][line])
                except:
                    print(csvres['Primal Bound'][line])
                    continue
        if not primal:
            y0=y
        print("Dual Bound: ",  y0)        
        f=open('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Testinstanzen/RobustnessComponents/'+file2)
        i+=1
        data=json.load(f)
        try:
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
            t7=data["partitioncover"]["Building Time"] + data["partitioncover"]["Computation Time"]
            y7=data["partitioncover"]["Objective value"]  
            t8=data["savecover"]["Building Time"] + data["savecover"]["Computation Time"]
            y8=data["savecover"]["Objective value"]  
            tmax=max(t1, t2, t3, t4, t5, t6, t7, t8)
            tmin=min(t1, t2, t3, t4, t5, t6, t7, t8)
            plt.plot([t1], [y1], 'rx', label='original robust')
            plt.plot([t2], [y2], 'yx', label='default reduction')
            plt.plot([t3], [y3], color='orange', marker='x', label='default')
            plt.plot([t4], [y4], color='indigo', marker='x', label='extended 1x')
            plt.plot([t6], [y6], color='violet', marker='x', label='extended 3x')
            plt.plot([t5], [y5], color='deeppink', marker='x', label='cover')
            plt.plot([t7], [y7], color='lightgreen', marker='x', label='cover partition')
            plt.plot([t8], [y8], color='darkgreen', marker='x', label='cover strength')
            #plt.plot([t1, t2, t3, t4, t5, t6], [y1, y2, y3, y4, y5, y6], 'rx')
            # plt.text(t1, y1, 'original')
            # plt.text(t2, y2, 'defwithcli')
            # plt.text(t3, y3, 'def')
            # plt.text(t4, y4, 'ext1')
            # plt.text(t6, y6, 'ext3')
            # plt.text(t5, y5, 'cover')
            plt.text(tmax/2, y0, 'primal bound')
            plt.hlines(y1, 0, tmax, colors='b')
            plt.hlines(y0, 0, tmax, colors='g')
            plt.xlabel('time [s]')
            plt.ylabel('obj. value')
            plt.legend(loc='best')
            pattern=re.search('[^\.]+', file2)
            #plt.savefig('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Grafiken/'+pattern.group(0))
            plt.close()
            f.close()
        except:
            continue
        try:
                bound[float(gam)].append(y0)
                orig[float(gam)].append([1, y1])
                defau[float(gam)].append([t2/t1, y2])
                defaucli[float(gam)].append([t3/t1, y3])
                ext1[float(gam)].append([t4/t1, y4])
                ext3[float(gam)].append([t6/t1, y6])
                cover[float(gam)].append([t5/t1, y5])
                coverext[float(gam)].append([t7/t1, y7])
                covercli[float(gam)].append([t8/t1, y8])
        except:
                bound[float(gam)]=[y0]
                orig[float(gam)]=[[1, y1]]
                defau[float(gam)]=[[t2/t1, y2]]
                defaucli[float(gam)]=[[t3/t1, y3]]
                ext1[float(gam)]=[[t4/t1, y4]]
                ext3[float(gam)]=[[t6/t1, y6]]
                cover[float(gam)]=[[t5/t1, y5]]
                coverext[float(gam)]=[[t7/t1, y7]]
                covercli[float(gam)]=[[t8/t1, y8]]
            



avgtimes={}
avgtimes['defau']=[]
avgtimes['defaucli']=[]
avgtimes['ext1']=[]
avgtimes['ext3']=[]
avgtimes['cover']=[]
avgtimes['coverext']=[]
avgtimes['covercli']=[]
posmeth={}
for m in [10, 40, 70, 100]:
        t1=[orig[m][n][0] for n in range(0, len(orig[m]))]
        t2=[defau[m][n][0] for n in range(0, len(defau[m]))]
        t3= [defaucli[m][n][0] for n in range(0, len(defaucli[m]))]
        t4=[ext1[m][n][0] for n in range(0, len(ext1[m]))]
        t5=[ext3[m][n][0] for n in range(0, len(ext3[m]))]
        t6=[cover[m][n][0] for n in range(0, len(cover[m]))]
        t7=[coverext[m][n][0] for n in range(0, len(coverext[m]))]
        t8=[covercli[m][n][0] for n in range(0, len(covercli[m]))]
        t1mean=stat.mean(t1)
        t2mean=stat.mean(t2)
        t3mean=stat.mean(t3)
        t4mean=stat.mean(t4)
        t5mean=stat.mean(t5)
        t6mean=stat.mean(t6)
        t7mean=stat.mean(t7)
        t8mean=stat.mean(t8)
        t1stddev=stat.stdev(t1)
        t2stddev=stat.stdev(t2)
        t3stddev=stat.stdev(t3)
        t4stddev=stat.stdev(t4)
        t5stddev=stat.stdev(t5)
        t6stddev=stat.stdev(t6)
        t7stddev=stat.stdev(t7)
        t8stddev=stat.stdev(t8)
        #avgtimes['defau']=[t1mean, t1stddev, m]
        avgtimes['defau'].append([t2mean, t2stddev, m])
        avgtimes['defaucli'].append([t3mean, t3stddev, m])
        avgtimes['ext1'].append([t4mean, t4stddev, m])
        avgtimes['ext3'].append([t5mean, t5stddev, m])
        avgtimes['cover'].append([t6mean, t6stddev, m])
        avgtimes['coverext'].append([t7mean, t7stddev, m])
        avgtimes['covercli'].append([t8mean, t8stddev, m])
        posmeth[m]=['defau', 'defaucli', 'ext1', 'ext3', 'cover', 'coverext', 'covercli']
        methpos={}
        for x in avgtimes:
            methpos[x]=0
            for y in avgtimes:
                if x==y:
                    continue
                if avgtimes[x] > avgtimes[y]:
                    methpos[x]+=1
            posmeth[m][methpos[x]]=x
                    
gaps={} 
gapswoz={}       
for m in [10, 40, 70, 100]:
    gaps={}
    for i in range(0, 7):
        meth=posmeth[m][i]
        numbers=[]        
        for n in range(0, len(defau[m])):
            y0=bound[m][n]
            y1=orig[m][n][1]
            y2=defau[m][n][1]
            y3=defaucli[m][n][1]
            y4=ext1[m][n][1]
            y5=ext3[m][n][1]
            y6=cover[m][n][1]
            y7=coverext[m][n][1]
            y8=covercli[m][n][1]
            if meth=='defau':
                if y0 > 0:
                    numbers.append(y2/y0 - y1/y0)
                else:
                    numbers.append(y0/y2 - y0/y1)
            if meth=='defaucli':
                if y0 > 0:
                    numbers.append(y3/y0 - y1/y0)
                else:
                    numbers.append(y0/y3 - y0/y1)
            if meth=='ext1':
                if y0 > 0:
                    numbers.append(y4/y0 - y1/y0)
                else:
                    numbers.append(y0/y4 - y0/y1)
            if meth=='ext3':
                if y0 > 0:
                    numbers.append(y5/y0 - y1/y0)
                else:
                    numbers.append(y0/y5 - y0/y1)
            if meth=='cover':
                if y0 > 0:
                    numbers.append(y6/y0 - y1/y0)
                else:
                    numbers.append(y0/y6 - y0/y1)
            if meth=='coverext':
                if y0 > 0:
                    numbers.append(y7/y0 - y1/y0)
                else:
                    numbers.append(y0/y7 - y0/y1)
            if meth=='covercli':
                if y0 > 0:
                    numbers.append(y8/y0 - y1/y0)
                else:
                    numbers.append(y0/y8 - y0/y1)
        for ts in avgtimes[meth]:
            if ts[2]==m:
                meth+='\n' + str(round(ts[0], 2)) + '[' + str(round(ts[1],2)) + ']'
        gaps[meth]=numbers
        gapswoz[meth]=[y for y in numbers if abs(y)>0.005]
    df=pd.DataFrame(data=gaps)
    ax=sns.boxplot(data=df)

    ax.set_yscale('log')
    ax.set_ylim([0,1])
    plt.setp(ax.get_xticklabels(), rotation=0, horizontalalignment='right', fontsize='x-small')


    ax.yaxis.set_major_formatter(tick.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
    plt.savefig('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Grafiken/' + 'boxplot' + str(m))
    plt.close()
    df.loc[~(df==0).all(axis=1)]
    df= df[abs(df['ColName']) >= 0.00001]
    df=df[(df.sum(axis=1) >= 0.0001)]
        
    ax=sns.boxplot(data=df)

    ax.set_yscale('log')
    ax.set_ylim([0,1])
    plt.setp(ax.get_xticklabels(), rotation=0, horizontalalignment='right', fontsize='x-small')


    ax.yaxis.set_major_formatter(tick.FuncFormatter(lambda y,pos: ('{{:.{:1d}f}}'.format(int(np.maximum(-np.log10(y),0)))).format(y)))
    plt.savefig('C:/Users/mariu/OneDrive/Dokumente/Masterarbeit/Grafiken/' + 'boxplotnonzeros' + str(m))
    plt.close()    

# gapsorig=[]
# gapsdefau=[]
# gapsdefaucli=[]
# gapsext1=[]
# gapsext3=[]
# gapscover=[]
# gapscoverext=[]
# gapscovercli=[]


# for n in range(0, len(defau[100])):
#     a=orig[100][n][1]
#     b=bound[100][n]
#     if defau[100][n][1]>0:
#         gapsorig.append(a/b)
#     else:
#         gapsorig.append(b/a);
# for n in range(0, len(defau[100])):
#     a=defau[100][n][1]
#     b=bound[100][n]
#     if defau[100][n][1]>0:
#         gapsdefau.append(a/b)
#     else:
#         gapsdefau.append(b/a);
# for n in range(0, len(defau[100])):
#     a=defaucli[100][n][1]
#     b=bound[100][n]
#     if defaucli[100][n][1]>0:
#         gapsdefaucli.append(a/b)
#     else:
#         gapsdefaucli.append(b/a);
# for n in range(0, len(defau[100])):
#     a=ext1[100][n][1]
#     b=bound[100][n]
#     if ext1[100][n][1]>0:
#         gapsext1.append(a/b)
#     else:
#         gapsext1.append(b/a);
# for n in range(0, len(defau[100])):
#     a=ext3[100][n][1]
#     b=bound[100][n]
#     if ext3[100][n][1]>0:
#         gapsext3.append(a/b)
#     else:
#         gapsext3.append(b/a);
# for n in range(0, len(defau[100])):
#     a=cover[100][n][1]
#     b=bound[100][n]
#     if cover[100][n][1]>0:
#         gapscover.append(a/b)
#     else:
#         gapscover.append(b/a);
# for n in range(0, len(defau[100])):
#     a=coverext[100][n][1]
#     b=bound[100][n]
#     if coverext[100][n][1]>0:
#         gapscoverext.append(a/b)
#     else:
#         gapscoverext.append(b/a);
# for n in range(0, len(defau[100])):
#     a=covercli[100][n][1]
#     b=bound[100][n]
#     if covercli[100][n][1]>0:
#         gapscovercli.append(a/b)
#     else:
#         gapscovercli.append(b/a);
#for gam in [10.0, 40.0, 70.0, 100.0]:
    
    

#plt.scatter(orig[100][0],orig[100][1] , color='red')
#plt.scatter(defau[100][0],defau[100][1] , color='blue')
