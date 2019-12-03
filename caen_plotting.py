
import matplotlib.pyplot as plt
from seaborn import heatmap,color_palette,cubehelix_palette
import math,os,time
from numpy import ones,square
from pandas import DataFrame
from caen_binary import parseBinary,getChan,getFreq
from caen_mapping import Map
from statistics import mean,stdev
import shutil




myColor=cubehelix_palette(10, start=2, rot=0, dark=0, light=.95, reverse=True)
myColor.insert(0,(0,0,1))
myColor=[(0.7019607843137254,0.803921568627451,0.8784313725490196)] # A light shade of blue

def plotEvent(data,event=1,show=True,label=None,config=False):
    if issubclass(type(data[event]),float):
        indexes=range(len(data))
        y=data
    else:
        indexes=range(len(data[event]))
        y=data[event]
    if config:
        freq=getFreq(config) #Gets the main config file.
        x=[i/freq for i in indexes]
    else:
        x=indexes
    plt.plot(x,y,label=label)
    if show: plt.show()

def plotMany(filePath,outDir,title,config=False,limit=10):
    rawData=parseBinary(os.path.abspath(filePath),limit=limit)
    try:
        shutil.rmtree(outDir)
    except:
        pass
    os.mkdir(outDir)
    for i in range(limit):
        plotEvent(rawData,i,config=config,show=False)
        plt.title(title.format(i))
        plt.savefig(os.path.join(outDir,f'evt_{i}.png'))
        plt.clf()


def plotAllChannels(rawData,bounds=None,config=False,title=None,filename="overlay",channel=None,limit=10):
    if issubclass(type(rawData),str):
        rawData=parseBinary(os.path.abspath(rawData),limit=limit)
        print(rawData)
    legend=False
    for chan,d in enumerate(rawData):
        if len(rawData) > 1 and channel is not None and chan is not channel: continue
        deviation=stdev(d)
        if deviation < 100:
            plotEvent(d,show=False,config=config)
        else:
            legend=True
            plotEvent(d,show=False,label="channel {}".format(chan),config=config)
    axes=plt.gca()
    all=flatten(rawData)
    bounds=(min(all),max(all))
    print(bounds)
    axes.set_ylim([bounds[0],bounds[1]])
    if title is None:
        plt.title("Mean Waveform of Each Channel")
    else:
        plt.title(title)
    if config:
        plt.xlabel("Time (microsecconds)")
    else:
        plt.xlabel("Time (#)")
    plt.ylabel("ADC Count (#)")

    if legend:
        plt.legend()
    plt.savefig(f'static/{filename}.png')
    plt.clf()

def plotGrid(img,bounds=None,title='heatmap',length=-1,funcName="Mean"):
    if bounds is not None:
        all=flatten(img)
        bounds=(min(all),max(all))
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

    plt.title("{} Difference in Pulse {} Events from {} ".format(funcName,length,title))
    plt.savefig('static/{}.png'.format(title))
    plt.clf()

def plotDiffHisto(minimums,maximums,bounds):
    extremas=[[big-small for small,big in zip(chan_min,chan_max)] for chan_min,chan_max in zip(minimums,maximums)]
    flat=flatten(extremas)
    bounds=(min(flat),max(flat))
    plotHistograms(extremas,bounds,title="Trace Height on Channel {}")

def plotHisto(channel,nEvents=1000, folder="E:\\controller"):
    startTime=time.time()
    def tick(prefix=""):
        currentTime=time.time()
        duration=currentTime-startTime
        print(f"{prefix} - Duration {duration}")
    tick("importing")
    from pandas import DataFrame
    folder=os.path.abspath(folder)
    files=sorted([(getChan(f),os.path.join(folder,f)) for f in os.listdir(folder) if '.dat' in f and 'wave' in f])
    files=[f[1] for f in files]
    tick(f"Parsing {nEvents}")
    rawData=parseBinary(files[channel],limit=nEvents)
    tick("Processing")
    data=[max(event)-min(event) for event in rawData]
    tick("Plotting")
    plt.hist(data,bins=250)
    tick('saving')
    plt.title(f"Trace Heights on Channel {channel}")
    plt.xlabel("ADC Count (#)")
    plt.ylabel("Count (#)")
    plt.savefig(f'static/special/special_histo_{channel}.png')
    plt.clf()

def plotHistograms(values,bounds,title=None):
    for chan,value in enumerate(values):
        plt.hist(value, bins=100,range=bounds)
        #plt.yscale('log', nonposy='clip')
        if title is None:
            plt.title("Minimum Peak Heights on Channel {}".format(chan))
        else: plt.title(title.format(chan))
        plt.xlabel("ADC Count (#)")
        plt.ylabel("Count (#)")
        plt.savefig('static/histo_{}.png'.format(chan))
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

def genTraces(channel=None,rms=None,limit=20):
    dataPath=os.path.abspath("E:\\controller")
    traceDir=os.path.join(os.path.join(dataPath,'static'),'traces')
    shutil.rmtree(traceDir)
    os.mkdir(traceDir)
    minimums,maximums,rawData = prepareBinary(dataPath,limit)
    bounds=(min(flatten(minimums)),max(flatten(maximums)))
    mapFront=Map("E:\\front_map.txt", True)
    mapBack=Map("E:\\back_map.txt", True)
    nEvents=len(rawData[0])

    filenames=[]
    plt.figure(figsize=(7,4))
    funcName="Mean"
    if rms is not None:
        funcName="RMS"
        rmsValues=[[mean(square(channel[event])) for event in range(nEvents)] for channel in rawData]
    for event in range(nEvents):
        if rms is not None:
            imgFront=mapFront.shape(rmsValues,n=event)
        else:
            imgFront=mapFront.pulseDiff(minimums,maximums,n=event)
            imgBack=mapBack.pulseDiff(minimums,maximums,n=event)
        title=f"Trace of event #{event}"
        wave=getFirstWave(rawData,event)
        plotGrid(imgFront,bounds,f'traces/grid_front_event_{event}',nEvents,funcName=funcName)
        plotGrid(imgBack,bounds,f'traces/grid_back_event_{event}',nEvents,funcName=funcName)
        filename=f"traces/event_{event}"
        plotAllChannels(wave,bounds,title=title,filename=filename,channel=channel)
        filenames.append(f"event_{event}.png")
    return filenames

def getTraces():
    dataPath=os.path.abspath("E:\\controller")
    traceDir=os.path.join(os.path.join(dataPath,'static'),'traces')
    return  [f for f in os.listdir(traceDir) if 'grid' not in f]

def makePlots(nEvents=100,event=None,pulseDifference=True,config='E:\\config.txt',histo=None):
    startTime=time.time()
    def tick(prefix=""):
        currentTime=time.time()
        duration=currentTime-startTime
        print(f"{prefix} - Duration {duration}")
    print("Initialized")
    mapFront=Map("E:\\front_map.txt", True)
    mapBack=Map("E:\\back_map.txt", True)
    tick("Parsed mapping")
    #Map.getBounds(mapFront,mapBack)
    dataPath=os.path.abspath("E:\\controller")
    if histo is not None:
        try:
            limit=int(histo)
            nEvents=limit
        except:
            pass
    minimums,maximums,rawData = prepareBinary(dataPath,nEvents)
    nEvents=len(rawData[0])
    tick("Parsed binary")
    bounds=(min(flatten(minimums)),max(flatten(maximums)))
    title=None
    if event is None:
        print("Plotting many")
        meanWaves=getMeanWaves(rawData)
    else:
        title=f"Trace of event #{event}"
        meanWaves=getFirstWave(rawData,event)
    tick("Extracted waveforms")
    if pulseDifference:
        imgFront=mapFront.pulseDiff(minimums,maximums)
        imgBack=mapBack.pulseDiff(minimums,maximums)
    else:
        imgFront=mapFront.shape(minimums)
        imgBack=mapBack.shape(minimums)
    tick("Processed bounds")
    print("Plot with config?",config)
    plt.figure(figsize=(7,4))
    plotAllChannels(meanWaves,bounds,config,title)
    tick("Plotted waveform")
    plotGrid(imgFront,bounds,'front_heatmap',nEvents)
    plotGrid(imgBack,bounds,'back_heatmap',nEvents)
    tick("Plotted grids")
    if histo is not None:
        plotDiffHisto(minimums,maximums,bounds)
        tick("Plotted histograms")
    print("Plot refreshed.",time.time())

if __name__ == '__main__':
    #genTraces(rms="")
    plotHisto(15,-1)
