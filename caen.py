from multiprocessing import Process
from caen_flask import startWeb
if __name__=='__main__':
    from caen_flask import startWeb
    p=Process(target=startWeb)
    p.start()
