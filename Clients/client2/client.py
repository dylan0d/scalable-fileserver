#pylint: disable=C0111, C0103
import os
import json
import requests

ip = "192.168.1.19"
lockserver = "9000"

def getVersionNumber(filename, versions):
    version_number = '-1'
    for i, line in enumerate(versions):
        if not (line == "" or line == "\n"):
            details = line.split()
            if details[0] == filename:
                version_number = details[1].strip('\n')
                return version_number
    return version_number

def getFile(filename): #ask for file
    cache = open("Files/cacheversions.txt", 'r')
    versions = cache.readlines()
    version_number = getVersionNumber(filename, versions)

    response = requests.get('http://'+ip+':1000/get_file/'+filename+'/'+version_number)
    print(response)
    if response.status_code == 200:
        if not os.path.exists(os.path.dirname('./Files/'+filename)): #create folder
            os.makedirs(os.path.dirname('./Files/'+filename))

        with open("Files/"+filename, 'wb+') as fd: # write file
            for chunk in response.iter_content(chunk_size=128):
                fd.write(chunk)

        newVersionNumber = response.headers['new-file-version']
        
        found = False
        for i, line in enumerate(versions): #update version numbers
            details = line.split()
            if details[0] == filename:
                versions[i] = ("%s %s\n" % (details[0], str(newVersionNumber)))
                found = True
                break

        if not found:
            versions.append("%s %s\n" % (filename, str(newVersionNumber)))
        with open("Files/cacheversions.txt", 'w') as cache:
            for new_line in versions:
                cache.write("%s" % new_line)
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
    cache = open("Files/cacheversions.txt", 'r')
    versions = cache.readlines()
    version_number = getVersionNumber(to_upload, versions)

    with open("Files/"+to_upload, 'rb') as f:
        file_version = {"file-version": version_number}
        response = requests.post('http://'+ip+':1000/send_file', files={to_upload: f}, headers = file_version)

    newVersionNumber = response.headers['new-file-version']
    print(newVersionNumber)
    found = False
    for i, line in enumerate(versions):
        if not(line == "" or line == '\n'):
            details = line.split()
            print(details)
            if details[0] == to_upload:
                versions[i] = "%s %s\n" % (details[0], newVersionNumber)
                found = True
                break
    if not found:
        versions.append("%s %s\n" % (to_upload, newVersionNumber))
    print("got here")
    print(versions)
    cache = open("Files/cacheversions.txt", 'w')
    for new_line in versions:
        cache.write("%s" % new_line)

def unlock(to_unlock):
    response = requests.get('http://'+ip+':'+lockserver+'/unlock_file/'+to_unlock)
    if response.status_code == 200:
        print("file unlocked")
    else:
        print("unlock failed")

def delete(to_delete):
    response = requests.get('http://'+ip+':1000/delete_file/'+to_delete)
    if response.status_code == 200:
        os.remove("Files/"+to_delete)
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
    actiondict = {'r': getFile, 's': uploadFile, 'u': unlock, 'd':delete, 'o':open_file}
    while not done:
        action = input("Retrieve File: r\nSend File: s\nUnlock File: u\nDelete File: d\nOpen and modify: o")
        file_to_use = input("Perform action on which file?\n")
        actiondict[action](file_to_use)

