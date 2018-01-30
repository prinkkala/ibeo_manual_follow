import subprocess
import sys
import json
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import os
from can_reverse_engineer import *

def jsons(lines):
    for line in lines:
        if(hasattr(line, 'decode')):
            line = line.decode('utf-8')
        yield json.loads(line)
        
def ibeo_objects(idc):
    mangler = subprocess.Popen(['./objects_to_json'], stdout=subprocess.PIPE, stdin=idc)
    return jsons(mangler.stdout)
######################################################################################################
kh = 'KH009'
######################################################################################################
path = "/media/tru/Transcend/2017/headway17_auto1/trusas_data_1/{!s}/".format(kh)
object_list = np.load(path +"chosen_object.npy")
#object_list2 = np.load(path +"chosen_object_orig.npy")
"""
blinder_ts =[]
with open("blinder.jsons", "r", encoding="utf-8") as json_file:
    for line in json_file:
        #print(line[1])
        if 'Lifting' in line:
            #print(line)
            ts = re.findall("\d+\.\d+", line)
            ts = float(ts[0])
            blinder_ts.append(ts)
   """         
            
ts_list = np.load(path + "ts_list.npy")
blinder_ts =[]        
for line in open(os.path.join(path, 'blinder.jsons')):

        hdr,data = json.loads(line) #luetaan datapisteitä hederiin ja dataan

        #print(hdr, data)

        if u'controller' in data.keys():
            if data['controller'] == 'Lifting\r\n':
                blinder_ts.append(hdr['ts'])

start = []
end= []
valid_ts =[]
for line in open(os.path.join(path, 'protocol.jsons')):

        hdr,data = json.loads(line) #luetaan datapisteitä hederiin ja dataan

        #print(hdr)

        if u'end_time' in data.keys():
            valid_ts.append((hdr['time'],data['end_time']))
            
del valid_ts[0]

dist_list = []
ts_obj = []
rvel_list = []

dist2_list = []
rvel2_list = []

for obj in object_list:
    ts_obj.append(obj[0])
    dist_list.append((obj[0],obj[1]["distance"]))
    rvel_list.append((obj[0],obj[1]["relative_velocity"]['x']))

rvel_list = np.array(rvel_list)
dist_list = np.array(dist_list)

check_again = []
def onclick(event):
    if event.button == 2:
        xdata = event.xdata
        i = 0
        for ts in ts_list:
            if np.absolute(ts - xdata) < 0.2:
                print("found it!")
                print("timeframe: ", i)
                check_again.append(i)
                break
            i+=1



fig = plt.figure()
plt.title(kh)
plt.ylim(0,160)
#for ts in blinder_ts:
#    plt.axvline(x=ts)

plt.plot(dist_list[:,0], dist_list[:,1], '.-', color = 'y') 
#plt.plot([dist_list[0][0], dist_list[-1][0]], [0,0], color = 'black')
#plt.plot(rvel_list[:,0], rvel_list[:,1], '.', color = 'r')
gps_vs_can_speed(path)

fig.canvas.mpl_connect('button_press_event', onclick)


plt.show()
print("please check again these timeframepoints") 
print(check_again)
