"""Final RestAPI File"""
from fastapi import FastAPI, File, UploadFile
from datetime import datetime, date
from pydantic import BaseModel, Field, root_validator, validator
import pandas as pd
from uuid import UUID, uuid4
from enum import Enum


# pydantic models
class ECGSample(BaseModel):
    """ Model of the results of a single subject of an experiment with ECG biosignals. """
    sample_id: UUID = Field(example="f70c1033-36ae-4b8b-8b89-099a96dccca5", default_factory=uuid4)
    subject_id: str = Field(..., example="participant_1")
    # pydantic will process either an int or float (unix timestamp) (e.g. 1496498400),
    # an int or float as a string (assumed as Unix timestamp), or
    # o string representing the date (e.g. "YYYY - MM - DD[T]HH: MM[:SS[.ffffff]][Z or [±]HH[:]MM]")
    timestamp_idx: list[datetime] = Field(..., min_items=2, example=[1679709871, 1679713471, 1679720671])
    ecg: list[float] = Field(..., min_items=2, example=[1.0, -1.100878, -3.996840])
    label: list[str] = Field(min_items=2, example=["undefined", "stress", "undefined"], default=None)

    class Config:
        schema_extra = {
            "example": {
                "sample_id": "f70c1033-36ae-4b8b-8b89-099a96dccca5",
                "subject_id": "participant_1",
                "timestamp_idx": [1679709871, 1679713471, 1679720671],
                "ecg": [1.0, -1.100878, -3.996840],
                "label": ["undefined", "stress", "undefined"]
            }
        }

    @validator('label', pre=True, always=True)
    def set_label_default(cls, v, values):
        """
        Set default for list parameter "label" if not already given.
        :param v: The input value of the field being validated.
        :type v: Any
        :param values: The input values that have already been validated.
        :type values: dict[str, Any]
        :return: The list with the corresponding labels.
        :rtype: list[str]
        """
        list1_len = len(values.get('timestamp_idx') or [])
        list2_len = len(values.get('ecg') or [])
        return v or ["undefined"] * max(list1_len, list2_len)

    @root_validator()
    def check_length(cls, values):
        """
        Validates that all given lists have the same length.
        :param values: The input values that have already been validated.
        :type values: dict[str, Any]
        :return: The validated input values.
        :rtype: dict[str, Any]
        :raises ValueError: If any of the input lists have different lengths.
        """
        timestamp_idx, ecg, label = values.get("timestamp_idx", []), values.get("ecg", []), values.get("label", [])
        lengths = set(len(lst) for lst in [timestamp_idx, ecg, label])
        print(lengths)
        if len(lengths) != 1:
            raise ValueError('All given lists must have the same length!')
        return values


class SignalEnum(str, Enum):
    chest = 'chest'
    wrest = 'wrest'


class ECGBatch(BaseModel):
    """ Input Modle for Data Validation. The Input being the results of an experiment with ECG biosignals,
    including a batch of ecg data of different subjects. """
    supervisor: str = Field(..., example="Lieschen Mueller")
    # pydantic will process either an int or float (unix timestamp) (e.g. 1496498400),
    # an int or float as a string (assumed as Unix timestamp), or
    # o string representing the date (e.g. "YYYY-MM-DD")
    record_date: date = Field(example="2034-01-16", default_factory=date.today())
    samples: list[ECGSample]
    configs: dict = Field(example={"device_name": "bioplux", "frequency": 400, "signal": SignalEnum.chest},
                          default=None)

    class Config:
        schema_extra = {
            "example": {
                "supervisor": "Lieschen Mueller",
                "record_date": "2034-01-16",
                "configs": {
                    "device_name": "bioplux",
                    "frequency": 400,
                    "signal": SignalEnum.chest
                },
                "samples": [
                    {
                        "sample_id": "f70c1033-36ae-4b8b-8b89-099a96dccca5",
                        "subject_id": "participant_1",
                        "timestamp_idx": [1679709871, 1679713471, 1679720671],
                        "ecg": [1.0, -1.100878, -3.996840],
                        "label": ["undefined", "stress", "undefined"]},
                    {
                        "subject_id": "participant_2",
                        "timestamp_idx": [1679709871, 1679713471, 1679720671],
                        "ecg": [1.0, -1.100878, -3.996840]}
                ]
            }
        }


class ECGFeatures(BaseModel):
    """ Response Model for Data Validation. The Response being the results of the Feature Processing of the given
    Input. """
    message: str = "test"


# initialize an instance of FastAPI
app = FastAPI()


# default route
@app.get("/")
def root():
    """
    Get Info and welcome message.
    :return: info message
    :rtype: str
    """
    return {"message": "Welcome to ECG Feature Processing FastAPI"}


# feature processing route (json)
@app.post("/process_ecg_features", response_model=ECGFeatures, status_code=200)
def process_features(data: ECGBatch):
    """
    Run feature processing.
    :param data: The input data.
    :type data: ECGBatch (JSON)
    :return: The features processed by the given input data.
    :rtype: ECGFeatures (JSON)
    """
    # to pandas / numpy
    data_df = pd.json_normalize(data.__dict__)
    data_df = pd.DataFrame(data.dict()).explode(['samples'])
    # clean data
    # extract features
    # combine data
    ecg_features = ECGFeatures()
    return ecg_features


# optional ############################################################################################################


# feature processing route (csv)
@app.post("/csv/process_ecg_features")
def csv_process_features(file: UploadFile = File(...)):
    """
    Run feature processing and return results combined in a csv.
    :param file: The input data.
    :type file: file (csv)
    :return: A file containing the features processed by using the input data.
    :rtype: file (csv)
    """
    df = pd.read_csv(file.file)
    file.file.close()
    return {"filename": file.filename}


