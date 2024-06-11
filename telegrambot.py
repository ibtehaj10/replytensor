import telebot
from config import apikey
import requests
import json
import uuid
import numpy as np
import cv2
import random
from datetime import datetime
import os
import requests
import base64
from io import BytesIO
import json
import io
from PIL import Image
from transformers import VitsModel, AutoTokenizer, pipeline
import torch
from pydub import AudioSegment
from scipy.io import wavfile
import soundfile as sf
import speech_recognition as sr

import requests
import json

import base64
from io import BytesIO
from PIL import Image

TOKEN = apikey
bot = telebot.TeleBot(TOKEN)


# Ensure the 'audios' directory exists
if not os.path.exists('audios'):
    os.makedirs('audios')
from PIL import Image


# Load the TTS model
tts_model = VitsModel.from_pretrained("facebook/mms-tts-eng")
tts_tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")

############################################### SPeech Recognition
def STT(filename):
    audio_file_path = 'audios/'+filename  # replace with your file path
    recognizer = sr.Recognizer()
    # Use the audio file as the source
    with sr.AudioFile(audio_file_path) as source:
        # Record the audio file
        audio_data = recognizer.record(source)

        # Recognize the content
        try:
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio_data)
            return text  # Urdu - Pakistan
            print("Recognized text:", text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")


################################################### Text TO Speech Handling
def tts(text,filename):

    inputs = tts_tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        tts_output = tts_model(**inputs).waveform
    audio_data = tts_output.squeeze().cpu().numpy()
    sf.write(filename, audio_data, 16000)

    return  filename


################################################ Handle Audio input
@bot.message_handler(content_types=['voice'])
def handle_audio(message):
    print('audio received')# Generate a random file name
    file_name = str(random.randint(1, 10)) + '.wav'
    user = message.from_user.id
    # Get file info and download the audio file
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Save the audio in .wav format
    with open('audios/' + file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Convert to WAV if necessary (if the original format isn't WAV)
    if not file_info.file_path.endswith('.wav'):
        audio = AudioSegment.from_file('audios/' + file_name)
        audio.export('audios/' + file_name, format='wav')
    text = STT(file_name)
    print('audio Text : ',text)
    prompt = text
    #prompt = prompts.replace("/chat","")
    headers={'Content-Type': 'application/json'}
    body = {
    "user_id":str(user),
    "prompt":prompt

   }
    r = requests.post('http://127.0.0.1:5002/api',headers=headers,json=body)
    ans = r.json()
    print(ans)
    anss = ans['message']
  # print(ans
    filename = 'gen_audios/'+str(user)+'.wav'
    audio_data = tts(anss,filename)
    audio = open(audio_data, 'rb')
    bot.send_audio(message.chat.id, audio)
    audio.close()
    #audio_buffer = io.BytesIO()
    #audio_data.write(audio_buffer, rate, audio_data)
    #audio_buffer.seek(0)
    #bot.send_audio(message.chat.id, audio=audio_buffer, title='TTS Audio')
    bot.reply_to(message, anss)
    # Reply with 'Hello' when an audio is received
   # bot.reply_to(message, "Hello")

############################################### Handle start
@bot.message_handler(commands=['start'])
def send_welcome(message):
        bot.reply_to(message, "Howdy, how are you doing?")





############################################# Handle  /chat command (Text messages)
@bot.message_handler(commands=['chat'])
def echo_all(message):
  print(message)

  user = message.from_user.id
  prompts = message.text
  prompt = prompts.replace("/chat","")
  headers={'Content-Type': 'application/json'}
  body = {
    "user_id":str(user)+"-telegram",
    "prompt":prompt

  }
  r = requests.post('http://127.0.0.1:5002/api',headers=headers,json=body)
  ans = r.json()
  print(ans)
  anss = ans['message']
  # print(ans)
  bot.reply_to(message, anss)











##################################################### Get  latest  prompt by user

def fetch_last_message_by_user(user_id):
    try:
        with open('last_messages.json', 'r') as file:
            last_messages = json.load(file)
            if user_id in last_messages:
                return last_messages[user_id]['text']
            else:
                return "User not found in the records."
    except FileNotFoundError:
        return "No message records found."



@bot.message_handler(commands=['help'])
def echo_all(message):
  msg = """
Hi!

I am ReplyTensor your personal assistant.

To ask me anything use /chat command.

To generate images based on prompt use /imagine command.

To Regenerate the  image again on the given prompt use /reimagine.

Use /clear command to clear the context.

Happy Generating! :)
"""
  bot.reply_to(message, msg)




############################################ Handle Clear funtion to clear chats

@bot.message_handler(commands=['clear'])
def echo_all(message):
  user = message.from_user.id
  headers={'Content-Type': 'application/json'}
  body = {
    "user_id":str(user),
  }
  r = requests.post('http://127.0.0.1:5002/delete_chats',headers=headers,json=body)
  ans = r.json()
  bot.reply_to(message, ans['message'])




##################################################### Funtion that dump last  prompt by every user in Json #####################################
def dump_json(message,id):
    # Create a dictionary to store the last message from each user
    last_messages = {}
    now = datetime.now()
    # Load the existing data from a JSON file if it exists
    try:
        with open('last_messages.json', 'r') as file:
            last_messages = json.load(file)
    except FileNotFoundError:
        pass
    print(message,"json dump")
    user_id = id
    user_data = {
        'text': message,
        'date': str(now)
    }

    # Check if the user is already in the dictionary
    if user_id in last_messages:
        # Update the user's last message
        last_messages[user_id] = user_data
    else:
        # Add a new entry for the user
        last_messages[user_id] = user_data

    # Save the updated data to the JSON file
    with open('last_messages.json', 'w') as file:
        json.dump(last_messages, file)
    return

##################### IMAGE GENERATION SN 18
miner_api_key = "LoTuFvRqEHhJuTdl6V7yh-adBsVSegPRNGD9WMOsplI1xpVTIg8ON1OydyCecs9v"
url = "https://sn18.neuralinternet.ai/imagegen"
def imagine_image(message, username):


        url = "http://localhost:8002/imagegen"

        payload = json.dumps({
  "messages": message,
  "type": 'true',
})
        headers = {
  'Content-Type': 'application/json',
   "Authorization": f"Bearer 9eKEnV1qyVuNyGC6FvL_RIJR48vUKCbkhCWiVUok0Ij9khzrjGJToNhpq7z3iwVX",
}

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)
        json_resp = json.loads(response.text)
        image_b64 = json_resp['choices'][0]['location'].split(',')[1]
        image_data = base64.b64decode(image_b64)
        image_stream = BytesIO(image_data)
        image = Image.open(image_stream)
        filenames = 'images/'+username+'_telegram.jpg'
        image.save(filenames, format="JPEG")
        print(filenames)
        return filenames
# def generate_top_response(message,username):
#     good_uids = [39, 8, 180, 41, 201, 79, 172, 59, 231, 134, 67, 85, 96, 112, 191, 3, 160, 254, 84, 64, 185, 199, 188, 107, 239, 151, 175, 194, 103, 78, 246, 58, 143, 118, 211, 77, 223, 99, 52, 9, 158, 105, 22, 234, 44, 208, 214, 209, 1]


#     for _ in range(0, len(good_uids)):
#       try:
#         good_uid = random.choice(good_uids)
#         api_key='7X_6rpOPPRf8dA8IqI4nHIgTzzX-hhJhPTfJG14cIQ8XMYRoCs83wfcLdDXOy7Y1'
#         url = 'http://0.0.0.0:8001/image'
#         print('message : ',message)
#         payload = json.dumps({
#   "messages": message,
#   "type": 'true',
# })

#         headers =  {
#   'Content-Type': 'application/json'
# }

#         response = requests.request("POST", url, data=payload, headers=headers)

#         image_data = response.json()
#         print()

#  #       arr = (np.asarray(json.loads(image_data)))
#   #      image = np.transpose(arr, (1, 2, 0))
#    #     image_rgb = image[..., ::-1]

#         file_path = image_data['choices'][0]['content']
#         #cv2.imwrite(file_path, image_rgb)
#         return file_path
#       except Exception as e:
#         print(e)




################################################### Telegram message handler that handles imagine command to generate image from random UIDs ###################################
@bot.message_handler(commands=['imagine'])
def send_image(message):
    text = message.text
    print(message,text)
    username = message.from_user.id
    newpath = imagine_image(str(text),str(username))
    chat_id = message.chat.id
    #dump_json(text,username)
    print("newpath  : ",newpath)
    #file_path = f'/tmp/{str(uuid.uuid4())}.png'
    bot.send_photo(chat_id, open(str(newpath),'rb'),reply_to_message_id=message.message_id)
    dump_json(str(text),str(username))


######################################################### Text  regenration funtion  #####################################
@bot.message_handler(commands=['regenerate'])
def echo_all(message):
  user = message.from_user.id
  headers={'Content-Type': 'application/json'}
  body = {
    "user_id":str(user),
  }
  r = requests.post('http://127.0.0.1:5002/regenerate',headers=headers,json=body)
  ans = r.json()
  bot.reply_to(message, ans['message'])




@bot.message_handler(commands=['reimagine'])
def send_im(message):
    #newpath = generate_image(message)
    username = message.from_user.id
    text = fetch_last_message_by_user(str(username))
    print(text,"reimagine text ")
    chat_id = message.chat.id
#    dump_json(message.text,username)
    print()
    newpath = imagine_image(text,str(username))
    print(text,"we are reimagining")    #file_path = f'/tmp/{str(uuid.uuid4())}.png'
    bot.send_photo(chat_id,  open(str(newpath),'rb'),reply_to_message_id=message.message_id)


############################################## Get Generated Video
def video_gen(prompt):
  url = "http://65.108.32.175:8060/video"

  payload = json.dumps({
    "prompt": prompt

  })
  headers = {
    'Content-Type': 'application/json'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  # print(response.text)
  return response.text



####################################################### Save Generated Video
def save_video(filename,data):
  decoded_data = base64.b64decode(data)
  file_path = str(filename)+".mp4"
  with open(file_path, "wb") as file:
      file.write(decoded_data)

  print(f"Video saved to {file_path}")
  return file_path
####################################################### VIDEO GENERATION
@bot.message_handler(commands=['video'])
def echo_all(message):
    msg = message.text
    id = message.id
    data = video_gen(msg.replace("/video",""))
    video_path = save_video(id,data)
    if video_path:
        # Send the video back to the user
        with open(video_path, 'rb') as video:
            bot.send_video(message.chat.id, video, reply_to_message_id=id)
    else:
        # Handle the case where video could not be saved or processed
        bot.reply_to(message, "Failed to process the video.")

bot.infinity_polling()

