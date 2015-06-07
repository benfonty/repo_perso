# Ubunto as base image
FROM centos:6
 
MAINTAINER Benoît FONTY
 
# install the gcc tools to enable compilation
RUN yum -y install gcc

RUN mkdir -p /sources
WORKDIR /sources

ENTRYPOINT make

CMD ["all"]