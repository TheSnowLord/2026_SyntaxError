
# 🧠 Planner AI Agent


An autonomous AI planning agent.

## Features

- Understands user goals
- Generates structured plans
- Prioritizes tasks
- Executes actions
- Returns JSON results


## Architecture


User
 |
Frontend Website
 |
FastAPI Backend
 |
Planner AI Model
 |
JSON Response


## API

POST:

/plan


Example Request:

{
 "request":"Create a study plan for exams"
}


Example Response:

{
 "goal":"Study for exams",
 "tasks":[]
}


## Installation

Install requirements:

pip install -r requirements.txt


## Run Backend

uvicorn main:app --reload


## Built With

- Python
- FastAPI
- PyTorch
- Transformers
- HuggingFace

