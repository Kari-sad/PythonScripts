# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 03:09:25 2019

@author: saikarthik.n
"""

from flask import Flask , jsonify , request
from flask_restful import Api , Resource
from pymongo import MongoClient
import bcrypt
# =============================================================================
# import requests
# import subprocess
# import json
# =============================================================================

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
mydb = client['WhoAmI']
mycoll = mydb['CanYouFindMe']

tocken_count = 0
## Pre Registrattion Checks
def RegisterCheckData(postedData):
    if 'user_name' not in postedData or 'first_name' not in postedData or 'last_name' not in postedData or 'password' not in postedData:
        StatusCode = 301
        Message = "Missing Mandatory Parameters"
        return StatusCode, Message
    elif len(postedData['password']) < 6 or len(postedData['password']) >= 13 or len(postedData['user_name']) < 5 or len(postedData['user_name']) >= 13 :
        StatusCode = 302
        Message = "Please give a value which is more than 6 characters to 12 characters"
        return StatusCode, Message
    else:
        StatusCode = 200
        Message = "Successfully created the User"
        return StatusCode, Message
 

def checkUserExists(user_name):
    try:
        mycoll.find_one({ "user_name"  : user_name })['user_name']
    except Exception:
        user = 0
    else:
        user = 1
    if user > 0:
        StatusCode = 303
        # Message = "Username already exist, please choose another"
        return StatusCode


def checkPasswd(user_name , password , hashed_password):
    try:
        pass_user1 = mycoll.find_one({ "user_name"  : user_name })['password']
        pass_user2 = mycoll.find_one({ "user_name"  : user_name })["user_name"]
    except Exception:
        CallFalse = 1
    else:
        CallFalse = 0
    if CallFalse == 1:
        StatusCode = 310
    else:
        if bcrypt.checkpw(password.encode('utf8') , pass_user1) or user_name != pass_user2:
            StatusCode = 305
            Message = "Authentication Error, Invalid Username or Password"
            return StatusCode, Message


class Register(Resource):
    def post(self):
        getPostedData = request.get_json()
        StatusCode, Message = RegisterCheckData(getPostedData)
        SendResponse = {
                "Message": Message,
                "Status Code": StatusCode
            }

        if StatusCode != 200:
            return jsonify(SendResponse)
        else:
            user_name = str(getPostedData["user_name"]).strip().lower()
            password = str(getPostedData["password"]).strip()
            first_name = str(getPostedData["first_name"]).strip().lower()
            last_name = str(getPostedData["last_name"]).strip().lower()
            hpass = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
            ## Inserting the values in DB
            UStatusCode = checkUserExists(user_name)
            if UStatusCode == 303:
                result = {"Status": UStatusCode,
                          "Message": "Username already exist, please choose another"}
                return jsonify(result)
            
            insert_result = mycoll.insert_one(
                {
                    "first_name": first_name,
                    "last_ name": last_name,
                    "user_name" : user_name,
                    "password" :  hpass,
                    "sentence" : "",
                    "token" : 10
                }
            )

            if insert_result.acknowledged:
                SendResponse = {
                "Message": Message,
                "Status Code": StatusCode,
                "Transaction" : "Inserted the given records in the Document"
                    }
            return jsonify(SendResponse)




class ClassifyMe(Reso):
    pass





# =============================================================================
## API Router
api.add_resource(Register , "/register")
# =============================================================================

if __name__=="__main__":
    app.run(host='0.0.0.0' , debug=True)