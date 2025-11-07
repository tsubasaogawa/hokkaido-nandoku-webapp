# Quickstart: Hokkaido Nandoku Quiz

This guide provides instructions for setting up and running the Hokkaido Nandoku Quiz application.

## Prerequisites

- Python 3.13+
- astral/uv
- An environment variable `NANDOKU_API_ENDPOINT` set to the URL of the backend API.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/tsubasaogawa/hokkaido-nandoku-webapp.git
    cd hokkaido-nandoku-webapp
    ```

2.  **Set the environment variable:**
    ```bash
    export NANDOKU_API_ENDPOINT="<your_api_endpoint_url>"
    ```

## Running the Application

The application is designed to be deployed as an AWS Lambda function with a Function URL. Refer to the AWS documentation for instructions on deploying the function.
