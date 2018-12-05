from flask import Flask, render_template
import scoreboarding

app = Flask(__name__)
app._static_folder = "static"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/simulator")
def about():
    scoreboarding.main()
    return render_template("simulator.html")

if __name__ == "__main__":
    app.run(debug=True)