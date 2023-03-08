"""Final RestAPI File"""
from fastapi import FastAPI, File, UploadFile
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Union
import pandas as pd

# load model
...

# pydantic models
class ModelItem(BaseModel):
    id: int
    date: list[int]
    time_index: list[int] # oder timestamps: list[str] # oder gar nicht notwendig
    ecg: list[float]
    bvp: list[float]

class Model(BaseModel):
    __root__: Union[list[ModelItem], ModelItem]

class ResponseModel(BaseModel):
    label: str
    prediction: int

# initialize an instance of FastAPI
app = FastAPI()

# default route
@app.get("/")
def root():
    """

    :return:
    :rtype:
    """
    return {"message": "Welcome to ECG Classification FastAPI"}

@app.post("/predict_features", response_model=ResponseModel, status_code=200)
def predict_features(data: ModelItem):
    # to pandas / numoy
    #data_df = pd.json_normalize(data.__dict__)
    #data_df = pd.DataFrame(data.dict()).explode(['ecg', 'bvp'])
    # clean data
    # extract fetaures
    # predict
    return response_model


@app.post("/csv/predict_features")
def csv_predict_features(file: UploadFile = File(...)):
    """

    :param file:
    :type file:
    :return:
    :rtype:
    """
    df = pd.read_csv(file.file)
    file.file.close()
    return {"filename": file.filename}
