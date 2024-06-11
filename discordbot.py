
# This is new in the discord.py 2.0 update
import cv2
from nltk.tokenize import sent_tokenize
from config import Token
import discord
from discord.ext import commands
import requests
import asyncio
import json
from PIL import Image
import numpy as np
import random
import requests
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
from datetime import datetime
import os
from transformers import VitsModel, AutoTokenizer, pipeline, AutoFeatureExtractor, AutoModelForCTC, AutoTokenizer
import torch
import soundfile as sf
import requests
import base64
from io import BytesIO
import json
from PIL import Image
# Set the command prefix for your bot


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = discord.Bot(intents=intents)
#tts_model = VitsModel.from_pretrained("facebook/mms-tts-urd-script_arabic")
#tts_tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-urd-script_arabic")
tts_model = VitsModel.from_pretrained("facebook/mms-tts-eng")
tts_tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-eng")



miner_api_key =  "LoTuFvRqEHhJuTdl6V7yh-adBsVSegPRNGD9WMOsplI1xpVTIg8ON1OydyCecs9v"

def bittensor(user,message):

    user = user
    prompt = message

    headers={'Content-Type': 'application/json'}
    body = {
    "user_id":user,
    "prompt":prompt

    }
    r = requests.post('http://127.0.0.1:5005/api',headers=headers,json=body)
    ans = r.json()
    anss = ans['message']
    print(anss)
    if len(anss) <= 2000:

        return anss
    else:
        t = anss[:2000]

        return str(ans)+"."




def regenerate_prompt(user):

    user = user


    headers={'Content-Type': 'application/json'}
    body = {
    "user_id":user

    }
    r = requests.post('http://127.0.0.1:5005/regenerate',headers=headers,json=body)
    ans = r.json()
    anss = ans['message']
    # print(ans)
    return anss



def clearchat(userid):
    user = userid
    headers={'Content-Type': 'application/json'}
    body = {
    "user_id":user

    }
    r = requests.post('http://127.0.0.1:5005/delete_chats',headers=headers,json=body)
    ans = r.json()
    return ans
# Event: When the bot is ready and connected to Discord


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Command: Ping-Pong


@bot.command()
async def ping(ctx):
    print(ctx)
    await ctx.send('Pong!')





def tts(text,filename='audio.wav'):

    inputs = tts_tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        tts_output = tts_model(**inputs).waveform
    audio_data = tts_output.squeeze().cpu().numpy()
    sf.write(filename, audio_data, 16000)

    return  filename






@bot.slash_command(name="clear_replytensor",description="Clear chat context!")
async def clear_replytensor(ctx):
    users = ctx.author.name
    await ctx.response.defer()
#    await ctx.followup.send("working on it ...")
    clearchat(users)
    await ctx.respond("Success")






@bot.slash_command(name="regenerate",description="Regenerate Last prompt")
async def regenerate(ctx):
    if ctx.author == bot.user:
        return
    users = ctx.author.name
    await ctx.response.defer()
    response = regenerate_prompt(users)
    user_mention = ctx.author.mention
    await ctx.respond(user_mention+" "+response)





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

########## Fetch last prompt from json by user
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

def imagine_image(message, username):


        url = "https://sn18.neuralinternet.ai/imagegen"

        payload = json.dumps({
  "messages": message,
  "type": 'true',
})
        headers = {
  'Content-Type': 'application/json',
   "Authorization": f"Bearer LoTuFvRqEHhJuTdl6V7yh-adBsVSegPRNGD9WMOsplI1xpVTIg8ON1OydyCecs9v",
}

        response = requests.request("POST", url, headers=headers, data=payload)
#       print(response.text)
        json_resp = json.loads(response.text)
        image_b64 = json_resp['choices'][0]['location'].split(',')[1]
        image_data = base64.b64decode(image_b64)
        image_stream = BytesIO(image_data)
        image = Image.open(image_stream)
        filenames = 'images/'+username+'.jpg'
        image.save(filenames, format="JPEG")
        print(filenames)
        return filenames
################ hit the api and generate image########################
def generate(message):

    good_uids = [58, 175, 148, 178, 6, 115, 91, 142, 52, 118, 25, 117, 227, 237, 238, 86, 12, 36, 34, 208, 143, 59, 239, 154, 158, 105, 1, 51, 66, 157, 248, 151, 39, 242, 26, 15, 226, 228, 233, 241, 172, 207]
    for _ in range(0, len(good_uids)):
      try:
        good_uid = random.choice(good_uids)
        api_key='7X_6rpOPPRf8dA8IqI4nHIgTzzX-hhJhPTfJG14cIQ8XMYRoCs83wfcLdDXOy7Y1'
        url = 'http://65.108.32.175:9001/imagegen'
        print('message : ',message)
        payload = json.dumps(
                {"uids": [good_uid], "messages": [{"content": message}], "width": 1080, "height": 960 , "seed": -1, "num_images_per_prompt": 1, 'strategy': 'Round-Robin'}
            )

        headers = { "Authorization": f"Bearer {api_key}" }

        response = requests.request("POST", url, data=payload, headers=headers)

        image_data = response.json()
        print()

        arr = (np.asarray(json.loads(image_data)))
        image = np.transpose(arr, (1, 2, 0))
        image_rgb = image[..., ::-1]

        # file_path = f'logs_images/{str(uuid.uuid4())}.png'
        file_path = 'image.png'
        cv2.imwrite(file_path, image_rgb)
        return file_path
      except Exception as e:
        print(e)

badwords = ['pussy','blow job','boobs','boobies','tits','sex','fucking','fucks','naked','nsfw','dildow']

###############################send image to discord
@bot.slash_command(name="imagine",description="Generate Image with ReplyTensor")
async def imagine(ctx,message: str):
    print(ctx)
    users = ctx.author.name
    msg = message
    bads = 0
    for i in badwords:
        if i in msg:
            bads = 1
    if bads == 0:
        dump_json(msg,users)
        user_mention = ctx.author.mention
        await ctx.response.defer()
    # # Process the message and get the response
        response = imagine_image(msg,users)
        print(response)
        with open(response, "rb") as image_file:
            await ctx.respond(
                user_mention + "-"+msg,
                file=discord.File(image_file, filename="generated_image.png"),
            )
    else:
        await ctx.respond('your prompt `'+msg+'` Blocked by NI.')


########### Regenerate image


@bot.slash_command(name="reimagine",description="Regenerate Image with ReplyTensor")
async def reimagine(ctx):
    users = ctx.author.name
    msg = fetch_last_message_by_user(users)
    user_mention = ctx.author.mention
    await ctx.response.defer()
    response = imagine_image(msg,users)
    with open(response, "rb") as image_file:
            await ctx.respond(
                user_mention + "-"+msg,
                file=discord.File(image_file, filename="generated_image.png"),
            )



####################################################### Speech handling###################################

@bot.event
async def on_message(message):
        #print('message : ',message.content)
#       if bot.user.mentioned_in(message):
        if message.author == bot.user or not message.attachments:
                if bot.user.mentioned_in(message):
                        users = message.author.name
                        msg = message.content
                        msg = msg.replace("<@1051209066925531206> ","")
                        print("user message    :    ",msg)
                        user_mention = message.author.mention
                        response = bittensor(users, msg)
                        if len(response) < 2000:
                                await message.reply(response, mention_author=True)
                        else:
                                response = bittensor(users, "summarize this ` "+response+"`")
                                await message.reply(response, mention_author=True)
        else:
                        for attachment in message.attachments:
                                if attachment.filename.endswith(('.wav', '.mp3', '.ogg', '.m4a')):
                                        await message.reply('Listening your audio...' , mention_author=True)

            # Download the file
                                file_path = f'audios/{attachment.filename}'
                                await attachment.save(file_path)
            # Convert audio to WAV if necessary
                                if not attachment.filename.endswith('.wav'):
                                        sound = AudioSegment.from_file(file_path)
                                        file_path = file_path.replace(attachment.filename.split('.')[-1], 'wav')
                                        sound.export(file_path, format='wav')

            # Transcribe the audio file
                                recognizer = sr.Recognizer()
                                with sr.AudioFile(file_path) as source:
                                        audio_data = recognizer.record(source)
                                        try:
                                                text = recognizer.recognize_google(audio_data)
                                                name = message.author.name
                                                reply = bittensor(name,text)
                                                if len(reply) < 2000:
                                                        await message.reply(reply, mention_author=True)
                                                        ttss = tts(reply)
                                                        await message.reply(file=discord.File(ttss))
                                                else:
                                                        response = bittensor(users, "summarize this ` "+reply+"`")
                                                        await message.reply(reply, mention_author=True)
                                                        await message.reply(file=discord.File(audio_file))
                                        except sr.UnknownValueError:
                                                await message.channel.send("Could not understand the audio.")
                                        except sr.RequestError:
                                                await message.channel.send("Error: Service is unavailable.")

            # Clean up the downloaded file
                        if os.path.exists(file_path):
                                os.remove(file_path)
#       await bot.process_commands(message)

############################################################################# Speech to text done









bot.run(Token)
