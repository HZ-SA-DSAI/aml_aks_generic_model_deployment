#!/usr/bin/env python
# coding: utf-8

# ### Model Scoring

# In[ ]:


import json
import numpy as np
import pandas as pd
import os
import pickle
import joblib
import os
from sklearn.linear_model import LogisticRegression
from azureml.core.workspace import Workspace
from azureml.core.model import Model


# In[ ]:


# Use Service Principal
from azureml.core.authentication import ServicePrincipalAuthentication

sp = ServicePrincipalAuthentication(tenant_id=os.environ['TENANT_ID'], # tenantID
                                    service_principal_id=os.environ['CLIENT_ID'], # clientId
                                    service_principal_password=os.environ['CLIENT_SECRET']) # clientSecret

ws = Workspace.get(name=os.environ['WORKSPACE_NAME'],
                   auth=sp,
                   subscription_id=os.environ['SUBSCRIPTION_ID'],
                  resource_group=os.environ['RESOURCE_GROUP'])


# In[ ]:


def score(raw_data, model_name):
    # Get predictions and explanations for each data point
    data = pd.read_json(raw_data)
    
    model_path = Model.get_model_path(model_name, version=None, _workspace=ws)

    model = joblib.load(model_path)

    # Make prediction
    predictions = model.predict(data)

    # You can return any data type as long as it is JSON-serializable
    return {'results': predictions.tolist()}


# ### API

# In[ ]:


from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
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
        results = score(data, model_name)
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
    app.run(host='0.0.0.0', port=80)


# In[ ]:




