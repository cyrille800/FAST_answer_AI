import base64
import requests
import google.generativeai as genai
import google.ai.generativelanguage as glm
from concurrent.futures import ThreadPoolExecutor
import pathlib
import anthropic
from ocr import ocr_files
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPEN_AI_GPT_KEY = os.getenv("OPEN_AI_GPT_KEY")

MODEL_OPEN_AI_GPT = os.getenv("MODEL_OPEN_AI_GPT")
MODEL_OPUS_AI_GPT = os.getenv("MODEL_OPUS_AI_GPT")
MODEL_GEMINI_AI = os.getenv("MODEL_GEMINI_AI")


genai.configure(api_key = GEMINI_API_KEY)
client = anthropic.Anthropic(
    api_key=ANTHROPIC_API_KEY,
)

def fetch_gpt_response(image_path, msg, method):
    """Fonction pour obtenir la réponse de l'API GPT."""
    try:
        
        api_key_gpt = OPEN_AI_GPT_KEY
    
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key_gpt}"
        }
        
        content_sys = [{
                "type": "text",
                "text": "here are the captures of the exercise statement" if method == None else "here is the result of the ocr performed on screen captures :"+method
                }]
        
        if method == None:
            for img in image_path:
                encode = encode_image(img)
                content_sys.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode}"
                    }
                    })
        
        payload = {
        "model": MODEL_OPEN_AI_GPT,
        "messages": [
            {
            "role": "system",
            "content": [{
                "type": "text",
                "text": msg
                }]
            },
            {
            "role": "user",
            "content": content_sys
            }
        ],
        "temperature": 0
        }
        
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        json_response = response.json()
        content = json_response.get("choices")[0].get("message").get("content")
        return content.split("[-]")[0]
    except Exception as e:
        return "error"

def fetch_opus_response(image_path, msg, method):
    """Fonction pour obtenir la réponse du modèle de vision."""
    try:
        
        content_sys = []
        
        content_sys.append({
            "type": "text",
            "text": "here are the captures of the exercise statement" if method == None else "here is the result of the ocr performed on screen captures :"+method
        })
                
        if method == None:
            for index,  img in enumerate(image_path):
                encode = encode_image(img)
                content_sys.append({
                        "type": "text",
                        "text": f"Image {index}:"
                    })
                content_sys.append(
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": encode,
                        },
                    })
            

        message = client.messages.create(
            model= MODEL_OPUS_AI_GPT,
            max_tokens=4096,
            temperature=0,
            system=msg,
            messages=[
                {
                    "role": "user",
                    "content": content_sys
                }
            ]
        )
        
        return message.content[0].text.split("[-]")[0]
    except Exception as e:
        print(e)
        return "error"
    
def fetch_gemini_response(image_path, msg, method):
    """Fonction pour obtenir la réponse du modèle de vision."""
    try:
        
        if method == None:
            msg = "here are the captures of the exercise statement . " + msg
        else:
            msg = "here is the result of the ocr performed on screen captures :"+method + msg
        pt = [glm.Part(text=msg)]
        if method == None:
            for ing in image_path:
                pt.append(glm.Part(
                    inline_data=glm.Blob(
                        mime_type='image/*',
                        data=pathlib.Path(ing).read_bytes()
                    )
                ))

        model = genai.GenerativeModel(MODEL_GEMINI_AI)
        response = model.generate_content(glm.Content(
            parts = pt,
        ),generation_config={"temperature":0})
        
        response.resolve()
        return response.text.split("[-]")[0]
    except Exception as e:
        print(e)
        return "error"
    
# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def get_reponse_chat_gpt(image_path, type="default", is_ocr=False, pat = ""):
    
    msg = ""
    res = None
    if is_ocr==False:
        msg = "You are an expert in IT development, DevOps and Agile. Answer the exercise in the images by providing only the answer, and give a concise explanation of no more than three lines. Separate the answer from the explanation with the separator '[-]' ."
    else:
        res = ocr_files(image_path)
        msg = f"You are an expert in IT development, DevOps and Agile. Answer the exercise based on the results of the OCR performed on screen captures, providing only the answer. Then give a concise explanation, in no more than three lines, and separate the answer from the explanation with the '[-]' separator ."

        
    with ThreadPoolExecutor(max_workers=3) as executor:
        gpt_future = executor.submit(fetch_gpt_response, image_path, msg, res)
        gemini_future = executor.submit(fetch_gemini_response, image_path, msg, res)
        opus_future = executor.submit(fetch_opus_response, image_path, msg, res)

    data = {
        "gpt": gpt_future.result(),
        "gemini": gemini_future.result(),
        "opus": opus_future.result()
    }
    
    gpt = data["gpt"]
    gemini = data["gemini"]
    opus = data["opus"] 
        

    if not os.path.exists(f"{pat}"):
        os.makedirs(f"{pat}")
            
    files = ['gpt.txt', 'gemini.txt', 'opus.txt']
    texts = [gpt, gemini, opus]

    for file_name in files:
        with open(file_name, 'w') as fichier:
            fichier.write(texts[files.index(file_name)])
            
        with open(f'{pat}/{file_name}', 'w') as fichier:
            fichier.write(texts[files.index(file_name)])
            
    return data