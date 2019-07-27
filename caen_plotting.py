
import matplotlib.pyplot as plt
from seaborn import heatmap,color_palette,cubehelix_palette
import math,os,time
from numpy import ones
from pandas import DataFrame
from caen_binary import parseBinary,getChan
from caen_mapping import Map
from statistics import mean,stdev


myColor=cubehelix_palette(10, start=2, rot=0, dark=0, light=.95, reverse=True)
myColor.insert(0,(0,0,1))
myColor=[(0.7019607843137254,0.803921568627451,0.8784313725490196)] # A light shade of blue

def plotEvent(data,event=1,show=True,label=None):
    if issubclass(type(data[event]),float):
        plt.plot(range(len(data)),data,linestyle="None",marker=".",label=label)
    else:
        plt.plot(range(len(data[event])),data[event],linestyle="None",marker=".",label=label)
    if show: plt.show()

def plotAllChannels(rawData,bounds):
    legend=False
    for chan,d in enumerate(rawData):
        deviation=stdev(d)
        if deviation < 100:
            plotEvent(d,show=False)
        else:
            legend=True
            plotEvent(d,show=False,label="channel {}".format(chan))
    axes=plt.gca()
    all=flatten(rawData)
    bounds=(min(all),max(all))
    print(bounds)
    axes.set_ylim([bounds[0],bounds[1]])
    plt.title("Mean Waveform of Each Channel")
    plt.xlabel("Time (#)")
    plt.ylabel("ADC Count (#)")

    if legend:
        plt.legend()
    plt.savefig('static/overlay.png')
    plt.clf()

def plotGrid(img,bounds=None,title='heatmap',length=-1):
    if bounds is not None:
        lowerBound,upperBound=bounds
        rows=len(img)
        columns=len(img[0])
        mask=DataFrame(img).isnull()
        background=DataFrame(ones((rows,columns)))
        #heatmap(background, linewidth=0.5,vmin=math.floor(lowerBound),vmax=math.ceil(upperBound),square=True,cbar=False,cmap=myColor)
        #heatmap(img, linewidth=0.5,vmin=math.floor(lowerBound),vmax=math.ceil(upperBound),annot=True,square=True,fmt='g',mask=mask)
        print(lowerBound,upperBound)
        heatmap(background, linewidth=0.5,vmin=lowerBound,vmax=upperBound,square=True,cbar=False,cmap=myColor)
        heatmap(img, linewidth=0.5,vmin=lowerBound,vmax=upperBound,annot=True,square=True,fmt='g',mask=mask)
    else:
        sns.heatmap(img, linewidth=0.5,annot=True,square=True,cmap=myColor)
    plt.title("Mean Min Pulse {} Events from {} ".format(length,title))
    plt.savefig('static/{}.png'.format(title))
    plt.clf()

def plotHistograms(minimums,bounds):
    for chan,peaks in enumerate(minimums):
        plt.hist(peaks, bins=100,range=bounds)
        plt.yscale('log', nonposy='clip')
        plt.title("Minimum Peak Heights on Channel {}".format(chan))
        plt.xlabel("ADC Count (#)")
        plt.ylabel("Count (#)")
        plt.savefig('static/pmin_{}.png'.format(chan))
        plt.clf()

def getMeanWave(waveforms):
    transpose=[ [] for _ in waveforms[0] ]
    for waveform in waveforms:
        for i,w in enumerate(waveform):
            transpose[i].append(w)
    return [mean(w) for w in transpose]

def getFirstWave(waveforms,n=0):
    return [channel[n] for channel in waveforms]
def getMeanWaves(rawData):
    return [getMeanWave(waveforms) for waveforms in rawData]

def prepareBinary(folder,nEvents=100):
    print("Parsing {} events".format(nEvents))
    files=sorted([(getChan(f),os.path.join(folder,f)) for f in os.listdir(folder) if '.dat' in f and 'wave' in f])
    files=[f[1] for f in files]
    rawData=[parseBinary(f,limit=nEvents) for f in files]
    print("Number of channels", len(rawData))
    minimums=[ [min(waveform) for waveform in channel] for channel in rawData]
    maximums=[ [max(waveform) for waveform in channel] for channel in rawData]
    #print(minimums[13])
    return minimums,maximums,rawData

def flatten(arr_arr):
    all=[]
    for arr in arr_arr:
        for a in arr:
            all.append(a)
    return all
def makePlots(nEvents=100):
    print("Initialized")
    mapFront=Map("E:\\front_map.txt", True)
    mapBack=Map("E:\\back_map.txt", True)
    #Map.getBounds(mapFront,mapBack)
    dataPath=os.path.abspath("E:\\controller")
    minimums,maximums,rawData = prepareBinary(dataPath,nEvents)
    bounds=(min(flatten(minimums)),max(flatten(maximums)))
    meanWaves=getFirstWave(rawData,0)
    imgFront=mapFront.shape(minimums)
    imgBack=mapBack.shape(minimums)
    plotAllChannels(meanWaves,bounds)
    plotGrid(imgFront,bounds,'front_heatmap',nEvents)
    plotGrid(imgBack,bounds,'back_heatmap',nEvents)
    plotHistograms(minimums,bounds)
    print("Plot refreshed.",time.time())

class PlotGenerator:
    def __init__(nEvents=100):
        self.nEvents=nEvents
        self.stage=0
    def next(self):
        if self.stage==0:
            self.mapFront=Map("E:\\front_map.txt", True)
            self.mapBack=Map("E:\\back_map.txt", True)
            self.bounds=Map.getBounds(self.mapFront,self.mapBack)
            self.bounds=(0,2**12)
        elif self.stage==1:
            self.dataPath=os.path.abspath("E:\\controller")
            self.minimums,self.rawData = prepareBinary(self.dataPath,self.nEvents)
        elif self.stage==2:
            self.meanWaves=getMeanWaves(self.rawData)
        elif self.stage==3:
            self.imgFront=self.mapFront.shape(self.minimums)
            self.imgBack=self.mapBack.shape(self.minimums)
        elif self.stage==4:
            plotAllChannels(self.meanWaves,self.bounds)
        elif self.stage==5:
            plotGrid(self.imgFront,self.bounds,'front_heatmap',self.nEvents)
            plotGrid(self.imgBack,self.bounds,'back_heatmap',self.nEvents)
        elif self.stage==6:
            plotHistograms(self.minimums,self.bounds)
        else:
            return None
        self.stage+=1
        return self.stage

if __name__ == '__main__':
    pass
