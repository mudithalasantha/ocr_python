# OCR Server

An web-based Optical Character Recognition system.

## Dependencies

 - $ sudo apt-get update
 - $ sudo apt-get install autoconf automake libtool
 - $ sudo apt-get install libpng12-dev
 - $ sudo apt-get install libjpeg62-dev
 - $ sudo apt-get install g++
 - $ sudo apt-get install libtiff4-dev
 - $ sudo apt-get install libopencv-dev libtesseract-dev
 - $ sudo apt-get install git
 - $ sudo apt-get install cmake
 - $ sudo apt-get install build-essential
 - $ sudo apt-get install libleptonica-dev
 - $ sudo apt-get install liblog4cplus-dev
 - $ sudo apt-get install libcurl3-dev
 - $ sudo apt-get install python2.7-dev
 - $ sudo apt-get install tk8.5 tcl8.5 tk8.5-dev tcl8.5-dev
 - $ sudo apt-get build-dep python-imaging --fix-missing

 - Ubuntu 14.04 
 - Leptonica 1.75.3 (http://www.leptonica.com/)
 - Tesseract 3.02.02 (https://github.com/tesseract-ocr/tesseract/wiki)
 
##### Docker OSX Install

Build the container and run the image...

```sh
$ docker build --rm -t flask-docker-ocr .
$ docker run -p 80:5000 flask-docker-ocr
```
