#seed
FROM python:3.8
#setup
ENV TZ=Europe/Minsk
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update
RUN apt-get -y install apt-utils vim curl apache2 apache2-utils
RUN apt-get -y install libapache2-mod-wsgi-py3
RUN ln /usr/bin/python3 /usr/bin/python
#RUN ln /usr/bin/pip3 /usr/bin/pip
#app periferals
ADD ./APP/ /var/www/html
ADD ./.env /var/www/html/
ADD ./extras/includes/APP_apache.conf /etc/apache2/sites-available/000-default.conf 
ADD ./extras/includes/requirements.txt /var/www/html 
#Groups, Permissions and Ownership
WORKDIR /var/www/html 
RUN mkdir logs
RUN chmod 775 /var/www/html/PP2 
RUN chmod 775 /var/www/html/logs 
RUN chown :www-data /var/www/html/PP2
RUN chown :www-data /var/www/html/logs
#venv
WORKDIR /var/www/
RUN apt install -y python3.8-venv
RUN python3 -m venv venv
RUN source venv/bin/activate
RUN pip install --upgrade pip
RUN pip install -r /var/www/html/requirements.txt 
#expose and run
EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]

