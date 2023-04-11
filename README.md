# sem-biosignals-ecg-feature-processing-api
(Fast)API Pipeline for the processing of heart rate data from raw ECG signals towards HRV features.

# Repo Structure


# Pipeline Description
Short Overview:
* Input (plus device): *...TBD...*
* Output: *...TBD...*
* Input data form: JSON implementing ECGBatch (see below)
* Output data form: *...TBD...*

## Input Data Form 
Examples for the Input are implemented in the code and can be seen when running the api via the /docs user interface. 
However here is an overview of the Input model and its attributes, including their type, constraints and description.

This code defines two Pydantic input models, ECGSample and ECGBatch, for validating and processing data related to 
electrocardiogram (ECG) biosignals. 

**ECGBatch** is a model for representing a batch of ECG data from multiple subjects in an experiment. It has the 
following attributes:

| **ECGBatch**  | ****            | ****         | ****            | ****                                                                                                  |
|---------------|-----------------|--------------|-----------------|-------------------------------------------------------------------------------------------------------|
| **Parameter** | **Type**        | **Optional** | **Constraints** | **Description**                                                                                       |
| supervisor    | str             | False        | N/A             | Name of the supervisor who conducted the experiment.                                                  |
| record_date   | date            | False        | N/A             | Date on which the ECG data was recorded. If not provided, the current date is set as the default.     |
| samples       | list[ECGSample] | False        | N/A             | A list of ECGSample objects representing the results of the experiment for all subjects.              |
| configs       | dict or None    | True         | N/A             | A dictionary containing the configuration settings used during the experiment. Default value is None. |

**ECGSample** is a model for representing the results of a single subject in an ECG experiment. It has the following 
attributes:

| **ECGSample**     | ****                        | ****         | ****            | ****                                                                                                                                                                                                  |
|-------------------|-----------------------------|--------------|-----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Parameter**     | **Type**                    | **Optional** | **Constraints** | **Description**                                                                                                                                                                                       |
| sample_id         | UUID or None                | True         | N/A             | Unique ID of the sample. If not provided, a UUID is generated using uuid4.                                                                                                                            |
| subject_id        | str                         | False        | N/A             | ID of the subject for whom the ECG data was collected.                                                                                                                                                |
| timestamp_idx     | list[datetime]              | False        | min_items=2     | A list of timestamps at which the ECG data was recorded.                                                                                                                                              |
| ecg               | list[float]                 | False        | min_items=2     | A list of ECG signal data values recorded at each timestamp.                                                                                                                                          |
| label             | list[str] or None           | True         | min_items=2     | A list of labels corresponding to each timestamp in the timestamp_idx list. If not provided, a default list with the same length as timestamp_idx and ecg is generated with "undefined" as its value. |
|                   |                             |              |                 |                                                                                                                                                                                                       |
| Config            | Class configuration options | False        | N/A             | Additional options for the class configuration, such as defining an example value for the model.                                                                                                      |
| set_label_default | Validator function          | N/A          | N/A             | A function that sets a default value for the label list parameter.                                                                                                                                    |
| check_length      | Validator function          | N/A          | N/A             | A function that checks that all list parameters have the same length.                                                                                                                                 |

The models use Pydantic's validation features, such as Field and validator, to ensure that the input data meets certain 
requirements, such as the length of the timestamp_idx, ecg, and label lists being the same. The Config class in each 
model then includes an example which can be seen in the code and also in the interface as mentioned above. Pydantic 
also enables someone to use this example as default input to test the routes, so no effort is to be taken defining a 
new example.

## Output Data Form

# Requirenments
...see requirenments.txt

# Setup
Setup via Dockerfile (suggested):
1. Install Docker[sdfs]
2. Build Docker Image: Via Software Interface or via Command Line 
   * Software Interface:
   * *...TBD (.gif)...*
   * Command Line: 
   * ````sudo docker build . diarization````
3. Start Docker Container: Via Software Interface or vie Command Line
   * Software Interface:
   * *...TBD (.gif)...*
   * Command Line:
     * In foreground: ````sudo docker run -p8000:8000 diarization:latest````
     * Or in forebackground: ````sudo docker run -d -p8000:8000 diarization:latest````
4. Check FastAPI Docs ...../docs or .../...

Otherwise:
1. Create a virtual environment (python 3.10)
2. Install requirements from requirements.txt with pip install -r requirements.txt

# Outlook
* Add parameter "feature_selection" (str or list[EnumFeatures], default=all) to input class ECGBatch: select features 
which shuold be computed. *Example: list: [feature_x, feature_y, feature_z]; str: "HRV" -> computes defined "basic" HRV Features,
"default" -> computes all features, "time-domain" -> computes only time domain features*
* Add new route "preprocess_ecg_data" to main.py: only execute preprocessing part of the application and do not compute the features.