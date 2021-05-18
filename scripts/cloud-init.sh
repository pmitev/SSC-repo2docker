#!/bin/bash
# Update =========================================================================================
export DEBIAN_FRONTEND=noninteractive
apt-get update && apt-get dist-upgrade -y

# Docker  ========================================================================================
export DEBIAN_FRONTEND=noninteractive
wget -qO- https://get.docker.com/ | sh

usermod -aG docker ubuntu

# Docker
cat << EOF > /etc/docker/daemon.json
{
  "mtu": 1400
}
EOF

systemctl restart docker.service

docker pull buildpack-deps:bionic

# Packages =======================================================================================
apt-get update && apt-get install -y --no-install-recommends mc units vim gawk git putty ncdu screen expect python3-pip python3.8-venv python3-tk

apt-get clean

python3 -m pip install --no-cache-dir jupyter-repo2docker


# Build to cache layers ==========================================================================

su ubuntu -c "jupyter-repo2docker --no-run https://github.com/pmitev/word-count.git"
