# diploma
Final work of the Skillbox ML module 1
------------------------------------------------------------------------------------------------------------------------------------------
The project is an analysis of data of SbrAvtoPodpiska service.

## Implementation Stages
* Source Data exploration, understanding and preparation.
* Creation of an ML model that predicts a target action (ad click) with ROC-AUC ~ 0.69
* Creating an API service that provides the result of the modeling.

## How to run
"ga_hits-002.csv" and "ga_sessions.csv" need to be copied in /data/ folder for running .ipnb scripts

Use requirements.txt to install all required packages

To run the API, use uvicorn:
* uvicorn main:app --reload

## Project files description:
* preproc2.ipnb - data preparation for modeling
* modeling4.ipnb - modeling
* main.py - script for running local API server (FastAPI)
* customclasses.py - classes for API data models
* geo_request.py - scrypt, that gets a place geo coordinates. It uses external API opentripmap.com. You need an API key for this to work
* make_prediction.py - functions to prepare data and make a prediction
* test_api.py - test scrypt to send a request to the local API
