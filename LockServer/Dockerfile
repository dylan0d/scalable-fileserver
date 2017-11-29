FROM python:3
WORKDIR /Users/dylan/Documents/College/CSY5/ScalableComputing/FileServer/LockServer
ADD . /Users/dylan/Documents/College/CSY5/ScalableComputing/FileServer/LockServer
EXPOSE 80
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
ENV NAME World

ADD lockserver.py /
CMD [ "python3", "-u", "lockserver.py" ]
