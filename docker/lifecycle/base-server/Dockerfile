FROM ubuntu

MAINTAINER Benoît FONTY

# Install required packages
RUN apt-get update
RUN apt-get -y install python python-pip wget
RUN pip install Flask

#add the user appli
RUN mkdir -p /usr/users/appli
RUN useradd --home /usr/users/appli -s /bin/bash appli

CMD ["bash"]
