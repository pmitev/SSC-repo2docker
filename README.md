# SSC-repo2docker

Simple [MyBider](https://mybinder.org/)-like solution for [SNIC Science Cloud](https://cloud.snic.se/)


## Prerequisites
Make sure to source the OpenStack RC file in the shell where scripts will be running. Test with `openstack image list` to confirm that you have working API connection.

### `openstack-client` and `flask` dependencies

``` bash
$ python3 -m pip install --user python-openstackclient flask Flask-Dance
```

## 1. Building the image to run [repo2docker ](https://github.com/jupyterhub/repo2docker)

Edit `00.create-image.sh` and specify the options for the inital image. **Keep it small.** A snapshot of the final instance will be used to boot VMs on demand.

``` bash
# Start VM with the specified parameters ==============================================
openstack server create \
  --image 98c10a7f-2587-450b-866c-1266ea0dbe4b \
  --flavor ssc.medium \
  --key-name my_key \
  --security-group ssh-whitelist \
  --user-data cloud-init.sh ${VM_NAME} |& tee logs/01.server-create.log
  ```


`cloud-init.sh` contains the instructions to install `docker`, some packages and `jupyter-repo2docker` via `pip`. On the last line we can build the target GitHub repositories to speedup the boot process in Step 2 by using the cached build.

Once the initial VM is ready, **power off** and make snapshot of it.

## 2. Configuring the VM on demand

Edit `06.boot-single.sh` to specify the the new boot image `--image` pointing to the snapshot of the image from Step 1 and the remaining settings.

``` bash
# Start VM with the specified parameters ==============================================
  openstack server create \
    --image e8f021f0-9cb4-4e68-bc1f-e7d91719d59a \
    --flavor ssc.medium \
    --boot-from-volume 150 \
    --key-name my_key \
    --security-group ssh-whitelist \
    --security-group Open-top \
    --user-data cloud-init-${VM_NAME}.sh  ${VM_NAME} |& tee logs/06.boot-${VM_NAME}.log
```

Make sure you protect your VMs by setting some reasonable restrictions for the open ports. Allow `ssh` access only to trusted IPs and open ports above 1024 to any IP.

### 2.1 booting from the command line.
``` bash
# Syntax
./06.boot-single.sh    VM_name    GitHub_URL
```

This setup uses user's GitHub IDs as an unique **VM_name**. The checks for both parameters are performed in the web interface running Flask.


## 3. Running the Web interface
For this you need a computer with port accessible from anywhere. Running a minimal VM instance with the installed prerequisites will be enough and perhaps the simplest solution.

Edit these lines in `user-web.py` accordingly

``` python
app.secret_key = "SSCsupersekrit"  # Replace this with your own secret!
# https://github.com/settings/developers - create new "OAuth Apps" and replace with the
# corresponding values
blueprint = make_github_blueprint(
  client_id="aaa",
  client_secret="bbb",
)

...

# Randomize the registration link
@app.route("/register/dde0d0aa-43e3-4492-a86c-611482cd7ac9")

...

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=5000, debug=True)
```

Advise:
- Change the port and switch off the debugging.
- Start the web Interface `./user-web.py` within `screen` session to avoid unexpected disconnect issues.


These are the routes (addresses) for the Web Interface API
- `/` - welcome page
- `/register/dde0d0aa-43e3-4492-a86c-611482cd7ac9` - link for regitering the users allowed to start VMs
- `/VM_start` - authenticated users can start a predefined VM or specify other URL `/VM_start?giturl=<GIT_URL>`
- `/VM_delete` - authenticated users can delete their VM and the attached storage.

