import os
import joblib
import pandas as pd
from fastapi import FastAPI
from customclasses import Form, AnswerForm
from make_prediction import make_prediction


app = FastAPI()


@app.post('/predict', response_model=AnswerForm)
def predict(form: Form):

    df = pd.DataFrame.from_dict([form.dict()])
    y = make_prediction(df)

    return {
        'client_id': form.dict()['client_id'],
        'predicted_action': y[0]
    }


@app.get('/version')
def version():
    # choose the latest version of a model
    model_file_name = max([file for file in os.listdir('model') if file.endswith('.pkl')])
    model = joblib.load(f'model/{model_file_name}')
    return f"{model['classifier']} version {model['version']} by {model['author']}. ROC-AUC={model['roc_auc_test']}"


@app.get('/status')
def status():
    return "I'm OK"


def main():
    pass
