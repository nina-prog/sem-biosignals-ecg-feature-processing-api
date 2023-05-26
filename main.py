"""Final RestAPI File"""
from fastapi import FastAPI, File, UploadFile
from datetime import datetime, date
from pydantic import BaseModel, Field, root_validator, validator
import pandas as pd
from uuid import UUID, uuid4

from tqdm import tqdm
import neurokit2 as nk

import src.feature_extraction as fe
import src.preprocessing as pp
import src.configs as cfg


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
        Set default for list parameter "label" if list has empty values.
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
        Validates that given lists have the same length.
        :param values: The input values that have already been validated.
        :type values: dict[str, Any]
        :return: The validated input values.
        :rtype: dict[str, Any]
        :raises ValueError: If any of the input lists have different lengths.
        """
        timestamp_idx, ecg = values.get("timestamp_idx", []), values.get("ecg", [])
        lengths = set(len(lst) for lst in [timestamp_idx, ecg])
        print(lengths)
        if len(lengths) != 1:
            raise ValueError('Given timestamp and ecg list must have the same length!')
        return values


class ECGConfig(BaseModel):
    """ Model of the configuration of an experiment with ECG biosignals. """
    device_name: str = Field(example="bioplux", default=None)
    frequency: int = Field(..., example=1000)
    signal: cfg.SignalEnum = Field(example=cfg.SignalEnum.chest, default=None)
    window_slicing_method: cfg.WindowSlicingMethodEnum = Field(example=cfg.WindowSlicingMethodEnum.time_related,
                                                               default=cfg.WindowSlicingMethodEnum.time_related)
    window_size: float = Field(example=1.0, default=5.0)

    class Config:
        schema_extra = {
            "example": {
                "device_name": "bioplux",
                "frequency": 1000,
                "signal": cfg.SignalEnum.chest,
                "window_slicing_method": cfg.WindowSlicingMethodEnum.time_related,
                "window_size": 5.0
            }
        }


class ECGBatch(BaseModel):
    """ Input Modle for Data Validation. The Input being the results of an experiment with ECG biosignals,
    including a batch of ecg data of different subjects. """
    supervisor: str = Field(..., example="Lieschen Mueller")
    # pydantic will process either an int or float (unix timestamp) (e.g. 1496498400),
    # an int or float as a string (assumed as Unix timestamp), or
    # o string representing the date (e.g. "YYYY-MM-DD")
    record_date: date = Field(example="2034-01-16", default_factory=date.today())
    configs: ECGConfig = Field(..., example=ECGConfig())
    samples: list[ECGSample] = Field(..., min_items=2, example=[ECGSample(), ECGSample()])

    class Config:
        schema_extra = {
            "example": {
                "supervisor": "Lieschen Mueller",
                "record_date": "2034-01-16",
                "configs": {
                    "device_name": "bioplux",
                    "frequency": 1000,
                    "signal": cfg.SignalEnum.chest,
                    "window_slicing_method": cfg.WindowSlicingMethodEnum.time_related,
                    "window_size": 5.0
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
@app.post("/process_ecg_features", status_code=200)
def process_features(data: ECGBatch):
    """
    Run feature processing.

    :param data: The input data.
    :type data: ECGBatch (JSON)

    :return: The features processed by the given input data.
    :rtype: ECGFeatures (JSON)
    """
    # to dict from json
    ecg_batch = data.__dict__
    # get configs
    configs = ecg_batch['configs']
    # get window size
    window_size = configs['window_size']
    # get window slicing method
    window_slicing_method = configs['window_slicing_method']

    features_df = pd.DataFrame()
    # iterate over samples of ecg batch
    for sample in tqdm(ecg_batch['samples']):
        # convert to pandas
        sample_df = pd.json_normalize(sample).explode(['timestamp_idx', 'ecg', 'label'])
        # preprocess ecg
        sample_df['ecg'] = nk.ecg_clean(sample_df['ecg'], sampling_rate=configs['frequency'], method="pantompkins1985")
        # slice in windows (window_size and window_slicing_method)
        windows = fe.create_windows(sample_df, 'timestamp_idx', window_size, window_slicing_method)
        print(f'Number of windows: {len(list(windows))}')
        # compute ecg features vor each window https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8203359/
        for i, window in enumerate(windows):
            # compute features
            features = fe.hrv_features(window['ecg'].values, configs['frequency'])
            # Create a DataFrame for the features
            tmp = pd.DataFrame(features, index=[0])
            # Add additional columns
            tmp['sample_id'] = sample['sample_id'].unique()
            tmp['subject_id'] = sample['subject_id'].unique()
            tmp['window_id'] = i
            tmp['w_start_time'] = window['timestamp_idx'].min()
            tmp['W_end_time'] = window['timestamp_idx'].max()
            # add new window features to df of all
            features_df = pd.concat([features_df, tmp], axis=0)

    features_df.reset_index(drop=True, inplace=True)

    return features_df.to_json(orient='records')
