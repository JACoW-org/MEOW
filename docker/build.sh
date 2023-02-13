#!/bin/bash

docker pull python:3.10

docker build --no-cache -t meow-ng-image .
