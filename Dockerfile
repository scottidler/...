FROM ubuntu

RUN apt-get update && apt-get install -y \
    vim \
    git \
    curl \
    sudo \
    python3 \
    python3-pip

RUN pip3 install \
    ruamel.yaml

# add non-priviledged user
RUN groupadd --gid 1000 manifest && \
    adduser --uid 1000 --disabled-password --gecos '' --ingroup manifest manifest

WORKDIR /home/manifest

RUN cd /home/manifest && git clone https://github.com/scottidler/...

# change user
RUN chown manifest:manifest -R .
USER $manifest
