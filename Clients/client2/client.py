#pylint: disable=C0111, C0103
import os
import json
import requests
from sqlite3 import *


ip = "10.6.75.8"
lockserver = "9000"

def init_db():
    conn = connect('client2')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS versions(id VARCHAR(20) PRIMARY KEY, version VARCHAR(20))
    ''')
    conn.commit()
    conn.close()
    return conn


def getFile(filename): #ask for file
    conn = connect('client2')
    cursor = conn.cursor()
    version_number = cursor.execute('''SELECT version FROM versions WHERE id = ?''', (filename,)).fetchone()
    if version_number is None:
        version_number = '-1'
    else:
        version_number = version_number[0]
    print("current version number is ", version_number)

    response = requests.get('http://'+ip+':1000/get_file/'+filename+'/'+version_number)
    print(response)
    if response.status_code == 200:
        if not os.path.exists(os.path.dirname('./Files/'+filename)): #create folder
            os.makedirs(os.path.dirname('./Files/'+filename))

        with open("Files/"+filename, 'wb+') as fd: # write file
            for chunk in response.iter_content(chunk_size=128):
                fd.write(chunk)

        newVersionNumber = response.headers['new-file-version']

        
        cursor.execute('''INSERT OR REPLACE INTO versions(id, version) VALUES(:id,:version)''', {'id':filename, 'version':newVersionNumber})
        conn.commit()
        conn.close()
        return 1
    elif response.status_code == 204:
        print("current version of file is up to date")
        return 1
    elif response.status_code == 409:
        print(filename, " is currently locked")
        return 0
    elif response.status_code == 404:
        print("no remote file, creating locally")
        return 2

def uploadFile(to_upload):
    conn = connect('client2')
    cursor = conn.cursor()
    version_number = cursor.execute('''SELECT version FROM versions WHERE id = ?''', (to_upload,)).fetchone()
    if version_number is None:
        version_number = '-1'
    else:
        version_number = version_number[0]

    with open("Files/"+to_upload, 'rb') as f:
        file_version = {"file-version": version_number}
        response = requests.post('http://'+ip+':1000/send_file', files={to_upload: f}, headers = file_version)

    newVersionNumber = response.headers['new-file-version']
    print(newVersionNumber)

    cursor.execute('''INSERT OR REPLACE INTO versions(id, version) VALUES(:id,:version)''', {'id':to_upload, 'version':newVersionNumber})
    conn.commit()
    conn.close()

def unlock(to_unlock):
    response = requests.get('http://'+ip+':'+lockserver+'/unlock_file/'+to_unlock)
    if response.status_code == 200:
        print("file unlocked")
    else:
        print("unlock failed")

def delete(to_delete):
    conn = connect('client2')
    cursor = conn.cursor()
    response = requests.get('http://'+ip+':1000/delete_file/'+to_delete)
    if response.status_code == 200:
        os.remove("Files/"+to_delete)
        cursor.execute('''DELETE FROM versions WHERE id = ? ''', (to_delete,))
        conn.commit()
        conn.close()
        print("File deleted")
    else:
        print("File not deleted")

def open_file(name):
    result = getFile(name)
    if result == 1:
        with open("Files/"+name) as new_file:
            print(new_file.read())
    if not result == 0:
        print("write new contents for file")
        to_write = input()
        directory = name.split('/')[0]
        if not os.path.exists("Files/"+directory):
            os.makedirs("Files/"+directory)
        with open("Files/"+name, 'w+') as fd:
            fd.write(to_write)
        uploadFile(name)
        print("file modified")
    else:
        print("file is locked")

if __name__ == "__main__":
    print(requests.get('http://'+ip+':1000'))
    done = False
    init_db()
    actiondict = {'r': getFile, 's': uploadFile, 'u': unlock, 'd':delete, 'o':open_file}
    while not done:
        action = input("Retrieve File: r\nSend File: s\nUnlock File: u\nDelete File: d\nOpen and modify: o")
        file_to_use = input("Perform action on which file?\n")
        actiondict[action](file_to_use)

