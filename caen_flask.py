import subprocess
from flask import Flask, request, redirect, render_template
from caen_plotting import makePlots,genTraces,getTraces,plotHisto,plotAllChannels,plotMany
from caen_binary import parseBinary
from save import save
import requests
import time,os
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

@app.after_request
def add_header(r):
    r.cache_control.no_cache=True
    return r

@app.route('/refresh')
def flask_refresh():
    makePlots()
    return app.send_static_file('index.html')

@app.route('/admin/plot')
def admin_plot():
    event=request.args.get('n',None)
    if event is not None:
        event=int(event)
    histo=request.args.get('histo',None)
    makePlots(event=event,histo=histo)
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

@app.route('/traces')
@app.route('/admin/traces')
def get_traces():
    filenames=getTraces()
    return render_template('waveforms.html',traces=filenames)
@app.route('/traces/plot')
@app.route('/admin/traces/plot')
def plot_traces():
    channel=request.args.get('channel',None)
    if channel is not None:
        channel=int(channel)
    rms=request.args.get('rms',None)
    filenames=genTraces(channel,rms=rms,limit=10)
    return redirect("/traces", code=302)


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
        err=err.decode('utf-8')
        print(err)
        if 'Device is not connected' in err:
            return 'Motor Error: Could not connect. Needs to be power cycled.'
        elif 'requested position' in err:
            return 'Motor Error: Requested position is out of bounds.'
        return "Motor Error: Unknown"
@app.route('/histo/<chan>')
def plot_special_histo(chan):
    plotHisto(int(chan),40000)
    return render_template('special_histo.html',channel=chan)

@app.route('/archive/<name>/wave/<chan>')
def archive_wave(name,chan):
    folder=os.path.join("E:\\data\\",name)
    binary=os.path.join(folder,'binary')
    config=os.path.join(folder,'meta')
    limit=request.args.get('limit',50)
    outDir='static/special/wave'
    plotMany(os.path.join(binary,f'wave_{chan}.dat'),outDir,'event {}',config=os.path.join(config,'config.txt'),limit=limit)
    filenames=os.listdir(outDir)
    return render_template('special_wave.html',traces=filenames)


@app.route('/archive/<name>/histo/<chan>')
def archive_histo(name,chan):
    folder=os.path.join(os.path.join("E:\\data\\",name),'binary')
    plotHisto(int(chan),40000,folder)
    return render_template('special_histo.html',channel=chan)

@app.route('/move/vertical')
def move_vert():
    distance=request.args['distance']
    position=move('v',distance)
    print(position)
    if issubclass(type(position),float):
        print("Successful movement of motors.")
        return f"{position*1000}", 200
    else:
        print("Error failed to move moters.")
        return position, 201

@app.route('/move/horizonal')
def move_horiz():
    distance=request.args['distance']
    position=move('h',distance)
    if issubclass(type(position),float):
        print("Successful movement of motors.")
        return f"{position*1000}", 200
    else:
        print("Error failed to move moters.")
        return position, 201

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

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        requests.get("http://localhost/updated/filesystem")
        #print(f'event type: {event.event_type}  path : {event.src_path}')

def startWeb():
    path='E:\\controller' #Location of the output of the binary data.
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    try:
        socketio.run(app,host='0.0.0.0',port='80',debug=False)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
  
