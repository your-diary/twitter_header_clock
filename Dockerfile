FROM alpine

WORKDIR /app

RUN apk add python3 py3-pip
RUN apk add build-base zlib-dev jpeg-dev python3-dev #for Pillow
RUN pip3 install python-twitter Pillow

CMD ["./twitter_header_clock.py"]

