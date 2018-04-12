# start with a base image
FROM ubuntu:14.04

# install dependencies
RUN apt-get update
RUN apt-get install -y autoconf automake libtool
RUN apt-get install -y libpng12-dev
RUN apt-get install -y libjpeg62-dev
RUN apt-get install -y g++
RUN apt-get install -y libtiff4-dev
RUN apt-get install -y libopencv-dev libtesseract-dev
RUN apt-get install -y git
RUN apt-get install -y cmake
RUN apt-get install -y build-essential
RUN apt-get install -y libleptonica-dev
RUN apt-get install -y liblog4cplus-dev
RUN apt-get install -y libcurl3-dev
RUN apt-get install -y python2.7-dev
RUN apt-get install -y tk8.5 tcl8.5 tk8.5-dev tcl8.5-dev
RUN apt-get --yes install python-imaging
RUN apt-get install -y imagemagick
RUN apt-get install -y wget
RUN apt-get install -y python python-pip

# build leptonica
#RUN apt-get install libleptonica-dev
RUN wget http://www.leptonica.com/source/leptonica-1.71.tar.gz
RUN tar -zxvf leptonica-1.71.tar.gz
WORKDIR leptonica-1.71/
RUN ./autobuild
RUN ./configure
RUN make
RUN make install
RUN ldconfig
WORKDIR /
RUN ls

ADD requirements.txt /
RUN pip install -r requirements.txt

# build tesseract
# RUN apt install tesseract-ocr
#RUN wget https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.02.tar.gz
#RUN tar -zxvf tesseract-ocr-3.02.02.tar.gz
ADD ./tesseract-ocr /tesseract-ocr
WORKDIR tesseract-ocr/
RUN ./autogen.sh
RUN ./configure
RUN make
RUN make install
RUN ldconfig
RUN cd ..

# download the relevant Tesseract English Language Packages
#RUN wget https://tesseract-ocr.googlecode.com/files/tesseract-ocr-3.02.eng.tar.gz
#RUN tar -xf tesseract-ocr-3.02.eng.tar.gz
RUN pwd
ADD ./tesseract-ocr/tessdata /usr/local/share/tessdata
RUN ls /usr/local/share/tessdata

# update working directories
ADD ./flask_server /flask_server
WORKDIR /flask_server

EXPOSE 80
CMD ["python", "app.py"]