#!/usr/bin/env python3
from flask import Flask, redirect, url_for
from flask import make_response, render_template, abort, request
from flask_dance.contrib.github import make_github_blueprint, github

from string import Template
import subprocess, shlex
import os

CMD2RUN= "./06.boot-single.sh ${par1} ${par2}"
GIT_URL= "https://github.com/pmitev/jupyter-binder.git"

#=======================================================================================
# Allowed github user id's
def read_allowed_users():
  with open('allowed_users.cfg','r') as f:
    lines=f.readlines()
  return set(map(str.strip,lines))

ID_ALLOWED= read_allowed_users()
print(f"Allowed users:{ID_ALLOWED}")

#============================================================================
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.secret_key = "SSCsupersekrit"  # Replace this with your own secret!
# https://github.com/settings/developers - create new "OAuth Apps" and replace with the
# corresponding values
blueprint = make_github_blueprint(
  client_id="aaa",
  client_secret="bbb",
)
app.register_blueprint(blueprint, url_prefix="/login")

@app.route("/VM_run")
def VM_RUN():
  ip= request.remote_addr

  if not github.authorized:
    return redirect(url_for("github.login"))
  resp = github.get("/user")
  
  assert resp.ok
  user_id= resp.json()["login"]
  
  par1= user_id
  try:
    par2= request.args.get('giturl')
  except:
    par2= GIT_URL
  if par2 == None :
    par2= GIT_URL

  ID_ALLOWED= read_allowed_users()
  if user_id in ID_ALLOWED:
    cmd_txt= CMD2RUN
    cmd_txt= Template(cmd_txt).substitute(ip=ip, par1=par1, par2=par2)

    cmd=shlex.split(cmd_txt)
    print(">>> cmd: " + cmd_txt)

    proc= subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    print(stdout.decode())
    print(stderr.decode())

    response_tmp= Template("${stdout}").substitute(ip=ip, stdout=stdout.decode(), stderr=stderr.decode)
    response= make_response(response_tmp, 200)
  else:
    print("Wrong")
    response= make_response('Wrong', 404)
    abort(403)

  response.mimetype = "text/plain"
  return response

#=======================================================================================
@app.route("/VM_delete")
def VM_DELETE():

  if not github.authorized:
    return redirect(url_for("github.login"))
  resp = github.get("/user")
  
  assert resp.ok
  user_id= resp.json()["login"]

  ID_ALLOWED= read_allowed_users()
  if user_id in ID_ALLOWED:
    cmd_txt= "./10.VM_delete.sh ${user_id}"
    cmd_txt= Template(cmd_txt).substitute(user_id=user_id)

    cmd=shlex.split(cmd_txt)
    print(">>> cmd: " + cmd_txt)

    proc= subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    print(stdout.decode())
    print(stderr.decode())

    response_tmp= Template("${stdout}\nDone").substitute(stdout=stdout.decode(), stderr=stderr.decode)
    response= make_response(response_tmp, 200)
  else:
    print("Wrong")
    response= make_response('Wrong', 404)
    abort(403)

  response.mimetype = "text/plain"
  return response

#=======================================================================================
# Randomize the registration link
@app.route("/register/dde0d0aa-43e3-4492-a86c-611482cd7ac9")
def register():
  if not github.authorized:
    return redirect(url_for("github.login"))
  resp = github.get("/user")

  assert resp.ok

  with open('allowed_users.cfg','r') as f:
    lines=f.readlines()

  ID_ALLOWED= set(map(str.strip,lines))
  ID_ALLOWED.add(resp.json()["login"])

  with open('allowed_users.cfg','w') as f:
    for i in list(ID_ALLOWED):
      f.write(f"{i}\n")

  return "Your GitHub ID is registered for the course"

#=======================================================================================
@app.route("/")
def index():
  return "SSC mybinder test"


#============================================================================

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=5000, debug=True)

