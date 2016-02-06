FROM ubuntu:latest
MAINTAINER Daniel White

# Let's start with a clean, up to date Ubuntu
RUN apt-get -y install software-properties-common
RUN apt-get update && apt-get -y upgrade

# Get rid of Python encoding errors
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN apt-get -y install git python2.7 python-setuptools python-stdeb libxml2-dev

RUN apt-get -y install  ipython \
			python-dateutil \
			python-hachoir-core \
			python-hachoir-metadata \
			python-hachoir-parser \
			python-protobuf \
			python-requests \
			python-six \
			python-yaml \
			libyaml-dev \
			bison \
			flex

#
# To build libyal/liblnk
RUN apt-get -y install autoconf automake autopoint build-essential libtool pkg-config python-dev

# Pefile won't install the required version if we don't specify the
# index URL to use
# RUN pip install -i https://pypi.python.org/pypi/ pefile==1.2.10-139

# Required packages to build tsk
RUN apt-get -y install zlib1g-dev

# Required packages to build pytsk
Run apt-get -y install libtalloc-dev

# Extra package for running plaso tests
RUN apt-get -y install python-mock

# more deps
RUN apt-get -y install quilt python3-dev python3-all byacc devscripts python3-setuptools libfuse-dev libssl-dev

########
#Checkout the repo
WORKDIR /home/plaso/
RUN git clone https://github.com/onager/l2tdevtools.git

WORKDIR /home/plaso/l2tdevtools
RUN git checkout docker_experiments

RUN PYTHONPATH=. ./tools/build.py --config=./data/docker/projects.ini dpkg
WORKDIR /home/plaso/l2tdevtool/build
RUN dpkg -i *.deb

RUN /sbin/ldconfig -v

WORKDIR /home/plaso/log2timeline/plaso
RUN export PYTHONIOENCODING=UTF-8 && python setup.py install

WORKDIR /usr/local/bin
COPY "plaso-switch.sh" "plaso-switch.sh"
RUN chmod ax plaso-switch.sh

# These volumes are here to share input data and output
# results with the host system
VOLUME ["/data/artefacts","/data/results"]

ENTRYPOINT ["/usr/local/bin/plaso-switch.sh"]
