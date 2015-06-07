FROM bfonty/base-server

MAINTAINER Benoît FONTY

#add the user appli
ADD appli/* /usr/users/appli/
RUN chown -R appli:appli /usr/users/appli

EXPOSE 5000

WORKDIR /usr/users/appli

LABEL type="appli"

CMD ["su","-","appli","-c","python appli.py"]