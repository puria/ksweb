FROM python:3
#ENV PYTHONUNBUFFERED 1
#ENV LANG C.UTF-8
#ENV LC_ALL C.UTF-8
#RUN apt-get update && apt-get install -y \
#    python3 \
#    python3-pip \
#    git
COPY ./ksweb /
RUN pip3 install -e .
RUN pip3 install --pre tg.devtools
EXPOSE 8080
ENTRYPOINT ["/serve"]