FROM ubuntu

RUN apt-get update && apt-get install -y software-properties-common python-software-properties && add-apt-repository ppa:ubuntugis/ubuntugis-unstable 
RUN apt-get update && apt-get install -y gdal-bin python3 python3-pyproj
