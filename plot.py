from caen_plotting import makePlots
if __name__=='__main__':
    import sys
    if len(sys.argv) == 2:
        makePlots(int(sys.argv[1]))
    else:
        makePlots(100)
