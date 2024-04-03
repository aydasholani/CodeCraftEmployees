import os
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
  text = "Hello World"
  return render_template('index.html', text=text)