# Ubuntu 18.04

  sudo apt-get update
  sudo apt-get install -y ansible
  ssh-keygen
  ssh-copy-id -i ~/.ssh/id_rsa.pub root@(Jenkins_IP)

# install dev environment

  ansible-playbook simpc_playbook.yml -i host.simpc


# install jenkins / robot-framework environment

  ansible-playbook jenkins_playbook.yml  -i host.simpc


# jenkins server / install Azure azcli package

  ansible-playbook azcli_playbook.yml  -i host.simpc


# jenkins server / install GCE gsutil packages

  ansible-playbook gsutil_playbook.yml  -i host.simpc


