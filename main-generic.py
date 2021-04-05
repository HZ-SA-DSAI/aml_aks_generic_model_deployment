#!/usr/bin/env python
# coding: utf-8
# %%
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

# %%

# ### Model Scoring

# %%


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


# %%


# Use Service Principal
from azureml.core.authentication import ServicePrincipalAuthentication

sp = ServicePrincipalAuthentication(tenant_id=os.environ['TENANT_ID'], # tenantID
                                    service_principal_id=os.environ['CLIENT_ID'], # clientId
                                    service_principal_password=os.environ['CLIENT_SECRET']) # clientSecret

ws = Workspace.get(name=os.environ['WORKSPACE_NAME'],
                   auth=sp,
                   subscription_id=os.environ['SUBSCRIPTION_ID'],
                  resource_group=os.environ['RESOURCE_GROUP'])


# %%


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

# %%


from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd
app = Flask(__name__)
api = Api(app)


# %%


parser = reqparse.RequestParser()
parser.add_argument('data', location='json')
parser.add_argument('model_name', required=True)


# %%


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


# %%


class HealthCheck(Resource):
    def get(self):
        details = json.dumps(ws.get_details())
        return {'HealthStatus':'Okay', 'WorkspaceDetails': details}, 200


# %%


api.add_resource(Score, '/score')
api.add_resource(HealthCheck, '/healthcheck')


# %%


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


# %%




