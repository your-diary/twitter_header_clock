#!/usr/bin/env bash

docker run --restart always --volume "${PWD}":/home/user/work ubuntu_selenium \
    bash -c './twitter_header_clock.py >> log.txt'

