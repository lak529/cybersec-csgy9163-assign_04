#!/bin/bash

CN=$(docker container ls --format='{{ .Names}}' | grep $1)
docker services rm $CN
