#!/bin/bash

source OS-functions
mkdir -p logs

VM_NAME="${1}"
if [ -z ${1} ]; then echo "Name for the VM not provided.";            exit ; fi

VOLUME_LIST=( $(OS_server_get_volumes ${1}) )

openstack server delete --wait ${1} && openstack volume delete ${VOLUME_LIST[@]}
