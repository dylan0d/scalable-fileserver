#pylint: disable=C0111, C0103
import json
from flask import Flask, request, send_from_directory
import requests

app = Flask(__name__)
ip = "10.101.20.41"
directory_dict = {
    "pogba":'2000', #server1
    "zlatan":'3000', #server2
    "lockserver":'9000'
}

@app.route("/get_file/<path:filepath>")
def get_file(filepath):
    parts = filepath.split('/')
    is_locked = requests.get('http://'+ip+':'+directory_dict['lockserver']+'/get_file/'+filepath)
    print(is_locked.status_code)
    if is_locked.status_code == 200:
        response = requests.get('http://'+ip+':'+directory_dict[parts[0]]+'/get_file/'+filepath)
        return response.content, response.status_code
    else:
        return "file is locked", 409

@app.route("/send_file", methods = ['POST'])
def recv_file():
    response = dict(request.files)
    file_name = list(response.keys())[0]
    new_file = list(response.values())[0][0]
    folder = file_name.split('/')[0]
    response = requests.post('http://'+ip+':'+directory_dict[folder]+'/send_file', files={file_name: new_file})
    return response.content, 200


@app.route("/") #if you want to check that manager is up
def hello():
    return "hello", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
