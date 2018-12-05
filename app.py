from flask import Flask, render_template, request, send_file
import scoreboarding
import pandas as pd

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app._static_folder = "static"

@app.route("/")
def home():
    return render_template("home.html")

@app.route('/simulator', methods=['GET', 'POST'])
def post():
    # get user input
    source = request.form['code_input']
    ldu_units = int(request.form['ldu_units'])
    alu_units = int(request.form['alu_units'])
    ldu_delay = int(request.form['ldu_delay'])
    alu_delay = int(request.form['alu_delay'])
    # execute simulation
    scoreboarding.main(source, ldu_units, alu_units, ldu_delay, alu_delay)
    return render_template("table.html")

@app.route("/simulator/download")
def DownloadLogFile(path = None):
        return send_file("results.log", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)