#!/bin/bash

docker pull python:3.11

docker build --no-cache -t cat--meow_image .
