from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

app = FastAPI(title="AgentForge AI Backend")

# Enable CORS for Frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace YOUR_GEMINI_API_KEY with your actual key from Google AI Studio
client = genai.Client(api_key="AQ.Ab8RN6JbvaJL-zOb1ASao0fuBXq5o_Eb6A8ng2kjcHudk07gog")

class GoalRequest(BaseModel):
    goal: str

@app.get("/")
def read_root():
    return {"status": "AgentForge AI Backend Live"}

@app.post("/solve")
async def solve_goal(request: GoalRequest):
    try:
        prompt = f"You are AgentForge AI. Provide a detailed, step-by-step solution for this goal: {request.goal}"
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        return {"result": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))