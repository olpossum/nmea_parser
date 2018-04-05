import pandas as pd
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime
import numpy as np

fpath = input("enter file path: ")
fpath = os.path.normpath(fpath)
fname = input("Enter file name for nmea log: ")

raw_file = fpath+"\\"+fname

filein = open(raw_file,'r')


data_to_write = {}
list_of_dicts = []

for line in filein:
    #stripped=line.rstrip("\n")
    stripped=line.strip()
    parsed=stripped.split(" - ")
    logtime=parsed[0]
    raw_msg=parsed[1].split(",")
    if raw_msg[0] == '$GPGSV':
        msg_length = len(raw_msg)
        num_msg_total = int(raw_msg[1])
        num_msg_current = int(raw_msg[2])
        num_tracked_sats = int(raw_msg[3])
        last_line_sats = num_tracked_sats - ((num_msg_total -1 ) * 4)
        if num_msg_current < num_msg_total:
            i = 0
            while i < 4:
                data_to_write['datetime'] = logtime
                data_to_write['sat_id'] = raw_msg[4+(4*i)]
                CNR_no_checksum = raw_msg[7+(4*i)].split("*")
                data_to_write['CNR'] = CNR_no_checksum[0]
                list_of_dicts.append(data_to_write)
                i+=1
                data_to_write = {}
                
        elif num_msg_current == num_msg_total:
            i = 0
            while i < last_line_sats:
                data_to_write['datetime'] = logtime
                data_to_write['sat_id'] = raw_msg[4+(4*i)]
                CNR_no_checksum = raw_msg[7+(4*i)].split("*")
                data_to_write['CNR'] = CNR_no_checksum[0]
                list_of_dicts.append(data_to_write)
                i+=1
                data_to_write = {}

df_VTG = pd.DataFrame(list_of_dicts,columns=['datetime','sat_id','CNR'])
df_VTG['datetime'] = pd.to_datetime(df_VTG['datetime'])
df_VTG.replace('',np.nan,inplace=True)
df_VTG = df_VTG.dropna(how='any')
df_VTG['CNR'] = df_VTG['CNR'].str.strip('\n').astype('int')

print(df_VTG)
sat_groups = df_VTG.groupby('sat_id')

fig,ax = plt.subplots()

style_counter=0
for name,group in sat_groups:
    print(group)
    print(name)
    if style_counter <= 6:
        ax.plot_date(group['datetime'],group['CNR'],'o',fillstyle='none',label=name)
    elif style_counter > 6 and style_counter <=13:
        ax.plot_date(group['datetime'],group['CNR'],'s',fillstyle='none',label=name)
    elif style_counter > 13:
        ax.plot_date(group['datetime'],group['CNR'],'^',fillstyle='none',label=name)
    style_counter += 1
        

ax.grid(True)
ax.legend(loc='upper left')
plt.title('GPS NMEA Reported CNR')
plt.ylabel('CNR Value')
plt.xlabel('Date/Time (UTC)')
plt.show()
