![](https://img.shields.io/github/license/FallenDeity/ApiProjects?style=flat-square)
![](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)
![](https://img.shields.io/badge/%20type_checker-mypy-%231674b1?style=flat-square)
![](https://img.shields.io/github/stars/FallenDeity/ApiProjects?style=flat-square)
![](https://img.shields.io/github/last-commit/FallenDeity/ApiProjects?style=flat-square)

# AgroIndia

AgroIndia is a web application that provides a platform for farmers to get the latest information about the market prices of their produce and also the latest information about the weather conditions.
It also provides a platform for buyers to get the latest information about the market prices of the produce they want to buy and also updates farmers with market prices of their produce in their locality.

AgroIndia is an RESTful API built on fastapi framework.
AgroIndia is built keeping in mind concurrency and asynchronous programming. Meaning, it can handle multiple requests at the same time without blocking any of them.
It uses PostgreSQL as the database hosted on heroku along with the API.
The API wraps various third party APIs to provide the required information to the users along with custom datasets from `data.gov.in`.
The API is custom built to provide Indian farmers with whatever information they need to make their farming more efficient and profitable.
In addition to that, their are plans to add more features to the API in the future such as to facilitate the farmers to sell their produce directly to the buyers eliminating the middlemen.

## Features

- Get the latest market prices of the produce in your locality.
- Get the latest weather conditions in your locality from nearest weather station.
- Get the latest market prices of the produce you want to buy.
- Get the latest market prices of the produce you want to sell.
- Registeration and login for farmers and buyers.
- Taxological data of various plants.
- Biological data of various plants.
- Identify plants using image recognition.
- Diagnostic data of various diseases of plants using image recognition.
- Get seasonal production data of various crops.

## Codebase

The codebase is divided into two main parts:
- `api` - The RESTful API built on fastapi framework.
- `data` - The data used by the API.

### API

1. The API Endpoints are distributed into various modules based on the functionality they provide.
2. Each module has its own `router` which is then imported into the `session.py` and then the `app` is run using uvicorn.
3. Each module has its own `models` and `schemas` which are used to define the database models and the schemas for the API endpoints.
4. The `utils` folder contains the various functions used by the API such as the return schemas and the database models.
5. Each module has a `logger` attribute which is used to log the various events that occur in the API using a custom logger module `logger.py`.
6. `aiohttp` is used to make asynchronous requests to the third party APIs to maintain concurrency.
7. Finally the API has a few event handlers which are used to handle the various events that occur in the API such as startup and shutdown events.

### Data

1. `asyncpg` is used to create a database pool connecting to the database hosted on heroku.
2. SQL scripts are used to create the database tables and populate them with the data on setup of the API. The scripts are located in the `bin` folder.
3. The data is stored in the `assets` folder in the form of csv files.
4. `models.py` contains various custom models used by the API to return the data in the required format.
5. Models are made of dataclasses which are then serialized and returned as JSON responses by fastapi in background.
6. The `database` class is then imported into the `session.py` and a connection is maintained throughout the API runtime.
