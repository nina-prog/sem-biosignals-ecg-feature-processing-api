# get the Fast API image with Python version 3.7
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

# greate the directory for the container
WORKDIR /app
COPY ../requirements.txt ./requirements.txt

# install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app.py ./

# copy the serialized model
COPY ./models/example.pkl ./models/example.pkl

# run by specifying the host and port
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]