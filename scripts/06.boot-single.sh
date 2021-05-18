#!/bin/bash

source OS-functions
mkdir -p logs

VM_NAME="${1}"
if [ -z ${1} ]; then echo "Name for the VM not provided.";            exit ; fi 
if [ -z ${2} ]; then echo "Git repository for the VM not provided.";  exit ; fi 

SERVER_LIST=( $(OS_server_list) )

if [[ " ${SERVER_LIST[@]} " =~ " ${VM_NAME} " ]]; then
  #echo "Server with the name: ${VM_NAME} alredy exists"
  VM_IPs=( $(OS_server_get_ip ${VM_NAME}) )
  VM_IP=${VM_IPs[-1]}
  echo "VM external IP: ${VM_IP}"


  echo -e "\n========= Jupyter link ===================================================="
  ssh -i ~/.ssh/singularity.pem \
      -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      ubuntu@${VM_IP} \
      'grep "  http://.*token=" /var/log/cloud-init-output.log | awk '"'"'/http:.*token/{sub("127.0.0.1","'${VM_IP}'");print; next}{print}'"'"' '

  echo -e "\n========= cloud-init.sh log ==============================================="
  ssh -i ~/.ssh/singularity.pem \
      -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      ubuntu@${VM_IP} \
      'tail -n 10  /var/log/cloud-init-output.log | awk '"'"'/http:.*token/{sub("127.0.0.1","'${VM_IP}'");print; next}{print}'"'"' '

else

cat <<EOF > cloud-init-${VM_NAME}.sh
#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
su ubuntu -c "jupyter-repo2docker ${2}"
EOF

  # Start VM with the specified parameters ==============================================
  openstack server create \
    --image f584099f-2985-42ca-85dc-e9bf7bec202c \
    --flavor ssc.medium \
    --boot-from-volume 150 \
    --key-name singularity \
    --security-group ssh-whitelist \
    --security-group Open-top \
    --user-data cloud-init-${VM_NAME}.sh  ${VM_NAME} |& tee logs/06.boot-${VM_NAME}.log

  OS_assign_floating_ip ${VM_NAME}
fi
