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

class QueryRequest(BaseModel):
    query: str

class LeadGenerationAPI:
    def __init__(self):
        self.app = FastAPI()
        self.prompt_extractor = UserPromptExtractor()
        
        @self.app.post("/research")
        def execute_research(request: QueryRequest):
            # Extract structured info from user query
            #extracted_json = self.prompt_extractor.extract_lead_info(request.query)
            #print(extracted_json)
            # Define callback for UI status updates
            #def example_task_callback(status: str):
                # This can be modified to send updates to UI
                #print(status)
            # Initialize research crew with callback
            #crew = ResearchCrew()
            
            # Execute research with extracted JSON
            #results = crew.execute_research(extracted_json)
           # structured_json = json.loads(results)
            #json.dumps(structured_json, indent=4)
            #response = JSONResponse(content=results)
            #print("Serialized Response Content:", response.body.decode())
            #print(structured_json)
            structured_json=JSONFileReader().read_json()
            return structured_json

def create_app():
    api = LeadGenerationAPI()
    return api.app

# For running the API directly
