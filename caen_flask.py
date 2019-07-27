import subprocess
from flask import Flask, request, redirect
from caen_plotting import makePlots
from save import save
import requests
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler,FileSystemEventHandler,PatternMatchingEventHandler
from multiprocessing import Process
from flask_socketio import SocketIO,send,emit

app = Flask(__name__)
socketio = SocketIO(app)

def execute(cmd):
    subprocess.Popen('cmd',shell=True).communicate()

@app.route('/')
def flask_index():
    return redirect("/admin", code=302)

@app.route('/refresh')
def flask_refresh():
    makePlots()
    return app.send_static_file('index.html')

@app.route('/admin/plot')
def admin_plot():
    makePlots()
    time.sleep(3)
    return redirect("/admin", code=302)

@app.route('/write')
def flaks_write():
    p2=subprocess.Popen('DT5742_write.exe',shell=True)
    response=p2.communicate()
    makePlots()
    return app.send_static_file('index.html')

@app.route('/admin')
def flaks_admin():
    print("The webpage has loaded.")
    return app.send_static_file('admin.html')

def move(dir,micrometers):
    if micrometers in ['-']:
        cmd=f'motor.exe {dir}'
    else:
        try:
            mm=float(micrometers)/1000
            cmd=f'motor.exe {dir} {mm}'
        except:
            print("Failed to parse input.")
            return None
    p2=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    response,err=p2.communicate()
    try:
        position=str(response).split('STARTPOS')[1].split('ENDPOS')[0]
        print(f'{dir} Value exctracted {position}')
        return float(position)
    except:
        print(err)
        return None

@app.route('/move/vertical')
def move_vert():
    distance=request.args['distance']
    position=move('v',distance)
    if position is not None:
        print("Successful movement of motors.")
        return f"{position*1000}", 200
    else:
        print("Error failed to move moters.")
        return "Error", 201

@app.route('/move/horizonal')
def move_horiz():
    distance=request.args['distance']
    position=move('h',distance)
    if position:
        print("Successful movement of motors.")
        return f"{position*1000}", 200
    else:
        print("Error failed to move moters.")
        return "Error", 201

@app.route('/write/refresh')
@app.route('/refresh/write')
def flaks_write_refresh():
    p2=subprocess.Popen('DT5742_write.exe',shell=True)
    p2.communicate()
    makePlots()
    return app.send_static_file('index.html')

@app.route('/save',methods=['POST'])
def execute_save():
    folder=request.form.get('folder','')
    print("Saving to {}".format(folder))
    save(folder)
    return "Success"

@app.route('/updated/filesystem',methods=['GET'])
def updated_filesystem():
    emit('update','',namespace='/', broadcast=True)
    return "Success"

class MyHandler(PatternMatchingEventHandler):
    def on_modified(self, event):
        requests.get("http://localhost/updated/filesystem")
        #print(f'event type: {event.event_type}  path : {event.src_path}')

def startWeb():
    path='E:\\controller\\' #Location of the output of the binary data.
    event_handler = MyHandler('wave_0.dat','',True,True)
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    try:
        socketio.run(app,host='0.0.0.0',port='80',debug=False)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
