from multiprocessing import Process
from caen_flask import startWeb

if __name__=='__main__':
    from caen_flask import startWeb
    p=Process(target=startWeb)
    p.start()
    #p2=subprocess.Popen('start firefox localhost:8888',shell=True)
