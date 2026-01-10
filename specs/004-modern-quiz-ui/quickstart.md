# Quickstart: Modern Quiz UI

## Prerequisites
- Python 3.13+
- AWS Credentials (for Bedrock/DynamoDB) or mocked environment.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # OR if using just the source folder
   pip install fastapi uvicorn jinja2 python-multipart boto3 httpx mangum
   ```

## Running Locally
1. Set environment variables:
   ```bash
   export NANDOKU_API_ENDPOINT="https://api.example.com" # Replace with real API or mock
   export AWS_REGION="ap-northeast-1"
   export DYNAMODB_TABLE_NAME="hokkaido-nandoku-quiz-cache"
   ```
   *Note: If you don't have AWS access, the app might fail on startup or request unless mocked.*

2. Run the server:
   ```bash
   uvicorn src.main:app --reload
   ```

3. Open `http://localhost:8000` to view the quiz.

## Testing UI
- Resize browser window to mobile sizes (375px) to test responsiveness.
- Use browser dev tools to emulate touch events.
