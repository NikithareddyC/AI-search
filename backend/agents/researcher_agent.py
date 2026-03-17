"""
Researcher Agent
Gathers information about AI/ML topics from the internet
Uses web scraping, search APIs, and knowledge bases
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
from agents.base_agent import Agent, AgentStatus
from services.llm_provider import llm_manager
from config import settings

logger = logging.getLogger(__name__)


class ResearcherAgent(Agent):
    """
    Researcher Agent
    Responsible for:
    - Researching AI/ML topics
    - Gathering data from multiple sources
    - Extracting key concepts and information
    - Creating learning summaries
    """
    
    def __init__(self):
        super().__init__(
            name="Researcher",
            role="Information Gatherer & Analyst",
            description="Researches AI/ML topics and gathers comprehensive information"
        )
        self.sources = []
        self.research_data = {}
    
    def get_available_tools(self) -> List[str]:
        return [
            "web_search",
            "google_scholar_search",
            "scrape_url",
            "fetch_rss_feeds",
            "extract_pdf",
            "analyze_github_repo",
            "fetch_huggingface_model_card"
        ]
    
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute research task with mock data (for MVP demo)
        Example: "Research RAG (Retrieval Augmented Generation)"
        """
        self.set_status(AgentStatus.THINKING, f"Starting research on: {task}")
        
        try:
            # Add task to memory
            self.add_memory("user", task)
            
            # Return mock research data for MVP demo
            self.set_status(AgentStatus.COMPLETE, "Research completed successfully")
            
            return {
                "status": "success",
                "topic": task,
                "search_queries": [
                    f"What is {task}",
                    f"{task} explained",
                    f"{task} tutorial",
                    f"{task} 2024 2025",
                    f"How to use {task}"
                ],
                "sources_found": 5,
                "research_data": {
                    "definition": f"{task} is a key concept in AI/ML that helps improve model performance and understanding.",
                    "key_concepts": [
                        "Core principles and fundamentals",
                        "Practical applications",
                        "Recent advances in 2024-2025",
                        "Integration with modern systems",
                        "Performance metrics and benchmarks"
                    ],
                    "how_it_works": f"{task} works through a systematic process that involves gathering data, processing it, and applying intelligent algorithms to derive insights.",
                    "why_it_matters": f"Understanding {task} is crucial for building effective AI systems. It improves model accuracy, efficiency, and real-world applicability."
                },
                "learning_summary": f"Master {task}: From fundamentals to production. Learn how {task} transforms AI workflows and why it's essential for modern development.",
                "sources": [
                    "https://example.com/what-is-llm",
                    "https://example.com/llm-guide",
                    "https://example.com/llm-tutorial",
                    "https://example.com/llm-2024",
                    "https://example.com/llm-production"
                ]
            }
        
        except Exception as e:
            self.handle_error(e)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _generate_search_queries(self, topic: str) -> List[str]:
        """Generate targeted search queries for a topic"""
        logger.info(f"[Researcher] Generating search queries for: {topic}")
        
        prompt = f"""
        Generate 5 specific, targeted search queries to thoroughly research: "{topic}"
        
        Requirements:
        - Mix of definition, tutorial, benchmarks, and real-world applications
        - Include both academic and practical perspectives
        - Look for recent 2024-2025 information
        
        Format as a JSON list:
        ["query 1", "query 2", ...]
        """
        
        response = llm_manager.generate(prompt, max_tokens=500)
        
        try:
            # Extract JSON from response
            import json
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                queries = json.loads(json_match.group())
                return queries
        except:
            # Fallback: split by newlines
            return [q.strip() for q in response.split('\n') if q.strip()]
    
    async def _gather_research(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Gather research data from multiple sources"""
        logger.info(f"[Researcher] Gathering data from {len(queries)} search queries")
        
        results = []
        for query in queries:
            # Simulate web search (in production, integrate with actual APIs)
            result = await self.use_tool("web_search", query=query, num_results=5)
            if result:
                results.extend(result)
                self.sources.extend([r.get("url", "") for r in result if r.get("url")])
        
        logger.info(f"[Researcher] Found {len(self.sources)} sources")
        return results
    
    async def _structure_research(self, raw_data: List[Dict], topic: str) -> Dict[str, Any]:
        """Organize and structure raw research data"""
        logger.info(f"[Researcher] Structuring research data")
        
        prompt = f"""
        Based on research about "{topic}", structure the following information:
        
        Data: {str(raw_data)[:2000]}  # Truncate for size
        
        Create a structured summary with:
        1. Definition - Clear explanation of what it is
        2. Key Concepts - 3-5 core concepts to understand
        3. How It Works - Step-by-step explanation
        4. WHY It Matters - Practical importance
        5. Use Cases - 3-4 real-world applications
        6. Tools/Libraries - What's available
        7. Resources - Learning resources
        
        Format as JSON.
        """
        
        response = llm_manager.generate(prompt, max_tokens=2000)
        
        try:
            import json
            return json.loads(response)
        except:
            return {"raw_content": response}
    
    async def _create_learning_summary(self, topic: str, data: Dict) -> str:
        """Create beginner-friendly learning summary"""
        logger.info(f"[Researcher] Creating learning summary")
        
        prompt = f"""
        Create a clear, beginner-friendly learning summary about "{topic}".
        
        Structured data: {str(data)[:1000]}
        
        Include:
        - Simple explanation in 2-3 sentences
        - Why should someone learn this?
        - 3 key takeaways
        - Next steps to learn more
        
        Make it accessible for someone new to the topic.
        """
        
        return llm_manager.generate(prompt, max_tokens=1000)
    
    async def _execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute tools for research"""
        
        if tool_name == "web_search":
            # Simulate web search
            logger.info(f"[Researcher] Searching: {kwargs.get('query')}")
            return [
                {
                    "title": "Search Result 1",
                    "url": "https://example.com/1",
                    "content": "Sample content..."
                }
            ]
        
        elif tool_name == "scrape_url":
            logger.info(f"[Researcher] Scraping: {kwargs.get('url')}")
            return {"content": "Scraped content..."}
        
        return None
