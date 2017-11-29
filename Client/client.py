#pylint: disable=C0111, C0103
import os
import json
import requests

ip = "10.101.20.41"

def getFile(filename): #ask for work
    response = requests.get('http://'+ip+':1000/get_file/'+filename)
    print(response)
    if response.status_code == 200:
        if not os.path.exists(os.path.dirname('./Files/'+filename)):
            os.makedirs(os.path.dirname('./Files/'+filename))
        with open("Files/"+filename, 'wb+') as fd:
            for chunk in response.iter_content(chunk_size=128):
                fd.write(chunk)
    elif response.status_code == 409:
        print(filename, " is currently locked")

def uploadFile(filename):
    with open("Files/"+filename, 'rb') as f:
        response = requests.post('http://'+ip+':1000/send_file', files={filename: f})
    print(response.text)

if __name__ == "__main__":
    print(requests.get('http://'+ip+':1000'))
    done = False
    actiondict = {'r': getFile, 's': uploadFile}
    while not done:
        action = input("Retrieve File: r\nSend File: s\n")
        filename = input("Perform action on which file?\n")
        actiondict[action](filename)
