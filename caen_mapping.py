import numpy
from statistics import mean
class Map:
    def __init__(self,mapFile,view=False):
        with open(mapFile,'r') as f:
            lines=f.read().split('\n')
            mapping=[l.split(' ') for l in lines]
        a=[len(l) for l in mapping]
        averageColumn=sum(a)/len(a)
        mapping=[m for m in mapping if len(m) >= averageColumn]
        if view:
            print(mapFile)
            for i in mapping:
                print(' '.join(i))
            print("")
        self.columns=max([len(l) for l in mapping])
        self.rows=len(mapping)
        self.mapping=mapping
    def getBounds(*args):
        all=[]
        reduced=[]
        for arr_arr in args:
            for arr in arr_arr.mapping:
                for a in arr:
                    try:
                        all.append(int(a))
                    except:
                        pass
        for item in all:
            if item in reduced:
                print("There is an issue with the mapping.")
                print("The channel, {} appeared twice.".format(item))
                response=""
                while not (response.lower() in ['yes','no','y','n']):
                    response=input("Continue (y/n)? ")
                if response.lower() in ['yes','y']:
                    print("bad idea...")
                    return
                else:
                    quit(-1)
            reduced.append(item)
            

    def shape(self,minimums):
        img=[[-1 for i in range(self.columns)] for j in range(self.rows)]
        for j in range(self.rows):
            for i in range(self.columns):
                try:
                    chan=int(self.mapping[j][i])
                    img[j][i]=mean(minimums[chan])
                except:
                    img[j][i]=numpy.nan
        return img
