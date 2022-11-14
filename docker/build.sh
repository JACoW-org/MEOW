#!/bin/bash

docker pull python:3.10

docker build --no-cache -t jpsp-ng-image .
