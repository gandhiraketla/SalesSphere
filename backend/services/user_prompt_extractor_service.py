import json
import requests
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from utils.envutils import EnvUtils

class UserPromptExtractor:
    def __init__(self):
        """
        Initialize the Lead Extractor with Perplexity API
        """
        # Use EnvUtils to load environment and get API key
        self.env_utils = EnvUtils()
        self.api_key = self.env_utils.get_required_env('PERPLEXITY_API_KEY')
        self.model = self.env_utils.get_required_env('PERPLEXITY_MODEL_NAME')
    def extract_lead_info(self, prompt):
        """
        Extract lead information from a given prompt using Perplexity API
        
        Args:
            prompt (str): Input prompt to extract information from
        
        Returns:
            dict: Extracted lead information
        """
        url = "https://api.perplexity.ai/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        extraction_prompt = f"""
        Extract structured information from the following prompt into a JSON format. 
        The JSON should have these exact keys: "industry", "company_stage", "geography", "funding_stage", "product".
        If any information is not available, leave the value as an empty string.
        
        Prompt: {prompt}
        
        Output ONLY the valid JSON, nothing else.
        Example output format:
        {{
            "industry": "technology",
            "company_stage": "startup",
            "geography": "California",
            "funding_stage": "seed",
            "product": "AI customer analytics"
        }}
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert at extracting structured information from text. Always respond with ONLY a valid JSON."
                },
                {
                    "role": "user", 
                    "content": extraction_prompt
                }
            ],
            "max_tokens": 200
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            # Extract the content
            content = response.json()['choices'][0]['message']['content'].strip()
            
            # Try to parse JSON, with fallback to a default dictionary
            try:
                # Attempt to parse the content as JSON
                parsed_json = json.loads(content)
                return parsed_json
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON-like content
                import re
                
                # Look for JSON-like content between { and }
                json_match = re.search(r'\{[^}]+\}', content)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except json.JSONDecodeError:
                        pass
                
                # Fallback to default dictionary if parsing fails
                print(f"Failed to parse JSON. Raw content: {content}")
                return {
                    "industry": "",
                    "company_stage": "",
                    "geography": "",
                    "funding_stage": "",
                    "product": ""
                }
        except requests.RequestException as e:
            print(f"API call error: {e}")
            return {
                "industry": "",
                "company_stage": "",
                "geography": "",
                "funding_stage": "",
                "product": ""
            }

def main():
    # Create extractor
    extractor = UserPromptExtractor()
    
    # Test prompts
    test_prompts = [
        "Generate leads for quantum computing startups in California interested in AI-driven cryptography"
        
    ]
    
    for prompt in test_prompts:
        print(f"\nPrompt: {prompt}")
        result = extractor.extract_lead_info(prompt)
        print(result)

if __name__ == "__main__":
    main()