#!/bin/bash

source OS-functions

mkdir -p logs
VM_NAME="repo2docker"

# Start VM with the specified parameters ==============================================
openstack server create \
  --image 98c10a7f-2587-450b-866c-1266ea0dbe4b \
  --flavor ssc.medium \
  --key-name singularity \
  --security-group ssh-whitelist \
  --user-data cloud-init.sh ${VM_NAME} |& tee logs/01.server-create.log

OS_assign_floating_ip ${VM_NAME} 


