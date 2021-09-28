import sys
import pymongo
import json
from argparse import ArgumentParser
from .requester import app

def main(args):
  
  # Set up an argument parser for configuration of server on startup
  parser = ArgumentParser(description='''Private API for Spacewalk''')
  
  # Add debug flag to toggle debug mode
  parser.add_argument('-d','--debug', action='store_true', 
      help='turns on flask debug setting',
      default=False)
  
  # Add multithreading flag to toggle multithreading
  parser.add_argument('-s','--singlethread', action='store_true', 
      help='turns off flask multithreading setting',
      default=False)
  args = parser.parse_args(args) # parse the arguments passed into main

  # Load the mongo credentials from credentials file
  f = open('./python_backend/credentials.json')
  credentials = json.load(f)

  # Login and authenticate with the mongo server
  client = pymongo.MongoClient("mongodb+srv://" + credentials["username"] + ":" + credentials["password"] + "@bigredhacks2021.cojtr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
  
  # select the Space Walk database fpr use
  db = client.SpaceWalk

  # configure Flask configs to include the whole Space Walk database, the users collection, and the bodies collection. These will be used in the endpoints
  app.config["db"] = db
  app.config["users"] = db.Users
  app.config["bodies"] = db.Bodies
  
  # Tell the server admins whether multithreading is turned on
  if args.singlethread:
    print(" * Using Only One Thread!!")
  else:
    print(" * Multithreading!!")
  app.run(threaded= not args.singlethread,debug=args.debug, host='0.0.0.0')

if __name__ == "__main__":
  main(sys.argv[1:])
