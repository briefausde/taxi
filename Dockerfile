FROM python:3.8-slim-buster

COPY ./requirements.txt /tmp/

RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install \
        -r /tmp/requirements.txt

ADD . /work/taxi
WORKDIR /work/taxi

CMD [ "python3", "-m",  "taxi"]

# init watchexec
ADD https://github.com/watchexec/watchexec/releases/download/1.10.0/watchexec-1.10.0-x86_64-unknown-linux-musl.tar.gz /opt/watchexec.tar.gz
RUN mkdir /opt/watchexec
RUN tar -xzf /opt/watchexec.tar.gz -C /opt/watchexec --strip-components=1
RUN ls -l /opt
RUN ln -s /opt/watchexec/watchexec /usr/local/bin/watchexec
RUN ln -s /opt/watchexec/watchexec /usr/bin/watchexec
