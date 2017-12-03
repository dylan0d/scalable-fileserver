To run this program, run docker compose up in Servers/pogba, Servers/zlatan,
LockServer and DirectoryServer. 2 clients are also provided, and can be run with 
"python3 client.py". 

When a client is running, press o to open a file. This will 
retrieve the file from the server or create it locally. It will also lock the file.
This can be tested by trying to open it in another client. Type in what you'd 
like to save to the file and press enter to close it. this will unlock the file 
and write it to the server determined by the directory server. Opening the file 
in another client will show your changes. If you try to open again from the same
client, it will realise that the version number (and therefore the file on the 
server) is the same as your local copy and won't download a new version but will
open the local copy. Changes made will still be sent to the server.