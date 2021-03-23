MIT License

Copyright (c) 2021 HZ-MS-CSA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



# aml_model_aks_custom


1. conda env create -f project_env.yml

2. conda activate project_environment

3. Provide the necessary environment variables at run time

    1. TENANT_ID
    2. CLIENT_ID
    3. CLIENT_SECRET
    4. WORKSPACE_NAME
    5. SUBSCRIPTION_ID
    6. RESOURCE_GROUP

4. python main-generic.py (Start flask app)

5. Send a post query with the following requirements

    1. Body is set to json string with the following structure: {'data': RAW_DATA}
    2. headers = {'Content-Type':'application/json'}
    3. params = {'model_name': MODEL_NAME}
    

```python

```
