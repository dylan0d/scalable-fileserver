#pylint: disable=C0111, C0103
from sqlite3 import *
from flask import Flask

app = Flask(__name__)

def init_db():
    conn = connect('lockserver')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locked_status(id VARCHAR(20) PRIMARY KEY, locked VARCHAR(1))
    ''')
    conn.commit()
    conn.close()
    return conn

@app.route("/get_file/<path:filepath>")
def checkFile(filepath):
    conn = connect('lockserver')
    cursor = conn.cursor()
    locked = cursor.execute('''SELECT locked FROM locked_status WHERE id = ?''', (filepath,)).fetchone()
    print(filepath, " is ", locked)
    if locked is None or locked[0] is '0':
        cursor.execute('''INSERT OR REPLACE INTO locked_status(id, locked) VALUES(:id,:version)''', {'id':filepath, 'version':'1'})
        conn.commit()
        conn.close()
        return "was open, now locked", 200
    else:
        return "locked", 409


@app.route("/unlock_file/<path:filepath>")
def unlockFile(filepath):
    conn = connect('lockserver')
    cursor = conn.cursor()
    cursor.execute('''INSERT OR REPLACE INTO locked_status(id, locked) VALUES(:id,:version)''', {'id':filepath, 'version':'0'})
    conn.commit()
    conn.close()
    return "unlocked", 200

@app.route("/delete_file/<path:filepath>")
def delete_file(filepath):
    conn = connect('lockserver')
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM versions WHERE id = ? ''', (filepath,))
    conn.commit()
    conn.close()
    return "file deleted", 200



@app.route("/") #if you want to check that manager is up
def hello():
    return "hello", 200


if __name__ == "__main__":
    init_db()
    app.run(host='0.0.0.0', port=80)
