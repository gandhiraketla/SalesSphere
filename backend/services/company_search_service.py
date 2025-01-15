from typing import Optional, Dict, List, Any
from dataclasses import dataclass
import requests
import logging
import os
import feedparser
from datetime import datetime
import json

@dataclass
class CompanyInfo:
    name: str
    industries: List[str]
    description: Optional[str]
    location: Optional[Dict]
    website: Optional[str] = None
    size: Optional[Dict] = None
    recent_news: List[Dict] = None

class CompanyService:
    def __init__(self):
        """
        Initialize the CompanyService with necessary API credentials.
        Requires API key in environment variable:
        - COMPANIES_API_KEY: for The Companies API access
        """
        self.api_key = "2Dg3nLHXP0uqQoC3Jz67ldGR2MdCsq6A"
        if not self.api_key:
            raise ValueError("Missing COMPANIES_API_KEY environment variable")
            
        self.base_url = "https://api.thecompaniesapi.com/v2"
        self.headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        self.logger = logging.getLogger(__name__)
        
    def search_companies(self, 
                        company_name: Optional[str] = None,
                        industries: Optional[List[str]] = None,
                        countries: Optional[List[str]] = None) -> List[CompanyInfo]:
        """
        Search for companies using The Companies API v2.
        
        Args:
            company_name (str, optional): Name of the company
            industries (List[str], optional): List of industries
            countries (List[str], optional): List of country codes
            
        Returns:
            List[CompanyInfo]: List of matching company information
        """
        try:
            # Start with just one simple query for testing
            query = [{
                "attribute": "about.industries",
                "operator": "or",
                "sign": "equals",
                "values": ["retail"]
            }]
            
            # Make the API request
            print(f"Query being sent: {json.dumps(query)}")  # Debug print
            
            # Try POST request instead of GET
            response = requests.post(
                f"{self.base_url}/companies",
                headers=self.headers,
                json={'query': query}  # Send as JSON body instead of query parameter
            )
            print(f"Full URL being called: {response.url}")  # Debug print
            
            results = response.json()
            print(f"API response: {results}")  # Debug print
            companies = []
            
            for result in results.get('data', []):
                print(f"Processing company: {result.get('name')}")  # Debug print
                company = CompanyInfo(
                    name=result.get('name'),
                    industries=result.get('about', {}).get('industries', []),
                    description=result.get('about', {}).get('description'),
                    location=result.get('locations', {}).get('headquarters'),
                    website=result.get('website'),
                    size=result.get('size'),
                    recent_news=[]
                )
                # Add recent news
                company.recent_news = self.get_company_news(company.name)
                companies.append(company)
            
            return companies
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error searching companies: {str(e)}")
            raise
    
    def get_company_news(self, company_name: str, max_articles: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent news articles about the company using Google News RSS.
        
        Args:
            company_name (str): Name of the company
            max_articles (int): Maximum number of articles to return
            
        Returns:
            List[Dict]: List of news articles with title, date, and URL
        """
        try:
            # Encode company name for URL
            encoded_name = requests.utils.quote(company_name)
            rss_url = f"https://news.google.com/rss/search?q={encoded_name}&hl=en-US&gl=US&ceid=US:en"
            
            # Parse RSS feed
            feed = feedparser.parse(rss_url)
            
            news_list = []
            for entry in feed.entries[:max_articles]:
                news_list.append({
                    'title': entry.title,
                    'date': datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z').strftime('%Y-%m-%d'),
                    'url': entry.link
                })
            
            return news_list
            
        except Exception as e:
            self.logger.error(f"Error fetching news: {str(e)}")
            return []


def main():
    """Main function for testing the CompanyService."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize service
        service = CompanyService()
        
        # Test simple company search
        print("\nSearching for Microsoft...")
        try:
            results = service.search_companies(
                company_name="Microsoft",
                industries=["software", "technology"],
                countries=["us"]
            )
            
            for company in results:
                print(f"\nCompany Information:")
                print(f"Name: {company.name}")
                print(f"Industries: {', '.join(company.industries)}")
                print(f"Description: {company.description}")
                if company.location:
                    print(f"Location: {company.location.get('city', '')}, {company.location.get('country', {}).get('code', '')}")
                print(f"Website: {company.website}")
                if company.size:
                    print(f"Size: {company.size.get('range', '')}")
                
                print("\nRecent News:")
                for news in company.recent_news:
                    print(f"- [{news['date']}] {news['title']}")
                    print(f"  URL: {news['url']}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
                
    except ValueError as e:
        print(f"Initialization error: {str(e)}")


if __name__ == "__main__":
    main()