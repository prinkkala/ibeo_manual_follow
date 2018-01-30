import subprocess
import sys
import json
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
import os

def jsons(lines):
    for line in lines:
        if(hasattr(line, 'decode')):
            line = line.decode('utf-8')
        yield json.loads(line)

def ibeo_objects(idc):
    mangler = subprocess.Popen(['./objects_to_json'], stdout=subprocess.PIPE, stdin=idc)
    return jsons(mangler.stdout)


class Index(object):
    def __init__(self, objects_list, ts_list, path):
        self.ind = 0
        self.chosen_id = None
        self.objects_list = objects_list
        self.max = len(ts_list)
        self.path = path
        
    def next(self):
        if self.chosen_id != None:
            objs = self.objects_list[self.ind]['objects']
            for obj in objs:
                if obj['id'] == i.chosen_id[0]:
                    if obj['contour'][0]['x'] < 300:                    
                       obj['chosen_id'] = self.chosen_id
            #print(self.objects_list[self.ind])
        if self.ind%5000 == 0:
            self.save_things()
            if self.ind%10000 == 0:
                self.save_object()

        self.ind += 1


    def prev(self):
        if self.ind == 0:
            return
        objs = self.objects_list[self.ind]['objects']
        for obj in objs:
            obj.pop("chosen_id", None)
        #self.objects_list[self.ind].pop("chosen_id", None)
        #print(self.objects_list[self.ind])
        self.ind -= 1
        
    def set_ind(self, i):
        self.ind = i
        
        
    def chosen_true_id(self, point):
        objs = objects_list[self.ind]['objects']
        for obj in objs:
            xys = [(-1.0*c['y'], c['x']) for c in obj['contour']] #!! x,y -> y,x
            if point in xys:
                age = obj['age']
                idi = obj['id']
                if self.chosen_id != None and self.chosen_id[0] == idi and np.absolute(self.chosen_id[1] - age) < 40:
                        print("HISTORY ERROR (keeping the chosen id)")
                else:
                    self.chosen_id = tuple((idi, i.ind-age))
                 
        
    def find_true_ids(self): #true ids of frame
            objs = objects_list[self.ind]['objects']
            true_id_tmp = []
            for obj in objs:
                age = obj['age']
                idi = obj['id']
                true_id = tuple((idi, i.ind-age))
                true_id_tmp.append(true_id)
            return true_id_tmp
            
    def next_true_id(self):
            tmp_chosen_id = self.chosen_id
            self.prev_true_id()
            self.chosen_id = tmp_chosen_id
            print("saving this object and finding next frame without chosen object")
            while True:
                if self.ind >= self.max -1:
                    break
                id_list = self.find_true_ids()
                found = False
                for t_id in id_list:   
                    if self.chosen_id[0] == t_id[0] and np.absolute(self.chosen_id[1] - t_id[1]) < 40:
                        if np.absolute(self.chosen_id[1] - t_id[1]) >0:
                            print("HISTORY ERROR", t_id, self.chosen_id)
                        self.next()
                        found = True
                #if there is just 1 frame, that skips the object, this skips over it
                if not found:
                    self.next()
                    id_list = self.find_true_ids()
                    for t_id in id_list:   
                        if self.chosen_id[0] == t_id[0] and np.absolute(self.chosen_id[1] - t_id[1]) < 40:
                            self.next()
                            found = True
                            print("skipped frame; found chosen_id again")
                    if not found:
                        self.next()
                        id_list = self.find_true_ids()
                        for t_id in id_list:   
                            if self.chosen_id[0] == t_id[0] and np.absolute(self.chosen_id[1] - t_id[1]) < 50:
                                self.next()
                                found = True
                                print("skipped 2 frames; found chosen_id again")
                    
                        if not found:
                            self.prev()
                            self.prev()
                            self.chosen_id = None
                            break
                
    def prev_true_id(self):
            #print("finding previous frame without chosen object") 
            while True:
                id_list = self.find_true_ids()
                found = False
                for t_id in id_list:   
                    if self.chosen_id[0] == t_id[0] and np.absolute(self.chosen_id[1] - t_id[1]) < 50:
                        self.prev()
                        found = True
                if not found:
                    self.prev()
                    id_list = self.find_true_ids()
                    for t_id in id_list:   
                        if self.chosen_id[0] == t_id[0] and np.absolute(self.chosen_id[1] - t_id[1]) < 50:
                            self.prev()
                            found = True
                            print("skipped frame; found chosen_id again")
                    if not found:
                        self.prev()
                        id_list = self.find_true_ids()
                        for t_id in id_list:   
                            if self.chosen_id[0] == t_id[0] and np.absolute(self.chosen_id[1] - t_id[1]) < 50:
                                self.prev()
                                found = True
                                print("skipped 2 frames; found chosen_id again")
                    
                        if not found:
                            self.next()
                            self.next()
                            self.chosen_id = None
                            break
                if self.ind == 0:
                    print("index = 0")
                    break
                    
    def none_chosen(self):
        self.chosen_id = None
        
    def get_objects_list(self):
            return self.objects_list
            
    def save_things(self):
            np.save(self.path +"objects_list.npy", self.get_objects_list())
            print("objects.npy saved")

            
    def save_object(self):
        j = 0
        chosen_object = []
        new_objects = self.get_objects_list()
        print("calculating distance for chosen_object.npy")
        while j < len(ts_list):
            for obj in new_objects[j]['objects']:
                if "chosen_id" in obj.keys(): 
                    obj_dist_list = []
                    for coord in (obj['contour']):
                        x = coord['x']
                        y = coord['y']
                        obj_dist_list.append(np.linalg.norm([x,y]))
                    dist = np.nanmin(np.array(obj_dist_list))
                    obj["distance"] = dist
                    chosen_object.append((ts_list[j], obj))
                    continue                    
            j+=1
        np.save(path +"chosen_object.npy", chosen_object)
        print("chosen_object.npy saved")



class PickerBrowser(object):
        #are there many or just one picker browser?
    def __init__(self, locations):
        print("init")
        self.locations = locations
        #subplot_kw = dict(xlim=(-20, 20), ylim=(-10,160), autoscale_on=False)
        #self.fig, self.ax = plt.subplots(subplot_kw=subplot_kw)

        #self.text = self.ax.text(0.05, 0.95, 'selected: none',
                            #transform=self.ax.transAxes, va='top')#?needed?
        #self.selected = None

        
    def onpress(self, event):
        #print("onpress")
        if event.key not in ('n', 'b', 'm', 'v', '1', '5', '0', 'q','t', 'å', 'j', '6'):
            print("wrong key")
            return
        if event.key == 'n':
            i.next()
        elif event.key == 'b':
            i.prev()
        elif event.key == 'm':
            i.next_true_id()
        elif event.key == 'v':
            i.prev_true_id()
        elif event.key == '1':
            for asd in range(10):        
                i.next()
        elif event.key == '5':
            for asd in range(50):        
                i.next()
        elif event.key == '0':       
            i.none_chosen()
        elif event.key == 'q':
            for asd in range(10):        
                i.prev()
        elif event.key == 't':
            for asd in range(50):        
                i.prev()
        elif event.key == 'å':        
            i.save_things()
            i.save_object()
        elif event.key == 'j':
            fast_forward()
        elif event.key == '6':
            forward_auto()
        plt.close()
    

        
    
    def onpick(self, event):
        pointer = event.artist
        xdata = pointer.get_xdata()
        ydata = pointer.get_ydata()
        ind = 0 #choosing just 1 point under click
        self.pick_point = tuple((xdata[ind], ydata[ind])) #turha?
        i.chosen_true_id(self.pick_point)
        print("onpick", i.chosen_id)
    
        
        #self.fig.canvas.draw() #TODO
    def new_fig(self):
        #subplot_kw = dict(xlim=(-38, 38), ylim=(-10,170), autoscale_on=False)
        #self.fig, self.ax, self.ax2 = plt.subplots(figsize = (12,10),subplot_kw=subplot_kw, sharex=True)
        self.fig = plt.figure(figsize = (12,9))
        self.ax = plt.subplot(211)
        draw_map(self.locations, i.ind)
        self.ax2 = plt.subplot(212, xlim=(-45, 45), ylim=(-10,260),autoscale_on=False)
        self.line = None #Turha?
        
    def connect(self):
        self.fig.canvas.mpl_connect('key_press_event', self.onpress)
        self.line.figure.canvas.mpl_connect('pick_event', self.onpick)
        
    def get_line(self, line):
            self.line = line
            
            
def location_reader(path, ibeo_ts):

    latitude = []
    longitude = []
    altitude = []
    ts = []

    for line in open(os.path.join(path, 'location.jsons')):

            hdr,data = json.loads(line) #luetaan datapisteitä hederiin ja dataan

            if 'mLatitude' in data.keys():
                latitude.append(data['mLatitude'])
                longitude.append(data['mLongitude'])
                altitude.append(data['mAltitude'])
                ts.append(hdr['ts'])
    locations = [ts, longitude, latitude, altitude]
    locations = interp_loc_ibeo(ibeo_ts, locations)
    return locations


def interp_loc_ibeo(ibeo_ts, locations):
    #interp locations[0] -> ibeo_ts
    
    interp_long = interp1d(locations[0], locations[1], axis = 0,  bounds_error=False)
    interp_lat = interp1d(locations[0], locations[2], axis = 0,  bounds_error=False)
    interp_alt = interp1d(locations[0], locations[3], axis = 0,  bounds_error=False)
    new_data = []
    locations[0] = ibeo_ts
    locations[1] = interp_long(ibeo_ts)
    locations[2] = interp_lat(ibeo_ts)
    locations[3] = interp_alt(ibeo_ts)
    
    return locations
    

def draw_map(locations, indx):
    start = int(len(locations[1])/2 - 1200) 
    stop = int(len(locations[1])/2 + 1200)
    longitude_short = locations[1][start:stop]
    latitude_short = locations[2][start:stop]
    longitude = locations[1]
    latitude = locations[2]
    plt.plot(longitude_short, latitude_short, '.', alpha = 0.1, color = 'g')
    plt.plot(longitude[indx], latitude[indx], '.', linewidth = 3.0, color = 'r')
        
        
def where_were_we(objects_list):
    i = 0
    last_chosen_i = 0
    while i < len(objects_list):
        objs = objects_list[i]['objects']
        for obj in objs:
            if "chosen_id" in obj.keys():
                last_chosen_i = i
                print("found_one!", i)
        i+=1
    return last_chosen_i
        
if __name__ == '__main__':

    ##########################################################################change these#########################################################################
    kh = 'KH009'
    starting_frame = 6876
    #[6875, 6885, 8514, 8530]



    unfinished = False
    ##########################################################################change these#########################################################################
    
    path = "/media/tru/Transcend/2017/headway17_auto1/trusas_data_1/{!s}/".format(kh)
    try:
        ts_list = np.load(path + "ts_list.npy")
        objects_list = np.load(path +"objects_list.npy")
        print("raw data loaded")
    except:
        objects = None
        with open(path + 'ibeo.idc') as ibeo_data:
            objects = ibeo_objects(ibeo_data)
        objects = iter(objects)
        #print(list(objects))
        ts0 = None
        ts_list =[]
        objects_list = []
        for hdr, objs in objects:
            ts = hdr['ts']
            ts_list.append(ts)
            objects_list.append(objs)
        np.save(path +"ts_list.npy", ts_list)
        np.save(path +"objects_list.npy", objects_list)
        print("raw data saved")
        
    locations = location_reader(path, ts_list)
    
    i = Index(objects_list, ts_list, path)
    #plt.ion()
    plot_frame = PickerBrowser(locations)
    ts0 = ts_list[0]
    

    

    #TODO please be aware of this!
    i.set_ind(starting_frame)
    
    if unfinished and starting_frame == 0:
        i.set_ind(where_were_we(objects_list))
    
    def fast_forward():
        plt.cla()
        #last_y = None
        while True:
            i.chosen_id = None
            plot_frame.ax = plt.subplot(211)
            plt.cla()
            draw_map(plot_frame.locations, i.ind)
            plot_frame.ax2 = plt.subplot(212, xlim=(-45, 45), ylim=(-10,260),autoscale_on=False)
            plot_frame.line = None #Turha?
            
            objs = objects_list[i.ind]['objects']
            for obj in objs:
                xys = [(c['x'], -1.0*c['y']) for c in obj['contour']]
                y, x = zip(*xys)    #swich x and y to right coodrinates
                line, = plt.plot(x, y, '.-',linewidth=2.5, picker=5) 
                plot_frame.get_line(line) #FIGURE UPDATE IS PRACTICALLY HERE
                #choosing every object in certain area
                if "chosen_id" not in obj.keys(): 
                        y = np.mean(y)
                        x = np.mean(x)
                        #if last_y == None:
                        #    last_y = 150
                        if y > 80 and y < 300 and np.absolute(x) < 8: 
                            age = obj['age']
                            idi = obj['id']
                            true_id = tuple((idi, i.ind-age))
                            i.chosen_id = true_id
                            #last_y = y
                            print(i.ind, i.chosen_id, x,y)
                            continue
                            #TODO tje last chosen object will be chosen id... is there a way to distinguis witch is better  one?55

            if i.ind +1 >=len(ts_list):
                break
            plot_frame.ax2.set_xlim(-45, 45)
            plot_frame.ax2.set_ylim(-10,260)
            plot_frame.connect()
            #plt.suptitle(kh)
            text = plot_frame.ax2.text(0.6, 0.95, str(i.ind) + "\n" + str(round(100.0*i.ind/len(ts_list), 1)) + " %",
                            transform=plot_frame.ax.transAxes, va='top')
            plt.pause(0.022)
            print(i.ind, i.chosen_id)
            plt.cla()
            i.next()
            
    def forward_auto():
        #last_y = None
        stop = i.ind + 50
        while i.ind < stop:
            i.chosen_id = None
            objs = objects_list[i.ind]['objects']
            for obj in objs:
                xys = [(c['x'], -1.0*c['y']) for c in obj['contour']]
                y, x = zip(*xys)    #swich x and y to right coodrinates
                #choosing every object in certain area
                if "chosen_id" not in obj.keys(): 
                        y = np.mean(y)
                        x = np.mean(x)
                        #if last_y == None:
                        #    last_y = 150
                        if y > 80 and y < 300 and np.absolute(x) < 8: #and np.absolute(y-last_y) < 70: 
                            age = obj['age']
                            idi = obj['id']
                            true_id = tuple((idi, i.ind-age))
                            i.chosen_id = true_id
                            #last_y = y
                            print(i.ind, i.chosen_id, x,y)
                            continue

            if i.ind +1 >=len(ts_list):
                break
            i.next()

        
    while i.ind < len(ts_list):
  
        plot_frame.new_fig()
        objs = objects_list[i.ind]['objects']
        for obj in objs:
            xys = [(c['x'], -1.0*c['y']) for c in obj['contour']]
            x, y = zip(*xys)
            line, = plt.plot(y, x, '.-',linewidth=2., picker=5) #swich x and y places
            plot_frame.get_line(line) #FIGURE UPDATE IS PRACTICALLY HERE

        if i.ind +1 >=len(ts_list):
            break
        plot_frame.connect()
        plt.suptitle(kh)
        text = plot_frame.ax2.text(0.6, 0.95, str(i.ind) + "\n" + str(round(100.0*i.ind/len(ts_list), 1)) + " %",
                        transform=plot_frame.ax.transAxes, va='top')
        plt.show()

        print(i.ind, i.chosen_id)

        
    print("The end")
    plt.close()

    i.save_things()
    i.save_object()


