from flask import Flask, render_template

# app = Flask(__name__, static_url_path='/static')

app = Flask(__name__)
app._static_folder = "static"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/simulator")
def about():
    return render_template("simulator.html")

if __name__ == "__main__":
    app.run(debug=True)