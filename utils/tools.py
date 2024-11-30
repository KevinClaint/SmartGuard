import json
from time import sleep

import openai


openai.api_base = ''
openai.api_key = ''

class Detector:
    def __init__(self,bg=""):
        self.bg=bg

    def detect(self,prompt):
        num=0
        while True:
            text=self.get_answer(self.bg+prompt)
            if text:
                Js=self.is_json(text)
                if Js:
                    return Js
                else:
                    num+=1
                    if num>10:
                        return False
                    else:
                        continue
            else:
                num+=1
                if num>10:
                    return False
                else:
                    continue

    def get_answer(self,prompt):
        wrong=0
        while True:
            try:
                messages = [
                    {"role": "user", "content": prompt}
                ]
                res = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    stream=False,
                )
                return res['choices'][0]['message']['content']
            except Exception as e:
                print("Request Error",e)
                if "error" in str(e):
                    wrong+=1
                    if wrong<10:
                        sleep(2)
                        continue
                return False

    def is_json(self,text):
        if "json" in text:
            text=text[7:-3]
        print(text)
        try:
            Js=json.loads(text)
        except ValueError as e:
            print("Json Format Error:",e)
            return False
        return Js

