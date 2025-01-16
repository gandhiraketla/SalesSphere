from fastapi import FastAPI
from pydantic import BaseModel
import json
import uvicorn
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
# Assuming these are imported from existing modules
from services.user_prompt_extractor_service import UserPromptExtractor
from services.read_json_test import JSONFileReader
from agent.lead_generation_crew import ResearchCrew
import json
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time


class QueryRequest(BaseModel):
    query: str

class LeadGenerationAPI:
    def __init__(self):
        self.app = FastAPI()
        self.prompt_extractor = UserPromptExtractor()
        self.app.add_middleware(CORSMiddleware,
            allow_origins=["http://localhost:5173"],  # Frontend URL
            allow_credentials=True,
            allow_methods=["*"],  # Allows all methods
            allow_headers=["*"],  # Allows all headers
        )
        self.use_agent_json = False
        @self.app.post("/research")
        def execute_research(request: QueryRequest):
            if self.use_agent_json:
                
                # Extract structured info from user query
                extracted_json = self.prompt_extractor.extract_lead_info(request.query)
            # print(extracted_json)
                # Define callback for UI status updates
                #def example_task_callback(status: str):
                    # This can be modified to send updates to UI
                    #print(status)
                # Initialize research crew with callback
                crew = ResearchCrew()
                
                # Execute research with extracted JSON
                results = crew.execute_research(extracted_json)
                results = results.replace("```json", "").replace("```", "")
                results = results.strip()
                structured_json = json.loads(results)
                json.dumps(structured_json, indent=4) 
                return structured_json
                #response = JSONResponse(content=results)
                #print("Serialized Response Content:", response.body.decode())
                #print(structured_json)
            else:
                time.sleep(30)
                structured_json=JSONFileReader().read_json()
                return structured_json

def create_app():
    api = LeadGenerationAPI()
    return api.app

# For running the API directly
