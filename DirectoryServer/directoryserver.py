#pylint: disable=C0111, C0103
import json
import random
from flask import Flask, request
from sqlite3 import *
import requests

app = Flask(__name__)
ip = "10.6.75.8"
servers = ['2000', '3000']



def init_db():
    conn = connect('fileserver')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers(id VARCHAR(20) PRIMARY KEY, port VARCHAR(20))
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS versions(id VARCHAR(20) PRIMARY KEY, version VARCHAR(20))
    ''')
    conn.commit()
    conn.close()

@app.route("/get_file/<path:filepath>")
def get_file(filepath):

    conn = connect('fileserver')
    cursor = conn.cursor()

    directory = filepath.split('/')[0] #get port
    port = cursor.execute('''SELECT port FROM servers WHERE id = ?''', (directory,)).fetchone()

    if port is None:
        return "file doesn't exist", 404

    file_and_version = filepath.rsplit('/', 1) #get file and version
    is_locked = requests.get('http://'+ip+':9000/get_file/'+file_and_version[0]) #check lockserver
    client_version_number = file_and_version[1]
    current_version_number = 0
    if is_locked.status_code == 200:
        current_version_number = cursor.execute('''SELECT version FROM versions WHERE id = ?''', (file_and_version[0],)).fetchone()
        if current_version_number is None:
            return "file doesn't exist", 404
        elif int(client_version_number) == int(current_version_number[0]):
            return "cached copy is up to date", 204
        else:
            response = requests.get('http://'+ip+':'+port[0]+'/get_file/'+file_and_version[0])
            response.headers['new-file-version'] = current_version_number[0]
            return (response.content, response.status_code, response.headers.items())
    else:
        return "file is locked", 409

@app.route("/send_file", methods = ['POST'])
def recv_file():
    conn = connect('fileserver')
    cursor = conn.cursor()

    response = dict(request.files)
    file_name = list(response.keys())[0]
    new_file = list(response.values())[0][0]
    folder = file_name.split('/')[0]
    
    versionNumber = request.headers['File-Version']
    print(versionNumber)
    newVersionNumber = str(int(versionNumber)+1)
    
    port = getPort(cursor, folder)

    response = requests.post('http://'+ip+':'+port+'/send_file', files={file_name: new_file})

    if response.status_code == 200:
        cursor.execute('''INSERT OR REPLACE INTO versions(id, version) VALUES(:id,:version)''', {'id':file_name, 'version':newVersionNumber})

        response.headers['new-file-version'] = newVersionNumber
        conn.commit()
        conn.close()
        return (response.content, response.status_code, response.headers.items())

    return response.content, response.status_code

def getPort(cursor, folder):
    port = cursor.execute('''SELECT port FROM servers WHERE id = ?''', (folder,)).fetchone()

    if port is None:
        new_port = random.choice(servers)
        cursor.execute('''INSERT INTO servers(id, port) VALUES(:id,:port)''', {'id':folder, 'port':new_port})
        port = new_port
    else:
        port = port[0]
    return port


@app.route("/delete_file/<path:filepath>")
def delete_file(filepath):
    conn = connect('fileserver')
    cursor = conn.cursor()

    directory = filepath.split('/')[0] 
    port = getPort(cursor, directory)#get port
    response = requests.get('http://'+ip+':'+port+'/delete_file/'+filepath)
    if response.status_code == 200:
        cursor.execute('''DELETE FROM versions WHERE id = ? ''', (filepath,))
        response = requests.get('http://'+ip+':9000/delete_file/'+filepath)
        conn.commit()
        conn.close()
    else:
        return response
    
    return "file deleted", 200
                    

@app.route("/") #if you want to check that manager is up
def hello():
    return "hello", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
