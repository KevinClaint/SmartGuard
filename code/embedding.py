import json
import os

import numpy as np
import torch
from tqdm import tqdm
from transformers import BertTokenizer, BertModel, RobertaTokenizer, RobertaModel

def create_name2text(path):
    name2text = {}
    files = os.listdir(path)
    for file in files:
        filename = file.split('.')[0]
        filepath = os.path.join(path, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            name2text[filename] = content

    with open(os.path.join(path,'name2text.json'), 'w', encoding='utf-8') as f:
        json.dump(name2text, f, ensure_ascii=False, indent=4)

    return True


device=torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
modelname=".\modelcache\codebertbase"
tokenizer = RobertaTokenizer.from_pretrained(modelname)
model = RobertaModel.from_pretrained(modelname)
model.to(device)
model.eval()

def create_text_vector(name2text=None,output_path=None):
    feature_features_dict= {}
    for nt in tqdm(name2text):
        text=name2text[nt]
        inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
        if inputs['input_ids'].shape[1] > 512:
            inputs['input_ids'] = inputs['input_ids'][:, :512]
            inputs['attention_mask'] = inputs['attention_mask'][:, :512]
        inputs=inputs.to(device)
        with torch.no_grad():
            outputs = model(**inputs)
        hidden_states = (outputs.last_hidden_state).cpu()
        avg_vector = torch.mean(hidden_states, dim=1).squeeze().numpy()
        feature_features_dict[nt]=avg_vector
    if output_path is not None:
        np.save(output_path, feature_features_dict)

def cosine_similarity(vector1, vector2):
    dot_product = np.dot(vector1, vector2)
    norm1 = np.linalg.norm(vector1)
    norm2 = np.linalg.norm(vector2)
    similarity = dot_product / (norm1 * norm2)
    return similarity

def query(query_text, feature_vectors, feature_names, num=64):
    inputs = tokenizer(query_text, padding=True, truncation=True, return_tensors="pt",max_length=512)
    inputs = inputs.to(device)
    with torch.no_grad():
        outputs = model(**inputs)
    query_vector = torch.mean((outputs.last_hidden_state).cpu(), dim=1).squeeze().numpy()
    similarities = []
    for i in range(len(feature_vectors)):
        similarity = cosine_similarity(query_vector, feature_vectors[i])
        similarities.append((similarity, feature_names[i]))
    similarities.sort(reverse=True)
    return similarities[:num]
