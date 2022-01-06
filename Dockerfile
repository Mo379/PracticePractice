#seed
FROM ubuntu:20.04
#setup
ENV TZ=Europe/Minsk
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update
RUN apt-get -y install apt-utils vim curl apache2 apache2-utils
RUN apt-get -y install python3 libapache2-mod-wsgi-py3
RUN apt-get -y install python3-pip
RUN ln /usr/bin/python3 /usr/bin/python
#RUN ln /usr/bin/pip3 /usr/bin/pip
RUN pip install --upgrade pip
#app periferals
ADD ./APP_apache.conf /etc/apache2/sites-available/000-default.conf 
ADD ./requirements.txt /var/www/html 
RUN pip install -r /var/www/html/requirements.txt 
#Groups, Permissions and Ownership
WORKDIR /var/www/html 
#RUN chmod 664 /var/www/html/APP/db.sqlite3 
#RUN chmod 775 /var/www/html/APP/PP2 
#RUN chmod 775 /var/www/html/APP/logs 
#RUN chown :www-data /var/www/html/APP/db.sqlite3 
#RUN chown :www-data /var/www/html/APP/PP2
#RUN chown :www-data /var/www/html/APP/logs
#expose and run
EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]

