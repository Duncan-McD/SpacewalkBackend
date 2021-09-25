from flask import Flask, request
from uuid import uuid4
import bcrypt
from python_backend import emailer

app = Flask(__name__)



#hashes s and returns it as a type bytes
def hash_string(s):
    byte_s = bytes(s, 'utf-8')
    hashed = bcrypt.hashpw(byte_s, bcrypt.gensalt())
    return hashed

#compare the given user s [type str] to a users hashed password [type bytes]
def compare_string_hashed(s, s_hash):
    assert type(s) == str
    assert type(s_hash) == bytes
    return bcrypt.checkpw(s.encode('utf-8'), s_hash)

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

@app.route("/updateAccountType", methods=["POST"])
def updateAccountType():
  body = request.get_json()
  if (authorized(body["username"], body["authKey"])):
    
    userid = body['username']
    public = body['public']
    test = app.config["users"].find_one_and_update({"ID": userid}, 
                                  {"$set": {"public": public}})
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
  public = body['public']
  doc = app.config["users"].find_one({"email":email})
  doc2 = app.config["users"].find_one({"ID":username})
  new_user = {
    "ID": username,
    "name": name,
    "email": email,
    "password": hash_string(password),
    "walkedDistance": 0,
    "level": 0,
    "confirmationKey": str(uuid4()),
    "confirmed": False,
    "authKey": str(uuid4()),
    "public": public
  }
  if(not doc and not doc2): 
    test = app.config["users"].insert_one(new_user)
    emailer.send_confirm(new_user["confirmationKey"], email, name.split()[0] , username)
    return {"success": bool(test)}
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
  if not username and not email: 
    return {"success": False, "reason": "no email or username provided"}
  doc = app.config["users"].find_one({"email":email})
  doc2 = app.config["users"].find_one({"ID":username})
  password_correct = compare_string_hashed(password,(doc["password"] if doc else doc2["password"]))
  if not doc and not doc2: 
    return {"success": False, "reason": "email or username not registered"}
  if (not (doc["confirmed"] if doc else doc2["confirmed"])): 
    return {"success": False, "reason": "You must confirm by email!"}
  if (password_correct):
    return {"success": True, "authKey": doc["authKey"] if doc else doc2["authKey"]}
  else:
    return {"success": False, "reason": "Incorrect Password"}

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

@app.route("/confirmEmail", methods=["GET"])
def emailConfirmation():
  confirmationKey = request.args.get('confirmationKey')
  username = request.args.get('username')
  doc = app.config["users"].find_one({"ID":username})
  if not doc: 
    with open("./python_backend/pages/emailconfirmfailed.html") as f:
      txt = f.read()
    return txt
  elif doc["confirmationKey"] != confirmationKey:
    with open("./python_backend/pages/emailconfirmfailed.html") as f:
      txt = f.read()
    return txt
  else:
    test = app.config["users"].find_one_and_update({"ID":username, "confirmationKey":confirmationKey}, 
                                {"$set": {"confirmed": True}})
    if bool(test):
      with open("./python_backend/pages/emailconfirmed.html") as f:
        txt = f.read()
      return txt
    else:
      with open("./python_backend/pages/emailconfirmfailed.html") as f:
        txt = f.read()
      return txt

@app.route("/passwordReset", methods=["POST"])
def passwordReset():
  return {}

@app.route("/deleteUser", methods=["POST"])
def deleteUser():
  
  body = request.get_json()
  username = (body['username'])
  password = body['password']
  if (authorized(body["username"], body["authKey"])):
    doc = app.config["users"].find_one({"ID":username})
    if compare_string_hashed(password,doc["password"]):
      res = app.config["users"].delete_one({"ID":username})
      return {"success": bool(res)}
    else:
      return {"success": False, "reason": "Password did not match"}
  else:
    return {"success": False, "reason": "You are not authorized to delete this user"}

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
  amount = request.args.get('amount')
  cursor = app.config["users"].find( { 'level': { '$gte': 2 }, 'public': True } )
  sortedCursor = cursor.sort("walkedDistance", -1)
  sortedList = list(sortedCursor)
  sortedLeaderboard = [{"username": user["ID"], "distanceWalked" : user["walkedDistance"]} for user in sortedList]


  if int(amount) > len(sortedLeaderboard):
    return {"success": True, "leaderboard":sortedLeaderboard}
  else:
    return {"success": True, "leaderboard":sortedLeaderboard[0:amount]}
