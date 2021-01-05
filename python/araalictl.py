#!/usr/bin/env python
import os
import requests
import sys
from sys import platform

from main import Usage, run_command

def fetch():
    linux_url = "https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl.linux-amd64"
    darwin_url = "https://s3-us-west-2.amazonaws.com/araalinetworks.cf/araalictl.darwin-amd64"

    if platform == "linux" or platform == "linux2":
        url = linux_url
    elif platform == "darwin":
        url = darwin_url
    else:
        raise Usage("only linux and mac are currently supported")
    print("Fetching araalictl ...")
    r = requests.get(url, allow_redirects=True)
    open('araalictl', 'wb').write(r.content)
    os.chmod('araalictl', 0o777)


def help():
    print(run_command("./araalictl -h", result=True, debug=False)[1])

if __name__ == '__main__':
    sys.exit(fetch())
