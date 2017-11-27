#pylint: disable=C0111, C0103
import json
from flask import Flask, request, send_from_directory
import requests

app = Flask(__name__)
ip = "192.168.1.19"
directory_dict = {
    "pogba":'2000', #server1
    "zlatan":'3000' #server2
}

@app.route("/answer", methods=['POST']) #to return answer
def incorporate():
    return "answer", 200

@app.route("/get_file/<path:filepath>")
def get_file(filepath):
    print("hey")
    parts = filepath.split('/')
    response = requests.get('http://'+ip+':'+directory_dict[parts[0]]+'/get_file/'+filepath)
    print(response)
    return response.content, 200

@app.route("/send_file", methods = ['POST'])
def recv_file():
    response = dict(request.files)
    file_name = list(response.keys())[0]
    new_file = list(response.values())[0][0]
    folder, name = file_name.split('/')
    response = requests.post('http://'+ip+':'+directory_dict[folder]+'/send_file', files={file_name: new_file})
    return response.content, 200


@app.route("/") #if you want to check that manager is up
def hello():
    return "hello", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
