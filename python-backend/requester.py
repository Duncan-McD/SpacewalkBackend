from flask import Flask, request
from uuid import uuid4

app = Flask(__name__)

def authorized(username, authKey):
  return bool(app.config["users"].find_one({"ID":username, "authKey":authKey}))


@app.route("/user", methods=["GET","POST"])
def user():
  userid = request.args.get('id')
  body = request.get_json()
  if (authorized(body["username"], body["authKey"]) and body["username"] == userid):
    
    docs = list(app.config["users"].find({"ID":userid}))
    if (len(docs)== 1): 
      del (docs[0]['_id'])
      del (docs[0]['password'])
      del (docs[0]['authKey'])
      return {"success":True, "user": docs[0]}
    else:
      return {"success":False, "reason":"Bad login"}
  else:
    return {"success":False, "reason":"You are not authorized to get this data!"}

@app.route("/bodies", methods=["GET"])
def bodies():
  cursor = app.config["bodies"].find({})
  return {"bodies": [doc["name"] for doc in cursor]}

@app.route("/body", methods=["GET"])
def body():
  name = request.args.get('name')
  docs = list(app.config["bodies"].find({"name":name}))
  if (len(docs)== 1): 
    del (docs[0]['_id'])
    return docs[0]
  return {}


@app.route("/updateDistance", methods=["POST"])
def updateDistance():
  body = request.get_json()
  if (authorized(body["username"], body["authKey"])):
    
    userid = body['username']
    distance = body['distance']
    test = app.config["users"].find_one_and_update({"ID": userid}, 
                                  {"$set": {"walkedDistance": distance}})
    return {"success": bool(test)}
  else:
    return {"success":False, "reason":"You are not authorized to update this data!"}

@app.route("/register", methods=["POST"])
def register():
  body = request.get_json()
  email = body['email']
  name = body['name']
  password = body['password']
  username = body['username']
  doc = app.config["users"].find_one({"email":email})
  doc2 = app.config["users"].find_one({"ID":username})
  new_user = {
    "ID": username,
    "name": name,
    "email": email,
    "password": password,
    "walkedDistance": 0,
    "level": 0,
    "authKey": str(uuid4())
  }
  if(not doc and not doc2): 
    test = app.config["users"].insert_one(new_user)
    return {"success": bool(test), "authKey": new_user["authKey"]}
  else:
    if(doc and doc2):reason ="Email and username already in use! :("
    elif(doc):reason ="Email already in use! :("
    elif(doc2):reason="Username already in use! :("
    
    return {"success": False, "reason": reason}


@app.route("/login", methods=["POST"])
def login():
  body = request.get_json()
  email = body['email']
  password = body['password']
  username = body['username']
  if not username and not email: return {"success": False, "reason": "no email or username provided"}
  doc = app.config["users"].find_one({"email":email, "password":password})
  doc2 = app.config["users"].find_one({"ID":username, "password":password})
  if not doc and not doc2: return {"success": False, "reason": "email and/or username do not match"}

  return {"success": True, "authKey": doc["authKey"] if doc else doc2["authKey"]}

@app.route("/logout", methods=["POST"])
def logout():
  body = request.get_json()
  username = body['username']
  authKey = body['authKey']
  if (authorized(username, authKey)):
    
    new_authKey = str(uuid4())
    test = app.config["users"].find_one_and_update({"ID":username, "authKey":authKey}, 
                                {"$set": {"authKey": new_authKey}})
    return {"success": bool(test)}
  else:
    return {"success":False, "reason":"You are not authorized to log out this user!"}

