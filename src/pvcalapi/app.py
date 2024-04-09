from flask import Flask



app = Flask(__name__)

@app.route("/")
def home():
    return "PV-Cal"

@app.route("/serialport")
def serialport():
    serialport = "COM1"
    return serialport

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)