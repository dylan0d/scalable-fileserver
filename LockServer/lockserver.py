#pylint: disable=C0111, C0103
import json
from flask import Flask

app = Flask(__name__)


@app.route("/get_file/<path:filepath>")
def checkFile(filepath):
    lockedFile = open("Files/lockedlist.txt", 'r')
    files = lockedFile.readlines()
    for i, line in enumerate(files):
        if not (line == "" or line == "\n"):
            details = line.split()
            if details[0] == filepath:
                if details[1] == '1':
                    return "locked", 409
                else:
                    files[i] = details[0] + " 1\n"
    lockedFile = open("Files/lockedlist.txt", 'w')
    for new_line in files:
        lockedFile.write("%s" % new_line)
    return "open", 200


@app.route("/unlock_file/<path:filepath>")
def unlockFile(filepath):
    lockedFile = open("Files/lockedlist.txt", 'r')
    files = lockedFile.readlines()
    found = False
    for i, line in enumerate(files):
        if not (line == "" or line == "\n"):
            details = line.split()
            if details[0] == filepath:
                files[i] = details[0] + " 0\n"
                found = True
                break
    if not found:
        files.append("%s %s\n" % (filepath, '0'))
    lockedFile = open("Files/lockedlist.txt", 'w')
    for new_line in files:
        lockedFile.write("%s" % new_line)
    return "unlocked", 200

@app.route("/delete_file/<path:filepath>")
def delete_file(filepath):
    lockedFile = open("Files/lockedlist.txt", 'r')
    files = lockedFile.readlines()
    for i, line in enumerate(files):
        details = line.split()
        if details[0] == filepath:
            files.remove(line)
    with open("Files/lockedlist.txt", 'w') as lockedFile:
        for new_line in files:
            lockedFile.write("%s" % new_line)
    
    return "file deleted", 200



@app.route("/") #if you want to check that manager is up
def hello():
    return "hello", 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
