from g4f.client import Client
client = Client()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "напиши анекдот про беларуса"}],

)
print(response.choices[0].message.content)
