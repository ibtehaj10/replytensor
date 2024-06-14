from flask import Flask, request, jsonify
import pandas as pd
from csv import writer

import os
import time
# import bittensor as bt
import requests
import json
import jsonpickle


app = Flask(__name__)





miner_api_key =  "9eKEnV1qyVuNyGC6FvL_RIJR48vUKCbkhCWiVUok0Ij9khzrjGJToNhpq7z3iwVX"


########################################################### GET best UIDS ##########################################################
import requests
def uids():
    headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {miner_api_key}",
                "Endpoint-Version": "2023-05-19",
            }

    params = {
        'n':10
    }
    r = requests.get('http://test.neuralinternet.ai/top_miner_uids',headers=headers,params=params)
    return r.json()


# prompt = bt.BittensorLLM()
############## GPT PROMPT ####################
def bittensor(inp,ind):
#    if len(inp) > 5:
 #       inp = inp[-5:]
    systems = {"role":"system","content":"""
               you're an AI assistant. your name is ReplyTensor.
                You are developed by the Team of Neural Internet on Bittensor Protocol .
               Dont greet untill you are greeted.only tell about yourself if someone as 
               one ask about it.remember you are powered by Bittensor not GPT or anything.
                Never mention OpenAI or chatGPT in your intro."""}

    new_inp = inp
    new_inp.insert(0,systems)
#    uid = uids()[ind]
    url = "https://sn18.neuralinternet.ai/textgen"
    #uid = uids()
    print('################### new input chat : ',new_inp)
    payload = json.dumps({

  "messages": new_inp,
  "engine": "gpt-4"
})
    headers = {
  'Content-Type': 'application/json',
   "Authorization": f"Bearer {miner_api_key}",
}

    response = requests.request("POST", url, headers=headers, data=payload)
    res = response.json()
    print(res)
    #return str(res['choices'][0]['message']['content'])
    for i in res["choices"]:
        b = i['message']['content']
        if b.endswith('.') or b.endswith('?'):
            print("Final result",b,"\n")
            return b
#        else:
 #           pass
         #   return "No Miner is able to reply at the moment"

############    GET CHATS BY USER ID ##################
def get_chats(id):
    # path = str(os.getcwd())+'//chats//'+id+'.json'
    path = id
    isexist = os.path.exists(path)
    if isexist:
        data = pd.read_json(path)
        chats = data.chat
        return  list(chats)
    else:
        return "No Chat found on this User ID."





############### APPEND NEW CHAT TO USER ID JSON FILE #################
def write_chat(new_data, id):
    with open(id,'r+') as file:
          # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["chat"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)



################################ CHECK IF USER IS ALREADY EXIST IF NOT CREATE ONE ELSE RETURN GPT REPLY ##################
@app.route('/api', methods=['POST'])
def check_user():

    ids = request.json['user_id']
    prompt = request.json['prompt']
    print("asd")
    path = str(os.getcwd())+'//chats//'+ids+'.json'
    # path = str(os.getcwd())+'\\'+"5467484.json"
    isexist = os.path.exists(path)
    if isexist:
        # try:
        print(path," found!")
        write_chat({"role":"user","content":prompt},path)
        chats = get_chats(path)
        send = bittensor(chats,0)
        reply = send
        print("reply    ",reply)
        write_chat({"role":"assistant","content":reply},path)
        return {"message":reply,"status":"OK"}
        # except:
        # except:
        #     return {"message":"something went wrong!","status":"404"}

    else:
        print(path," Not found!")
        dictionary = {
        "user_id":ids,
        "chat":[]


        }

        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        # Writing to sample.json
        with open(path, "w") as outfile:
            outfile.write(json_object)
        reply = check_user()
        return reply

####################   NEW ENPOINT GET CHAT ##############################
@app.route('/get_chats', methods=['POST'])
def get_chatss():
    ids = request.json['user_id']
    return jsonpickle.encode(get_chats(ids))

#################################### DELETE CHATS ##############################

@app.route('/delete_chats', methods=['POST'])
def clear_chatss():
    ids = request.json['user_id']

    try:
        path =os.remove(str(os.getcwd())+'//chats//'+ids+'.json')

        return {"status":"OK","message":"success"}

    except :
        return { "status":"error","message":"Something went wrong,chat doesn't exist" }


####################   Regenerate ##############################
@app.route('/regenerate', methods=['POST'])
def regenerate():
    ids = request.json['user_id']
    path = str(os.getcwd())+'//chats//'+ids+'.json'
    print(path)
    chats = get_chats(path)
    print(chats)
    chats.pop()
    print(chats)
    reply = bittensor(chats,1)
    return {"message":reply,"status":"OK"}

if __name__ == '__main__':
    app.run(port=5005,host='0.0.0.0',threaded=True)

