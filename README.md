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
