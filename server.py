'''
This package contains server related methods.
'''
import sys
from flask import Flask, escape, request, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args)<2:
        args = ["127.0.0.1", "5000"]
    app.run(debug=True, host=args[0], port=args[1])