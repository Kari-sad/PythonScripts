# -*- coding: utf-8 -*-
"""
Created on Sun Dec 15 03:09:25 2019

@author: saikarthik.n
"""

from flask import Flask , jsonify , request
from flask_restful import Api , Resource
from pymongo import MongoClient
import bcrypt
import spacy

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


## Post Registrattion Checks
def ICommentCheckData(postedData):
    global tocken_count
    tocken_count = mycoll.find_one({ "user_name"  : postedData['user_name'] })['token']
    if 'user_name' not in postedData or 'password' not in postedData:
        StatusCode = 304
        Message = "Missing Mandatory Parameters"
        return StatusCode, Message
    elif tocken_count <= 0 :
        StatusCode = 306
        Message = "Unable to Store, no Tokens"
        return StatusCode, Message
    else:
        StatusCode = 200
        Message = "Comments stored Successfully"
        return StatusCode, Message

def checkCred(user_name , password):
    try:
        pass_user1 = mycoll.find_one({ "user_name"  : user_name })['password']
        pass_user2 = mycoll.find_one({ "user_name"  : user_name })["user_name"]
    except Exception:
        CallFalse = 1
    else:
        CallFalse = 0
    if CallFalse == 1:
        StatusCode = 310
        return StatusCode
    else:
        if bcrypt.checkpw(password.encode('utf8') , pass_user1) and user_name == pass_user2:
            StatusCode = 220
            return StatusCode
        else:
            StatusCode = 305
            return StatusCode


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



class ReFillCredits(Resource):
    def post(self):
        getPostedData = request.get_json()
        StatusCode = checkCred(getPostedData['user_name'] , getPostedData['password'])
        if StatusCode != 220:
            SendResponse = {
                "Message" : "Authentication Error, Invalid Username or Password",
                "Status Code" : StatusCode
                }
            return jsonify(SendResponse)

        else:
            user_name = str(getPostedData["user_name"]).strip().lower()
            admin_user_name = str(getPostedData["user_name"]).strip().lower()
            refil_count = int(getPostedData["refil_count"])
            
            if admin_user_name == 'Karthik@123':
                refilled = mycoll.update_one(
                    { "user_name" : user_name } ,
                    {
                        "$set":
                        {
                        "token" : tocken_count + refil_count
                        }})
                if refilled.acknowledged:
                    return jsonify(SendResponse)
                else:
                    return jsonify(SendResponse)

class ComparePlag(Resource):
    def post(self):
        getPostedData = request.get_json()
        StatusCode = checkCred(getPostedData['user_name'] , getPostedData['password'])
        if StatusCode != 220:
            SendResponse = {
                "Message" : "Authentication Error, Invalid Username or Password",
                "Status Code" : StatusCode
                }
            return jsonify(SendResponse)

        else:
            user_name = str(getPostedData["user_name"]).strip().lower()
            comment1 = str(getPostedData["sentence1"]).strip()
            comment2 = str(getPostedData["sentence1"]).strip()
            password = str(getPostedData["password"]).strip()

            StatusCode = checkCred(user_name , password)
            if StatusCode != 220:
                SendResponse = {
                "Message" : "Authentication Error, Invalid Username or Password",
                "Status Code" : StatusCode
                }
                return jsonify(SendResponse)
            else:
                nlp = spacy.load('en_core_web_sm')
                text1 = nlp(comment1)
                text2 = nlp(comment2)
                ratio = text1.similarity(text2)
                
                update_result = mycoll.update_one(
                { "user_name" : user_name } ,
                {
                    "$set":
                    {
                    "token" : tocken_count - 1
                 }})
                SendResponse = {
                    
                    "Status Code" : StatusCode,
                    "Message" : "Comparission Successful",
                    "Ratio" : ratio
                    }
                if update_result.acknowledged:   
                    return jsonify(SendResponse)
                else:
                    SendResponse = {
                    
                    "Status Code" : StatusCode,
                    "Message" : "Error",
                    }
                    return jsonify(SendResponse)

api.add_resource(Register , "/register")
api.add_resource(ComparePlag , "/compare")
api.add_resource(ReFillCredits , "/recharge")

if __name__=="__main__":
    app.run(host='0.0.0.0' , debug=True)