
def getChan(filename):
    return int(filename[-7:-4].replace('e','').replace('_',''))

#Parser extractor
def extractFieldInGroup(data,field,key=None):
    if issubclass(type(data),str): data=data.split('\n')
    found=False
    for i,d in enumerate(data):
        if field in d and '#' not in d:
            found=True
            if key is None:
                return d
        if found and key in d:
            return d

def getOffset(filename,config='E:\\config.txt'):
    chan=getChan(filename)
    with open(config,'r') as f:
        configData=f.read().split('\n')
        group1=extractFieldInGroup(configData,'[0]','GRP_CH_DC_OFFSET').split(' ')[-1].split(',')
        group2=extractFieldInGroup(configData,'[1]','GRP_CH_DC_OFFSET').split(' ')[-1].split(',')
        offsets=[float(o) for o in group1+group2]
        dc_offset=offsets[chan]/50
        return dc_offset

def parseBinary(filename, header=True, offset=None, readConfig=True,limit=None, adc=True):
    from numpy import fromfile,dtype
    with open(filename, mode='rb') as f:
        length=1030
        offset=6
        if not header:
            return fromfile(f,dtype=dtype("<f"),count=-1)
        if limit is None:
            print("Limit is None")
            d=fromfile(f,dtype=dtype("<f"),count=-1)
        else:
            d=fromfile(f,dtype=dtype("<f"),count=length*limit)
        trace=[]
        dc_offset=0
        if readConfig:
            dc_offset=getOffset(filename)
        for i in range(len(d)//length):
            if adc:
                trace.append([float(w) for w in d[i*length+offset:(i+1)*length-20]])
            else:
                trace.append([float(w)/(2**12-1)+dc_offset for w in d[i*length+offset:(i+1)*length]])
        return trace

def parseAscii(filename):
    with open(filename,mode='r') as f:
        return [float(n) for n in f.parse().split('\n')[:-1]]
def parse(filename):
    if '.dat' in filename[-4:]: return parseBinary(filename)
    else: return parseAscii(filename)
#MHz
def getFreq(config='E:\\config.txt'):
    freq=[5000,2500,1000,750]
    with open(config,'r') as f:
        configData=f.read().split('\n')
        return freq[int(extractFieldInGroup(configData, 'DRS4_FREQUENCY').split(' ')[-1])]
if __name__ == '__main__':
    print(getFreq())
