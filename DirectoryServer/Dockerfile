FROM python:3
WORKDIR /Users/dylan/Documents/College/CSY5/ScalableComputing/FileServer/DirectoryServer
ADD . /Users/dylan/Documents/College/CSY5/ScalableComputing/FileServer/DirectoryServer
EXPOSE 80
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt
ENV NAME World

ADD directoryserver.py /
CMD [ "python3", "-u", "directoryserver.py" ]
