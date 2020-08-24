from flask import Flask, render_template

app = Flask(__name__, template_folder='../../files/webui/', static_folder='../../files/webui/static')

wsserver = None


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/ajax')
def ajax():
    return wsserver.get_config()
