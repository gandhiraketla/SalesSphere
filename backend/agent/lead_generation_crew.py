import sys
import os
import json
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
from crewai import Agent, Task, Crew,LLM,Process
from tools.company_intelligence_tool import CompanyIntelligenceTool
from tools.market_research_tool import MarketResearchTool
class ResearchCrew:
    def __init__(self):
        #self.task_callback = task_callback
        
        # Initialize LLM
        self.llm = LLM(
            model="gpt-4",
            temperature=0.8,
            max_tokens=5000
        )
        
        # Initialize everything
        self._initialize_agents()
        self._initialize_tasks()

    def _on_task_complete(self, task_output) -> None:
        """Task completion callback handling both string outputs and task objects"""
        if self.task_callback:
            if isinstance(task_output, str):
                # If it's a direct string output
                self.task_callback("Task completed with output")
            else:
                # If it's a task object
                agent_name = getattr(task_output, 'agent', None)
                print(f"Agent name: {agent_name}")
                if agent_name and hasattr(agent_name, 'role'):
                    self.task_callback(f"{agent_name.role} has completed their task")
                else:
                    self.task_callback(f"{agent_name} has completed their task")

    def _initialize_agents(self) -> None:
        """Initialize all agents"""
        # Supervisor Agent
        self.supervisor_agent = Agent(
            role="Research Supervisor",
            goal="Coordinate and oversee the research and outreach process",
            backstory=(
                "You are a seasoned project manager with expertise in coordinating "
                "complex research and outreach campaigns. You ensure all team members "
                "work efficiently and maintain high quality standards."
            ),
            llm=self.llm,
            allow_delegation=True,
            verbose=True
        )

        # Company Research Agent
        self.company_research_agent = Agent(
            role="Company Research Specialist",
            goal="Conduct comprehensive research on target companies",
            backstory=(
                "You are an expert business analyst with a keen eye for detail "
                "and a deep understanding of various industries. Your specialty "
                "lies in gathering and analyzing company information from multiple "
                "sources to provide actionable insights."
            ),
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            tools=[CompanyIntelligenceTool()]
        )

        # Market Research Agent
        self.market_trends_agent = Agent(
            role="Market Trends Analyst",
            goal="Analyze current market trends and opportunities",
            backstory=(
                "You are an experienced market research analyst with deep knowledge "
                "of industry trends and market dynamics. Your expertise lies in "
                "identifying emerging patterns and market opportunities."
            ),
            llm=self.llm,
            allow_delegation=False,
            verbose=True,
            tools=[MarketResearchTool()]
        )

        # Outreach Agent
        self.outreach_agent = Agent(
            role="Outreach Specialist",
            goal="Create compelling, personalized outreach emails",
            backstory=(
                "You are a skilled B2B communication expert who excels at crafting "
                "personalized, engaging outreach messages. You combine company research "
                "and market insights to create compelling value propositions."
            ),
            llm=self.llm,
            allow_delegation=False,
            verbose=True
        )

    def _initialize_tasks(self) -> None:
        """Initialize all tasks"""
        # Company Research Task
        self.company_research_task = Task(
            description=(
                "Research companies by following these steps:\n\n"
                "Step 1 - Initial Search:\n"
                "Use Company Intelligence Search tool with these exact parameters:\n"
                "industry: {industry}\n"
                "company_stage: {company_stage}\n"
                "geography: {geography}\n"
                "funding_stage: {funding_stage}\n\n"
                "Step 2 - For ONLY the companies returned by the tool, analyze:\n"
                "1. Business model and market fit\n"
                "2. Growth potential and market opportunity\n"
                "3. Team composition and experience\n"
                "4. Financial health and funding history\n"
                "5. Competitive advantages and unique value propositions\n\n"
                "Important Rules:\n"
                "- Only analyze companies that were returned in tool results\n"
                "- Do not search for additional companies\n"
                "- Use competitor information if direct data unavailable\n"
                "- Do not make assumptions about missing data"
            ),
            expected_output=(
                "For each company found by the tool:\n"
                "- Company Name\n"
                "- Website\n"
                "- Headquarters\n"
                "- Funding Status\n"
                "- Business Overview\n"
                "- Growth Analysis\n"
                "- Team Info\n"
                "- Financial Status\n"
                "- Competitive Position\n\n"
                "Note: Only include companies that were returned by the initial tool search"
            ),
            agent=self.company_research_agent
        )

        # Market Research Task
        self.market_trends_task = Task(
            description=(
                "Step 1: Get market research using tool:\n"
                "Use Market Research Intelligence tool with:\n"
                "industry: {industry}\n"
                "product: {product}\n\n"
                "Step 2: For each company from company research results:\n"
                "1. Look at their specific business model and focus:\n"
                "   - What they do\n"
                "   - Their target market\n"
                "   - Current capabilities\n\n"
                "2. Connect relevant market insights:\n"
                "   - Which market trends directly affect their business\n"
                "   - Which opportunities match their capabilities\n"
                "   - Which challenges specifically impact them\n"
                "   - How future market changes will affect them\n\n"
                "Create a company-specific analysis connecting market insights to each business.\n"
                "Use only the tool output and connect it to each company."
            ),
            expected_output=(
                "A JSON array with market insights for each company:\n"
                "[\n"
                "    {\n"
                "        'company_name': 'From company research',\n"
                "        'business_focus': 'Company's main business area',\n"
                "        'relevant_trends': 'Market trends affecting this specific business',\n"
                "        'matched_opportunities': 'Opportunities this company can leverage',\n"
                "        'specific_challenges': 'Challenges affecting this business model',\n"
                "        'growth_potential': 'How market changes affect their future'\n"
                "    },\n"
                "    ...\n"
                "]\n"
                "Note: Focus on connecting existing market research to each company's specific situation"
            ),
            agent=self.market_trends_agent,
            context=[self.company_research_task]  # Access to company research results
   )

        # Outreach Task
        self.outreach_task = Task(
            description=(
                "Using the provided research, create personalized emails.\n"
                "Email body has to be elaborative with information from research and market trends\n"
                "Return a well structured JSON array with company name, website, headquarters, funding status, email subject and body\n"
                "Email body has to be between 50 and 125 words\n "
                "provide only JSON array no other text"
                
            ),
            expected_output=(
                "JSON array of emails, each containing:\n"
                "- Company information from research\n"
                "- Personalized subject line\n"
                "- Customized email body"
            ),
            agent=self.outreach_agent
            
        )

        # Supervisor Task is not needed as the supervisor agent will manage tasks automatically in hierarchical process
        # self.supervisor_task = Task(...

    def execute_research(self, inputs: dict) -> dict:
        """Execute the complete research and outreach process"""
        try:
            # Prepare inputs with optional product info
            research_inputs = inputs.copy()
            product = inputs.get('product', '')
            research_inputs['product_info'] = f"Product/Technology focus: {product}\n" if product else ""
            
            # Setup task dependencies
            self.market_trends_task.context = [self.company_research_task]
            self.outreach_task.context = [self.company_research_task, self.market_trends_task]
            
            # Create the crew with hierarchical process
            research_crew = Crew(
                agents=[
                    self.company_research_agent,
                    self.market_trends_agent,
                    self.outreach_agent
                ],
                tasks=[
                    self.company_research_task,
                    self.market_trends_task,
                    self.outreach_task
                ],
                  # Set supervisor as manager
                verbose=True,
                process=Process.sequential,
                memory=False
            )

            # Execute the process
            print("Starting research process...")
            results = research_crew.kickoff(inputs=research_inputs)
            #print(f"Raw Output: {results.raw}")
            #if results.json_dict:
                 #print(f"JSON Output: {json.dumps(results.json_dict, indent=2)}")
            #if results.pydantic:
             #   print(f"Pydantic Output: {results.pydantic}")
            #print(f"Tasks Output: {results.tasks_output}")
            #print(f"Token Usage: {results.token_usage}")
            #print("Raw results from kickoff:", results)
            #print("Type of results:", type(results))
            #print("Attributes of results:", dir(results))
            #print("Results Type:", type(results))
            #print("Results Dir:", dir(results))
            #json_results = json.loads(str(results))
            #tasks_output = results.get('tasks_output', [])
            
            print("Returning Results")
            return results.raw

        except Exception as e:
            print(f"An error occurred during research: {str(e)}")
            raise

# Example usage for local testing
def example_task_callback(message):
    print(f"\n{message}")

def main():
    """Main function to test the research functionality"""
    crew = ResearchCrew()

    # Test inputs
    test_inputs = {
        "industry": "retail",
        "company_stage": "startup",
        "geography": "California",
        "funding_stage": "",
        "product": "AI in customer analytics"  # Optional
    }

    try:
        results = crew.execute_research(test_inputs)
        print(results)

    except Exception as e:
        print(f"Main execution error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
