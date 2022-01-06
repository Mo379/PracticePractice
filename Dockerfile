#seed
FROM ubuntu:20.04
#setup
RUN apt-get update
RUN apt-get -y install apt-utils vim curl apache2 apache2-utils
RUN apt-get -y install python3 libapache2-mod-wsgi-py3
RUN apt-get -y install python3-pip
RUN ln /usr/bin/python3 /usr/bin/python
RUN ln /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip
#exec
COPY ./requirements.txt requirements.txt
COPY pip install -r requirements.txt
ADD ./PP2_apache.conf /etc/apache2/000-default.conf
EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]

