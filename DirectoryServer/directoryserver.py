#pylint: disable=C0111, C0103
import json
from flask import Flask, request, send_from_directory
import requests

app = Flask(__name__)
ip = "10.6.86.174"
directory_dict = {
    "pogba":'2000', #server1
    "zlatan":'3000', #server2
    "lockserver":'9000'
}

@app.route("/get_file/<path:filepath>")
def get_file(filepath):
    directory = filepath.split('/')[0] #get port
    file_and_version = filepath.rsplit('/', 1) #get file and version
    is_locked = requests.get('http://'+ip+':'+directory_dict['lockserver']+'/get_file/'+file_and_version[0])
    client_version_number = file_and_version[1]
    current_version_number = 0
    if is_locked.status_code == 200:
        cache = open("Files/cacheversions.txt", 'r')
        versions = cache.readlines()
        for i, line in enumerate(versions):
            details = line.split()
            if details[0] == file_and_version[0]:
                index = i
                current_version_number = details[1].strip('\n')

        if int(client_version_number) == int(current_version_number):
            return "cached copy is up to date", 204
        else:
            response = requests.get('http://'+ip+':'+directory_dict[directory]+'/get_file/'+file_and_version[0])
            response.headers['new-file-version'] = current_version_number
            return (response.content, response.status_code, response.headers.items())
    else:
        return "file is locked", 409

@app.route("/send_file", methods = ['POST'])
def recv_file():
    response = dict(request.files)
    file_name = list(response.keys())[0]
    new_file = list(response.values())[0][0]
    folder = file_name.split('/')[0]
    versionNumber = request.headers['File-Version']
    print(versionNumber)
    newVersionNumber = str(int(versionNumber)+1)
    cache = open("Files/cacheversions.txt", 'r')
    versions = cache.readlines()
    found = False
    for i, line in enumerate(versions):
        details = line.split()
        if details[0] == file_name:
            versions[i] = "%s %s\n" % (details[0], newVersionNumber)
            found = True
    if not found:
        versions.append("%s %s\n" % (details[0], newVersionNumber))

    response = requests.post('http://'+ip+':'+directory_dict[folder]+'/send_file', files={file_name: new_file})

    if response.status_code == 200:
        with open("Files/cacheversions.txt", 'w') as cache:
                for new_line in versions:
                    cache.write("%s" % new_line)
        response.headers['new-file-version'] = newVersionNumber
        return (response.content, response.status_code, response.headers.items())

    return response.content, response.status_code


@app.route("/") #if you want to check that manager is up
def hello():
    return "hello", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
