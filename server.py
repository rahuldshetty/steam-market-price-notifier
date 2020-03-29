'''
This package contains server related methods.
'''
import sys
from os import environ
from flask import Flask, escape, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=environ.get("PORT", 5000))