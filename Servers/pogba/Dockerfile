FROM python:3
WORKDIR /Users/dylan/Documents/College/CSY5/ScalableComputing/FileServer/Servers/pogba
ADD . /Users/dylan/Documents/College/CSY5/ScalableComputing/FileServer/Servers/pogba
EXPOSE 80
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
ENV NAME World

ADD server.py /
CMD [ "python3", "-u", "server.py" ]
