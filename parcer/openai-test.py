import requests

headers={
    'Content-Type':'application/json',
    'Authorization':'Bearer sk-proj-dxycvKIaoR5og3YUthGCT3BlbkFJH5qcGIgRdCFCiaFrDbPB',

}

data={
    "model":"gpt-3.5-turbo",
    "messages":[{"role":"user","content":"Say this is a test"}],
    "temperature":0.7
}

response=requests.post('https://api.openai.com/v1/chat/completions',
headers=headers, json=data)
print(response.json())