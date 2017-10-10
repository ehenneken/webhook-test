FROM phusion/baseimage:0.9.22

RUN apt-get update
RUN apt-get install -y git bzip2 net-tools curl nano python-pip python-dev libpq-dev
RUN pip install -U pip
RUN pip install --upgrade gunicorn==19.6.0 gevent==1.1.2 supervisor==3.3.0 futures==3.0.5

# add scripts/tags
ADD repository /repository
#ADD release /release
ADD before_install.sh /before_install.sh
ADD after_install.sh /after_install.sh


WORKDIR /app
RUN /bin/bash -c "git clone `cat /repository` /app"
#RUN git pull && git reset --hard `cat /release`

# Provision the project
RUN pip install -r requirements.txt
RUN if -e alembic.ini; then alembic -c ./alembic.ini upgrade head; fi

# Add local config
ADD gunicorn.conf.py /app/gunicorn.conf.py
ADD gunicorn.sh /etc/service/gunicorn/run

EXPOSE 9000
# insert the local config
ADD service/local_config.py /local_config.py
RUN /bin/bash -c "find . -maxdepth 2 -name config.py -exec /bin/bash -c 'echo {} | sed s/config.py/local_config.py/ | xargs -n1 cp /local_config.py' \;"
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN /after_install.sh

# expose log files written to tmp
VOLUME ["/tmp"]

CMD ["/sbin/my_init"]
