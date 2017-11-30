#pylint: disable=C0111, C0103
import os
import json
import requests
from flask import Flask, request, send_from_directory
lockserver = '9000'
ip = "10.101.20.40"


app = Flask(__name__)

@app.route("/get_file/<path:path>")
def get_file(path):
    return send_from_directory('./Files', path), 200

@app.route("/send_file", methods = ['POST'])
def recv_file():
    response = dict(request.files)
    file_name = list(response.keys())[0]
    new_file = list(response.values())[0][0].read()
    if not os.path.exists(os.path.dirname('./Files/'+file_name)):
        print("creating directory")
        os.makedirs(os.path.dirname('./Files/'+file_name))
    with open("Files/"+file_name, 'wb+') as fd:
        print("writing file")
        fd.write(new_file)
    updated_lock = False
    while not updated_lock:
        response = requests.get('http://'+ip+':'+lockserver+'/unlock_file/'+file_name)
        updated_lock = response.status_code == 200

    return "file received", 200

@app.route("/delete_file/<path:filepath>")
def delete_file(filepath):
    response = requests.get('http://'+ip+':'+lockserver+'/delete_file/'+filepath)
    if response.status_code == 200:
        os.remove("Files/"+filepath)
        return "file deleted", 200
    else:
        print("broke at server")
        return "file not deleted", 500

@app.route("/") #if you want to check that manager is up
def hello():
    return "hello", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
