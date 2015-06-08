docker rm -f $(docker ps -qa -f label=type=appli)
