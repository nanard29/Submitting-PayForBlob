from flask import Flask, render_template, request, redirect, url_for
import subprocess
import json
import secrets
import binascii
import requests
import time
import re
import getpass

def generate_rand_hex_encoded_namespace_id():
    # Generate 8 random bytes
    n_id = secrets.token_bytes(8)
    # Return the hex-encoded string representation of the bytes
    return binascii.hexlify(n_id).decode()

def generate_rand_message():
    # Generate a random message length between 1 and 100 bytes
    len_msg = secrets.choice(range(16, 65))
    # Generate random bytes for the message
    msg = secrets.token_bytes(len_msg)
    # Return the hex-encoded string representation of the bytes
    return binascii.hexlify(msg).decode()

def init():
    while True:
        initw = 'OK'
        return initw


app = Flask(__name__)
initw = init()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():

    # Generate random number
    n_id, msg = generate_rand_hex_encoded_namespace_id(), generate_rand_message()

    # Submit through curl
    curl_cmd = f"curl -X POST -H 'Content-type: application/json' -d '{{\"namespace_id\": \"{n_id}\", \"data\": \"{msg}\", \"gas_limit\": 80000, \"fee\": 2000}}' http://localhost:26659/submit_pfb"
    submit_output = subprocess.check_output(curl_cmd, shell=True)

    # Get data from the response
    submit_response = json.loads(submit_output)
    height = submit_response["height"]
    txhash = submit_response["txhash"]
    logs = submit_response["logs"]
    signer = logs[0]['events'][0]['attributes'][2]['value'].strip('"')
    # Get share message via curl using header
    header_url = f"http://localhost:26659/namespaced_shares/{n_id}/height/{height}"
    header_cmd = f"curl {header_url}"
    header_output = subprocess.check_output(header_cmd, shell=True)

    # Share message 
    share_msg = json.loads(header_output.decode())["shares"][0]

    return render_template("result.html", n_id=n_id, msg=msg, height=height, txhash=txhash, share_msg=share_msg, signer=signer)


if __name__ == "__main__":
    app.run()
