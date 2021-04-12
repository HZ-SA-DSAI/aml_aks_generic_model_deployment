#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# MIT License

# Copyright (c) 2021 HZ-MS-CSA

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# ### Model Scoring

# In[ ]:


import json
import pandas as pd
import os
import pickle
import joblib
import os
from azureml.core.workspace import Workspace
from azureml.core.model import Model
from azureml.core.authentication import ServicePrincipalAuthentication
from flask import Flask
from flask_restful import Resource, Api, reqparse

import string
import re
import os
import numpy as np
import pandas as pd
import urllib.request
import json
import keras
from keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
from azureml.core.model import Model
import onnxruntime


# In[ ]:


# Use Service Principal

sp = ServicePrincipalAuthentication(tenant_id=os.environ['TENANT_ID'], # tenantID
                                    service_principal_id=os.environ['CLIENT_ID'], # clientId
                                    service_principal_password=os.environ['CLIENT_SECRET']) # clientSecret

ws = Workspace.get(name=os.environ['WORKSPACE_NAME'],
                   auth=sp,
                   subscription_id=os.environ['SUBSCRIPTION_ID'],
                  resource_group=os.environ['RESOURCE_GROUP'])


# In[ ]:
def init(onnx_model_name):

    global onnx_session
    global dictonary
    global contractions
    
    try:
        words_list_url = ('https://quickstartsws9073123377.blob.core.windows.net/'
                          'azureml-blobstore-0d1c4218-a5f9-418b-bf55-902b65277b85/glove50d/wordsList.npy')
        word_vectors_dir = './word_vectors'
        os.makedirs(word_vectors_dir, exist_ok=True)
        urllib.request.urlretrieve(words_list_url, os.path.join(word_vectors_dir, 'wordsList.npy'))
        dictonary = np.load(os.path.join(word_vectors_dir, 'wordsList.npy'))
        dictonary = dictonary.tolist()
        dictonary = [word.decode('UTF-8') for word in dictonary]
        print('Loaded the dictonary! Dictonary size: ', len(dictonary))
        
        contractions_url = ('https://quickstartsws9073123377.blob.core.windows.net/'
                            'azureml-blobstore-0d1c4218-a5f9-418b-bf55-902b65277b85/glove50d/contractions.xlsx')
        contractions_df = pd.read_excel(contractions_url)
        contractions = dict(zip(contractions_df.original, contractions_df.expanded))
        print('Loaded contractions!')
        
        # Retrieve the path to the model file using the model name
        onnx_model_path = Model.get_model_path(onnx_model_name, version=None, _workspace=ws)
        print('onnx_model_path: ', onnx_model_path)
        
        onnx_session = onnxruntime.InferenceSession(onnx_model_path)
        print('Onnx Inference Session Created!')
        
    except Exception as e:
        print(e)

def remove_special_characters(token):
    pattern = re.compile('[{}]'.format(re.escape(string.punctuation)))
    filtered_token = pattern.sub('', token)
    return filtered_token

def convert_to_indices(corpus, dictonary, c_map, unk_word_index = 399999):
    sequences = []
    for i in range(len(corpus)):
        tokens = corpus[i].split()
        sequence = []
        for word in tokens:
            word = word.lower()
            if word in c_map:
                resolved_words = c_map[word].split()
                for resolved_word in resolved_words:
                    try:
                        word_index = dictonary.index(resolved_word)
                        sequence.append(word_index)
                    except ValueError:
                        sequence.append(unk_word_index) #Vector for unkown words
            else:
                try:
                    clean_word = remove_special_characters(word)
                    if len(clean_word) > 0:
                        word_index = dictonary.index(clean_word)
                        sequence.append(word_index)
                except ValueError:
                    sequence.append(unk_word_index) #Vector for unkown words
        sequences.append(sequence)
    return sequences

def score(raw_data):
    # Get predictions and explanations for each data point

    try:
        print("Received input: ", raw_data)
        
        maxSeqLength = 125
        
        print('Processing input...')
        input_data_raw = [raw_data]
        # input_data_raw = np.array(json.loads(raw_data))
        input_data_indices = convert_to_indices(input_data_raw, dictonary, contractions)
        input_data_padded = pad_sequences(input_data_indices, maxlen=maxSeqLength, padding='pre', truncating='post')
        # convert the data type to float
        input_data = np.reshape(input_data_padded.astype(np.float32), (1,maxSeqLength))
        print('Done processing input.')
        
        # Run an ONNX session to classify the input.
        result = onnx_session.run(None, {onnx_session.get_inputs()[0].name: input_data})[0].argmax(axis=1).item()
        # return just the classification index (0 or 1)
        return {'results': result}
    except Exception as e:
        print(e)
        error = str(e)
        return error


# ### API

# In[ ]:


app = Flask(__name__)
api = Api(app)


# In[ ]:


parser = reqparse.RequestParser()
parser.add_argument('data', location='json')
parser.add_argument('model_name', required=True)


# In[ ]:


class Score(Resource):
    def get(self):
        data = 'TEST_MESSAGE'
        return {'data': data}, 200  # return data and 200 OK code
    
    def post(self):
        args = parser.parse_args()
        data = args['data']
        model_name = args['model_name']
        init(model_name)
        results = score(data)
        return results, 200  # return data with 200 OK


# In[ ]:


class HealthCheck(Resource):
    def get(self):
        details = json.dumps(ws.get_details())
        return {'HealthStatus':'Okay', 'WorkspaceDetails': details}, 200


# In[ ]:


api.add_resource(Score, '/score')
api.add_resource(HealthCheck, '/healthcheck')


# In[ ]:


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


# In[ ]:




