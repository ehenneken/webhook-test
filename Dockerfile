FROM phusion/baseimage:0.9.22

ENV TERM xterm-256color
ENV LC_ALL C

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        git \
        bzip2 \
        net-tools \
        curl \
        nano \
        build-essential \
        python \
        ipython \
        python-dev \
        python-pip \
        python-setuptools \
        libpq-dev
RUN pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install --upgrade setuptools && \
    pip install --upgrade gunicorn==19.6.0 gevent==1.1.2 supervisor==3.3.0 futures==3.0.5

# add scripts/tags
ADD repository /repository
#ADD release /release
ADD before_install.sh /before_install.sh
ADD after_install.sh /after_install.sh


WORKDIR /app
RUN /bin/bash -c "git clone `cat /repository` /app"
#RUN git pull && git reset --hard `cat /release`

ADD service/local_config.py /app/local_config.py
RUN /bin/bash -c "find . -maxdepth 2 -name config.py -exec /bin/bash -c 'echo {} | sed s/config.py/local_config.py/ | xargs -n1 cp /app/local_config.py' \;"

# Provision the project
RUN pip install -U -r requirements.txt
RUN alembic -c ./alembic.ini upgrade head

# Add local config
ADD gunicorn.conf.py /app/gunicorn.conf.py
ADD gunicorn.sh /etc/service/gunicorn/run
RUN chmod 755 /etc/service/gunicorn/run

EXPOSE 9000
# insert the local config
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN /after_install.sh

# expose log files written to tmp
VOLUME ["/tmp"]

CMD ["/sbin/my_init"]
