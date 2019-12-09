#!/bin/bash

CN=$(docker container ls --format='{{ .Names}}' | grep $1)
docker exec -ti $CN /bin/sh
