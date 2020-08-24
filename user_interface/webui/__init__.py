from flask import Flask, render_template

from time import time
from utils import sysinfo

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__, template_folder='../../files/webui/', static_folder='../../files/webui/static')

wsserver = None


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/ajax')
def ajax():
    data = {'time': time(), 'config': wsserver.get_config()}
    return data


@app.route('/setdata')
def setdata():
    return 'W.I.P'


@app.route('/sysinfo')
def info():
    return sysinfo.sysinfo()
