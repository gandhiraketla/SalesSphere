import os
import ast
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from utils.envutils import EnvUtils

class MarketResearchService:
    def __init__(self):
        # Load environment variables
        self.env_utils = EnvUtils()
        self.api_key = self.env_utils.get_required_env('PERPLEXITY_API_KEY')
        self.model = self.env_utils.get_required_env('PERPLEXITY_MODEL_NAME')
        if not self.api_key:
            raise ValueError("Please set the PERPLEXITY_API_KEY environment variable")

        # Perplexity API Key
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')

    def generate_market_research(
        self, 
        industry: Optional[str] = None, 
        product: Optional[str] = None
    ) -> str:
        """
        Generate comprehensive market research insights using Perplexity AI.
        
        :param industry: Target industry
        :param product: Specific product or technology
        :return: Comprehensive market research insights as a string
        """
        # Construct search query
        search_query = self._build_search_query(industry, product)
        
        # Generate insights
        insights = self._generate_perplexity_insights(search_query)
        
        return insights

    def _build_search_query(self, industry: Optional[str], product: Optional[str]) -> str:
        """
        Construct a search query from industry and product.
        
        :param industry: Optional target industry
        :param product: Optional product or technology
        :return: Constructed search query
        """
        query_parts = []
        
        if product:
            query_parts.append(product)
        
        if industry:
            query_parts.append(industry)
        
        return " ".join(query_parts) if query_parts else "technology innovation"

    def _generate_perplexity_insights(self, query: str) -> str:
        """
        Generate market research insights using Perplexity AI.
        
        :param query: Search query
        :return: Comprehensive market research insights as a string
        """
        # Validate API key
        if not self.perplexity_api_key:
            return "Perplexity API key is missing. Unable to generate insights."

        # Perplexity API endpoint
        url = "https://api.perplexity.ai/chat/completions"

        # Construct detailed prompt for comprehensive insights
        prompt = f"""You are a top-tier market research analyst conducting an in-depth strategic analysis on {query}. 

Provide a comprehensive market research report that includes:

1. Market Landscape Analysis:
- Current market dynamics
- Emerging trends and innovations
- Key players and competitive ecosystem

2. Strategic Opportunities:
- Potential business opportunities
- Innovative application areas
- Untapped market segments

3. Technology and Innovation Insights:
- Cutting-edge technological developments
- Potential disruptive technologies
- Future technology trajectories

4. Business Strategy Recommendations:
- Strategic entry points
- Investment considerations
- Innovation and development strategies

5. Potential Challenges and Mitigation:
- Market barriers
- Potential risks
- Strategies for overcoming challenges

Ensure the analysis is:
- Forward-looking and predictive
- Backed by current market intelligence
- Actionable for strategic decision-makers

Provide specific, data-driven insights with a clear, structured approach that offers both macro and micro-level perspectives.
"""

        # Payload for Perplexity API
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert market research analyst providing strategic, forward-looking business insights."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
        }

        # API request headers
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }

        try:
            # Make API call
            response = requests.post(url, json=payload, headers=headers)
            response_data = response.json()
            
            # Extract and return insights
            insights = response_data.get('choices', [{}])[0].get('message', {}).get('content', 
                "Unable to generate insights. Please try again.")
            
            return insights
        
        except Exception as e:
            print(f"Error generating insights: {e}")
            return f"An error occurred while generating insights: {str(e)}"

def generate_market_research(
    industry: Optional[str] = None, 
    product: Optional[str] = None
) -> str:
    """
    Generate comprehensive market research insights.
    
    :param industry: Optional target industry
    :param product: Optional product or technology
    :return: Comprehensive market research insights as a string
    """
    # Initialize research tool
    research_tool = MarketResearchService()
    
    # Generate market insights
    return research_tool.generate_market_research(industry, product)

def main():
    # Get user input
    industry = input("Enter the target industry (optional): ").strip() or None
    product = input("Enter the specific product/technology (optional): ").strip() or None
    
    # Generate market research
    try:
        market_insights = generate_market_research(industry, product)
        
        # Print comprehensive insights
        print("\n--- Comprehensive Market Insights ---")
        print(market_insights)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

