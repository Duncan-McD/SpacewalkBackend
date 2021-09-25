from flask import Flask, request

app = Flask(__name__)

@app.route("/users", methods=["GET"])
def users():
  cursor = app.config["users"].find({})
  return {"users": [doc["ID"] for doc in cursor]}
   

@app.route("/user", methods=["GET"])
def user():
  userid = request.args.get('id')
  docs = list(app.config["users"].find({"ID":userid}))
  if (len(docs)== 1): 
    del (docs[0]['_id'])
    return docs[0]
  return {}

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
  userid = body['id']
  distance = body['distance']
  test = app.config["users"].find_one_and_update({"ID": userid}, 
                                {"$set": {"walkedDistance": distance}})
  return {"success": bool(test)}

@app.route("/signUp", methods=["POST"])
def signUp():
  body = request.get_json()
  email = body['email']
  name = body['name']
  password = body['password']
  username = body['userame']
  doc = app.config["users"].find_one({"email":email})
  doc2 = app.config["users"].find_one({"ID":username})
  new_user = {
    "ID": username,
    "name": name,
    "email": email,
    "password": password,
    "walkedDistance": 0,
    "level": 0
  }
  if(not len(doc) and not len(doc2)): 
    test = app.config["users"].insert_one(new_user)
    return {"success": bool(test)}
  else:
    if(len(doc) and len(doc2)):reason ="Email and username already in use! :("
    elif(len(doc)):reason ="Email already in use! :("
    elif(len(doc2)):reason="Username already in use! :("
    
    return {"success": False, "reason": reason}
  