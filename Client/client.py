#pylint: disable=C0111, C0103
import json
import requests

def getFile(filename): #ask for work
    response = requests.get('http://10.6.90.53:1000/get_file/'+filename)

    if response.status_code is 200:
        with open("Files/"+filename, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=128):
                fd.write(chunk)
    else:
        print(response)

def uploadFile(filename):
    with open("Files/"+filename, 'rb') as f: 
        response = requests.post('http://10.6.90.53:1000/send_file', files={filename: f})
    print(response.text)

if __name__ == "__main__":
    print(requests.get('http://10.6.90.53:1000'))
    name = str(input("Send a file: "))
    uploadFile(name)
