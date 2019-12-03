from caen_plotting import makePlots
if __name__=='__main__':
    import sys
    if len(sys.argv) == 2:
        makePlots(int(sys.argv[1]),config='E:\\config.txt',histo=True)
    else:
        makePlots(100,config='E:\\config.txt',histo=True)
