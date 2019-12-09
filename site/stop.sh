#!/bin/bash
app="tc"
docker stop ${app}
docker rm ${app}
docker rmi ${app}