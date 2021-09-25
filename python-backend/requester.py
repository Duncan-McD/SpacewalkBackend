from flask import Flask, request

app = Flask(__name__)

@app.route("/users", methods["GET"])
def search_users():
  return [];

@app.route("/user", methods["GET"])
def search_users():
  userid = request.args.get('id')
  return {};

@app.route("/bodies", methods["GET"])
def search_users():
  return [];

@app.route("/body", methods["GET"])
def search_users():
  name = request.args.get('name')
  return {};