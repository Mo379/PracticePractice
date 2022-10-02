#seed
FROM python:3.8
#setup
ENV TZ=Europe/Minsk
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update
RUN apt-get install build-essential checkinstall
#RUN apt-get -y install libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
RUN apt-get -y install libffi-dev
RUN apt-get -y install apt-utils vim curl apache2 apache2-utils apache2-dev python3-dev
RUN ln /usr/bin/python3 /usr/bin/python
#RUN ln /usr/bin/pip3 /usr/bin/pip
#RUN apt-get -y install libapache2-mod-wsgi-py3
# WSGI
RUN wget https://github.com/GrahamDumpleton/mod_wsgi/archive/refs/tags/4.9.4.tar.gz \
	&& tar xvfz 4.9.4.tar.gz \
	&& cd mod_wsgi-4.9.4 \
	&& ./configure --with-python=/usr/bin/python3.8 \
	&& make \
	&& make install 
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
#requirements
RUN pip install --upgrade pip
RUN pip install -r /var/www/html/requirements.txt 
#expose and run
EXPOSE 80 3500
CMD ["apache2ctl", "-D", "FOREGROUND"]

