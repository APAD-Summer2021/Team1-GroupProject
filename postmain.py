from flask import Flask, render_template, request, redirect, url_for  # For flask implementation
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient("mongodb://")  # host uri
db = client.mymongodb  # Select the database


if __name__ == "__main__":
    app.run(debug=True)