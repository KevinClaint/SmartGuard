import glob
import json
import os
from time import sleep
import numpy as np
from Blockchain.tools import Detector


test=False
sleep_time=1

num2label = {'0': 'none', '1': 'Overflow-Underflow', '2': 'Re-entrancy', '3': 'Timestamp-Dependency'}

def extract_filename(path):
    return os.path.basename(path)

def find_sol_files(folder_path):
    sol_files = []
    for file in glob.glob(os.path.join(folder_path, '*.sol')):
        sol_files.append(file[:-4])
    return sol_files

def get_labels(label_path):
    labels = []
    with open(label_path, 'r') as f:
        content=f.readlines()
        for line in content:
            labels.append(line.strip())
    return labels

def get_names(name_path):
    names = []
    with open(name_path, 'r') as f:
        content=f.readlines()
        for line in content:
            names.append(line.strip())
    return names

def nameMlabel(names,labels):
    dataset={}
    for i in range(len(labels)):
        dataset[names[i]]=[]
        numlabels=labels[i].split(',')
        for numlabel in numlabels:
            dataset[names[i]].append(num2label[numlabel])
    return dataset

name_path=r""
label_path=r""
dataset_path=r""
target_json_path=""

detector= Detector('')


labels=get_labels(label_path)
names=get_names(name_path)
dataset=nameMlabel(names,labels)


wrongs=[]
last_num=30
while True:
    num=1
    try:
        for key in dataset:
            if num!=last_num:
                num+=1
                continue
            last_num=num
            num+=1
            print(key)
            file_path=os.path.join(dataset_path,key+".sol")
            with open(file_path, 'r+',encoding="utf-8") as f:
                content = f.read()
                times=0
                while True:
                    flags = [0] * (len(dataset[key]))
                    if 'none' not in dataset[key]:
                        if times==0:
                            if not test:
                                sleep(sleep_time)
                                result = detector.detect(content)
                            else:
                                result = {'answer': 'yes', 'type': 'Overflow-Underflow', 'reason': 'test'}
                        elif times<=6:
                            prompt=content+'\n'+"And your answer:"+json.dumps(result)+" may have some errors, please rethink again."
                            if not test:
                                sleep(sleep_time)
                                result = detector.detect(prompt)
                        elif times<=8:
                            right_answer={"answer":"yes","type":"","reason":""}
                            for i, flag in enumerate(flags):
                                if flag==0:
                                    right_answer['type']+=dataset[key][i]+','
                            right_answer['type']=right_answer['type'][:-1]
                            prompt=content+'\n'+"And your answer:"+json.dumps(result)+" may have some errors.The right answer is"+json.dumps(right_answer)+", please help me explain the reason."
                            if not test:
                                sleep(sleep_time)
                                result = detector.detect(prompt)
                        elif times==10:
                            wrongs.append(key)
                            break
                        if result:
                            if result['answer']=='yes':
                                types=result['type'].split(',')
                                for type in types:
                                    if type in dataset[key]:
                                        flags[dataset[key].index(type)]=1
                                if np.sum(flags)==len(types):
                                    if not test:
                                        with open(os.path.join(target_json_path,key+".json"), 'w+',encoding="utf-8") as j:
                                            if 9 >= times > 6:
                                                result['att'] = "1"
                                            print(result)
                                            json.dump(result, j)
                                    break
                                else:
                                    times+=1
                                    continue
                            else:
                                times+=1
                                continue
                        else:
                            times+=1
                            continue
                    else:
                        if times == 0:
                            if not test:
                                sleep(sleep_time)
                                result = detector.detect(content)
                            else:
                                result = {'answer': 'yes', 'type': 'Overflow-Underflow', 'reason': 'test'}
                        elif 3 >= times > 0:
                            prompt = content + '\n' + "And your answer:" + json.dumps(result) + " may have some errors, please help me check again."
                            if not test:
                                sleep(sleep_time)
                                result = detector.detect(prompt)
                        elif 6 >= times > 3:
                            prompt = content + '\n' + "And your answer:" + json.dumps(
                                result) + " may have some unrecognised vulnerabilities, please help me check again."
                            if not test:
                                sleep(sleep_time)
                                result = detector.detect(prompt)
                        elif 9 >= times > 6:
                            right_answer = {"answer": "none", "type": "none", "reason": ""}
                            prompt = content + '\n' + "And your answer:" + json.dumps(result) + " may have some errors.The right answer is" + json.dumps(right_answer) + ", please help me explain the reason."
                            if not test:
                                sleep(sleep_time)
                                result = detector.detect(prompt)
                        elif times == 10 :
                            wrongs.append(key)
                            break
                        if result['answer'] == 'no':
                            with open(os.path.join(target_json_path, key + ".json"), 'w+', encoding="utf-8") as j:
                                if 9 >= times > 6:
                                    result['att'] ="1"
                                print(result)
                                json.dump(result, j)
                            break
                        else:
                            times += 1
                            continue
    except Exception as e:
        print("Error:",e)

with open(os.path.join(target_json_path,"wrong.txt"), 'w+',encoding="utf-8") as f:
    for wrong in wrongs:
        f.write(wrong+'\n')


