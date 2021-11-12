# -*- coding: utf-8 -*-
"""
Script to evaluate the json files with the different values of all instances (computed by comparerobustmethods).
Performs the graphical evaluations and also 
"""


import os
import fnmatch
import re
import json
import matplotlib.pyplot as plt
import numpy as np
import csv
import pandas as pd
import seaborn as sns


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
df2=pd.DataFrame(columns=['gamma', 'range', 'bound',  'originaltime', 'originalvalue', 'defaultcliquetime', 'defaultcliquevalue', 'defaulttime', 'defaultvalue', 'ext1time', 'ext1value', 'covertime', 'covervalue', 'coverparttime', 'coverpartvalue', 'coverexttime', 'coverextvalue'])

csvres=pd.read_csv('C:/Users/User/Documents/Masterarbeit/ergebnisse/ComputationalResults.csv', delimiter=';')
for file2 in os.listdir('C:/Users/User/Documents/Masterarbeit/data'):   
    if fnmatch.fnmatch(file2, '*.json'):
        print(file2)
        pattern=re.search('g=(\d+)', file2)
        gam=pattern.group(1)
        print(pattern.group(1))
        pattern=re.search('d=(\d+)', file2)
        lb=pattern.group(1)
        print(pattern.group(1))
        primal=False
        y=float('inf')
        for line in csvres.index:
            if not fnmatch.fnmatch(file2, csvres['Instance'][line] + '*'):
                continue
            if fnmatch.fnmatch(file2, csvres['Instance'][line] + '*') and float(gam)==float(csvres['Gamma Percentage Used Variables'][line]) and float(lb)==float(csvres['Lower Percentage Deviation'][line]):
                try:
                    if float(csvres['Primal Bound'][line]) < y:
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
        print("Primal Bound: ",  y0)        
        f=open('C:/Users/User/Documents/Masterarbeit/data/'+file2)
        i+=1
        data=json.load(f)
        try:
            #at the moment it is for analyzing the pure model solving times.
            #add the following command instead, if wanting to analyze complete computation times
            #t1=data["original"]["Building Time"] + data["original"]["Computation Time"]
            t1= data["original"]["Computation Time"]

            y1=data["original"]["Objective value"]
            t2=data["defaultwithcliques"]["Computation Time"]
            y2=data["defaultwithcliques"]["Objective value"]
            t3= data["default"]["Computation Time"]
            y3=data["default"]["Objective value"]
            t4= data["ext1"]["Computation Time"]
            y4=data["ext1"]["Objective value"]
            t5= data["cover"]["Computation Time"]
            y5=data["cover"]["Objective value"]  
            t7= data["partitioncover"]["Computation Time"]
            y7=data["partitioncover"]["Objective value"]  
            t8= data["savecover"]["Computation Time"]
            y8=data["savecover"]["Objective value"]  
            tmax=max(t1, t2, t3, t4, t5, t7, t8)
            tmin=min(t1, t2, t3, t4, t5, t7, t8)
            plt.plot([t1], [y1], 'rx', label='original robust')
            plt.plot([t2], [y2], 'yx', label='default reduction')
            plt.plot([t3], [y3], color='orange', marker='x', label='default')
            plt.plot([t4], [y4], color='indigo', marker='x', label='extended 1x')
            plt.plot([t5], [y5], color='deeppink', marker='x', label='cover')
            plt.plot([t7], [y7], color='lightgreen', marker='x', label='cover partition')
            plt.plot([t8], [y8], color='darkgreen', marker='x', label='cover strength')
            plt.text(t1, y1, 'original')
            plt.text(t2, y2, 'defwithcli')
            plt.text(t3, y3, 'def')
            plt.text(t4, y4, 'ext1')
            plt.text(t5, y5, 'cover')
            plt.text(tmax/2, y0, 'primal bound')
            plt.hlines(y1, 0, tmax, colors='b')
            plt.hlines(y0, 0, tmax, colors='g')
            plt.xlabel('time [s]')
            plt.ylabel('obj. value')
            plt.legend(loc='best')
            pattern=re.search('[^\.]+', file2)
            df2.loc[len(df2)]=[gam, lb, y0, t1, y1, t2, y2, t3, y3, t4, y4, t5, y5, t7, y7, t8, y8]
            a=len(df2)-1
            df2=df2.rename(index={a: pattern.group(0)})
            #uncomment if wanting to really plot all the values
            #plt.savefig('C:/Users/User/Documents/Masterarbeit/Grafiken/'+pattern.group(0))
            plt.close()
            f.close()
        except:
            continue

            

df3=pd.DataFrame(data=df2.loc[:,['originaltime', 'defaultcliquetime', 'defaulttime', 'ext1time', 'covertime', 'coverexttime','coverparttime']])
df3.rename(columns={'originaltime':'original', 'defaultcliquetime':'defaultclique', 'defaulttime':'default', 'ext1time':'ext1', 'covertime':'cover', 'coverexttime':'coverext','coverparttime':'coverpart'}, inplace=True)
df3=df3.apply(lambda x: x/x['original'], axis=1)
timestat=df3.describe()
timestat=np.round(timestat, 5)
timestat.to_latex('C:/Users/User/Documents/Masterarbeit/Tables/modeltimestats.tex')
ax=sns.stripplot(data=df3.loc[:,['defaultclique', 'default', 'ext1', 'cover', 'coverext','coverpart']], alpha=0.85, size=1.5)
ax.set_ylim([0,20])
plt.ylabel('relative computation time')
plt.savefig('C:/Users/User/Documents/Masterarbeit/Grafiken/' + 'scattertimes')
plt.close()

# for m in [10, 40, 70, 100]:
#     df4=pd.DataFrame(data=df2.loc[df2['gamma']==str(m), ['bound','originalvalue', 'defaultcliquevalue', 'defaultvalue', 'ext1value', 'covervalue', 'coverextvalue','coverpartvalue']])
#     df4=df4.apply(lambda x: x/x['bound'] if x['bound']>0 else x['bound']/x, axis=1)
#     df4.rename(columns={'originalvalue':'original', 'defaultcliquevalue':'defaultclique', 'defaultvalue':'default', 'ext1value':'ext1', 'covervalue':'cover', 'coverextvalue':'coverext','coverpartvalue':'coverpart'}, inplace=True)

#     ax = sns.violinplot(data=df4.loc[:,['original', 'defaultclique', 'default', 'ext1', 'cover', 'coverext','coverpart']], palette="Set2", scale="count", inner="quartile", color='red', order=['original','defaultclique', 'default','coverpart', 'cover','coverext', 'ext1'])
#     y_ticks = np.arange(0, 1, 0.1)
    
#     plt.yticks(y_ticks, fontsize='small')
#     ax.set_ylim([0,1])
#     plt.ylabel('integrality gap')
#     plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
#     plt.savefig('C:/Users/User/Documents/Masterarbeit/Grafiken/' + 'boxplot' + str(m))
#     plt.close()
#     df4.to_csv('C:/Users/User/Documents/Masterarbeit/Tables/integrality_gaps_'+str(m)+'.csv')
#     stas=df4.describe()
#     stas=np.round(stas, 5)
#     stas.to_latex('C:/Users/User/Documents/Masterarbeit/Tables/int_gaps_stats_'+str(m)+'.tex');
    
    
# for m in [10, 40, 70, 100]:
#     df4=pd.DataFrame(data=df2.loc[df2['gamma']==str(m), ['bound','originalvalue', 'defaultcliquevalue', 'defaultvalue', 'ext1value', 'covervalue', 'coverextvalue','coverpartvalue']])
#     df4=df4.apply(lambda x: x/x['bound'] if x['bound']>0 else x['bound']/x, axis=1)
#     df4=df4.apply(lambda x: x-x['originalvalue'], axis=1)
#     df4.rename(columns={'originalvalue':'original', 'defaultcliquevalue':'defaultclique', 'defaultvalue':'default', 'ext1value':'ext1', 'covervalue':'cover', 'coverextvalue':'coverext','coverpartvalue':'coverpart'}, inplace=True)
#     ax = sns.violinplot(data=df4.loc[:,['defaultclique', 'default', 'ext1', 'cover', 'coverext','coverpart']], palette="Set2", scale="count", inner="quartile", color='red', order=['defaultclique', 'default','coverpart', 'cover','coverext', 'ext1'])
#     y_ticks = np.arange(0, 0.8, 0.1)
#     plt.ylabel('integrality gap difference')
#     plt.yticks(y_ticks, fontsize='small')
#     ax.set_ylim([0,0.8])
#     plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
#     plt.savefig('C:/Users/User/Documents/Masterarbeit/Grafiken/' + 'boxplot_diff' + str(m))
#     plt.close()
#     df4.to_csv('C:/Users/User/Documents/Masterarbeit/Tables/integrality_gaps_difference_'+str(m)+'.csv')
#     stas=df4.describe()
#     stas=np.round(stas, 5)
#     stas.to_latex('C:/Users/User/Documents/Masterarbeit/Tables/int_gaps_diff_stats_'+str(m)+'.tex');
    
    
for m in [10, 40, 70, 100]:
    df4=pd.DataFrame(data=df2.loc[df2['gamma']==str(m), ['bound','originalvalue', 'defaultcliquevalue', 'defaultvalue', 'ext1value', 'covervalue', 'coverextvalue','coverpartvalue']])
    df4=df4.apply(lambda x: 1-x/x['bound'] if (x['bound']>0 and x['originalvalue']*x['bound']>0) else (1-x['bound']/x if (x['bound']<=0 and x['originalvalue']*x['bound']>0) else None) , axis=1)
    df4=df4.apply(lambda x: (x['originalvalue']-x)/x['originalvalue'] if x['originalvalue']!=0 else 0, axis=1)
    df4.rename(columns={'originalvalue':'original', 'defaultcliquevalue':'defaultclique', 'defaultvalue':'default', 'ext1value':'ext1', 'covervalue':'cover', 'coverextvalue':'coverext','coverpartvalue':'coverpart'}, inplace=True)
    ax = sns.violinplot(data=df4.loc[:,['defaultclique', 'default', 'ext1', 'cover', 'coverext','coverpart']], palette="Set2", scale="count", inner="quartile", color='red', order=['defaultclique', 'default','coverpart', 'cover','coverext', 'ext1'])
    y_ticks = np.arange(0, 1, 0.1)
    plt.ylabel('integrality gap closed')
    plt.yticks(y_ticks, fontsize='small')
    ax.set_ylim([0,1])
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
    plt.savefig('C:/Users/User/Documents/Masterarbeit/Grafiken/' + 'integrality_gaps_closed_' + str(m))
    plt.close()
    df4.to_csv('C:/Users/User/Documents/Masterarbeit/Tables/integrality_gaps_difference_'+str(m)+'.csv')
    stas=df4.describe()
    stas=np.round(stas, 5)
    stas.to_latex('C:/Users/User/Documents/Masterarbeit/Tables/integrality_gaps_closed_'+str(m)+'.tex');
    
for m in [10, 40, 70, 100]:
    df4=pd.DataFrame(data=df2.loc[df2['gamma']==str(m), ['bound','originalvalue', 'defaultcliquevalue', 'defaultvalue', 'ext1value', 'covervalue', 'coverextvalue','coverpartvalue']])
    df4=df4.apply(lambda x: 1-x/x['bound'] if (x['bound']>0 and x['originalvalue']*x['bound']>0) else (1-x['bound']/x if (x['bound']<=0 and x['originalvalue']*x['bound']>0) else None) , axis=1)
    df4.rename(columns={'originalvalue':'original', 'defaultcliquevalue':'defaultclique', 'defaultvalue':'default', 'ext1value':'ext1', 'covervalue':'cover', 'coverextvalue':'coverext','coverpartvalue':'coverpart'}, inplace=True)

    ax = sns.violinplot(data=df4.loc[:,['original', 'defaultclique', 'default', 'ext1', 'cover', 'coverext','coverpart']], palette="Set2", scale="count", inner="quartile", color='red', order=['original','defaultclique', 'default','coverpart', 'cover','coverext', 'ext1'])
    y_ticks = np.arange(0, 1, 0.1)
    
    plt.yticks(y_ticks, fontsize='small')
    ax.set_ylim([0,1])
    plt.ylabel('integrality gap')
    plt.setp(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize='x-small')
    plt.savefig('C:/Users/User/Documents/Masterarbeit/Grafiken/' + 'boxplot' + str(m))
    plt.close()
    df4.to_csv('C:/Users/User/Documents/Masterarbeit/Tables/integrality_gaps_'+str(m)+'.csv')
    stas=df4.describe()
    stas=np.round(stas, 5)
    stas.to_latex('C:/Users/User/Documents/Masterarbeit/Tables/int_gaps_stats_'+str(m)+'.tex');

