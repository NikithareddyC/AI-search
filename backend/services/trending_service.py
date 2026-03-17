"""
Trending Topics Service
Fetches trending AI/ML topics from multiple sources
"""

import logging
import aiohttp
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TrendingTopicsService:
    """Fetches trending AI/ML topics from various sources"""
    
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
        self.cache_duration = 3600  # 1 hour
        
        # Fallback trending topics (updated regularly)
        self.fallback_topics = [
            {
                "topic": "Retrieval Augmented Generation (RAG)",
                "description": "Latest advances in RAG systems and LangChain integration",
                "source": "Featured",
                "trending_score": 95
            },
            {
                "topic": "Large Language Models (LLM)",
                "description": "Updates on GPT-4, Claude 3, and open-source LLMs",
                "source": "Featured",
                "trending_score": 90
            },
            {
                "topic": "Agentic AI",
                "description": "Autonomous AI agents and multi-agent systems",
                "source": "Featured",
                "trending_score": 88
            },
            {
                "topic": "Vector Databases",
                "description": "Pinecone, Weaviate, and embedding management trends",
                "source": "Featured",
                "trending_score": 82
            },
            {
                "topic": "Fine-tuning and LORA",
                "description": "Cost-effective model customization techniques",
                "source": "Featured",
                "trending_score": 78
            },
            {
                "topic": "Prompt Engineering",
                "description": "Advanced techniques for optimal AI responses",
                "source": "Featured",
                "trending_score": 75
            },
            {
                "topic": "Multi-Modal AI",
                "description": "Vision-language models and multimodal learning",
                "source": "Featured",
                "trending_score": 80
            },
            {
                "topic": "AI Safety and Alignment",
                "description": "Ensuring AI systems act according to human values",
                "source": "Featured",
                "trending_score": 77
            },
            {
                "topic": "GraphRAG",
                "description": "Graph-based retrieval for improved context understanding",
                "source": "Featured",
                "trending_score": 82
            },
            {
                "topic": "Quantization and Model Compression",
                "description": "Making large models efficient and deployable",
                "source": "Featured",
                "trending_score": 79
            }
        ]
    
    async def fetch_from_hackernews(self) -> List[Dict[str, Any]]:
        """Fetch AI/ML trending topics from HackerNews"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://news.ycombinator.com/newest', timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        topics = []
                        ai_keywords = ['AI', 'ML', 'LLM', 'RAG', 'transformer', 'neural', 'model', 'learning', 'deep', 'agent']
                        
                        for row in soup.select('.athing')[:20]:
                            title_elem = row.select_one('.titleline > a')
                            if title_elem:
                                title = title_elem.get_text()
                                # Check if title contains AI/ML keywords
                                if any(keyword.lower() in title.lower() for keyword in ai_keywords):
                                    topics.append({
                                        "topic": title,
                                        "description": f"Trending on HackerNews",
                                        "source": "HackerNews",
                                        "trending_score": 85
                                    })
                        
                        return topics[:5]
        except Exception as e:
            logger.warning(f"Failed to fetch from HackerNews: {e}")
        
        return []
    
    async def fetch_from_reddit(self) -> List[Dict[str, Any]]:
        """Fetch trending topics from Reddit AI/ML communities"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            async with aiohttp.ClientSession() as session:
                url = 'https://www.reddit.com/r/MachineLearning/hot.json'
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        topics = []
                        
                        for post in data.get('data', {}).get('children', [])[:10]:
                            post_data = post.get('data', {})
                            title = post_data.get('title', '')
                            score = post_data.get('score', 0)
                            
                            if title and score > 100:
                                topics.append({
                                    "topic": title.split('[')[0].strip(),  # Remove tags
                                    "description": f"Trending on Reddit (Score: {score})",
                                    "source": "Reddit",
                                    "trending_score": min(90, (score // 100) * 10)
                                })
                        
                        return topics[:5]
        except Exception as e:
            logger.warning(f"Failed to fetch from Reddit: {e}")
        
        return []
    
    def extract_topic_name(self, text: str) -> str:
        """Extract clean topic name from longer text"""
        # Remove URLs and special characters
        text = text.split('|')[0].split('–')[0].split('-')[0].strip()
        # Limit length
        if len(text) > 100:
            text = text[:97] + "..."
        return text
    
    async def get_trending_topics(self) -> Dict[str, Any]:
        """Get trending AI/ML topics from multiple sources"""
        
        # Check cache
        if 'trending' in self.cache:
            if datetime.utcnow() < self.cache_expiry.get('trending', datetime.utcnow()):
                logger.info("📊 Using cached trending topics")
                return self.cache['trending']
        
        logger.info("🔍 Fetching trending AI/ML topics...")
        
        all_topics = []
        
        # Fetch from multiple sources concurrently
        hn_topics = await self.fetch_from_hackernews()
        reddit_topics = await self.fetch_from_reddit()
        
        all_topics.extend(hn_topics)
        all_topics.extend(reddit_topics)
        
        # If we got some topics from APIs, use them, otherwise use fallback
        if all_topics:
            # Remove duplicates and sort by trending score
            unique_topics = {}
            for topic in all_topics:
                key = topic['topic'].lower()
                if key not in unique_topics or topic['trending_score'] > unique_topics[key]['trending_score']:
                    unique_topics[key] = topic
            
            trending_list = list(unique_topics.values())
            trending_list.sort(key=lambda x: x['trending_score'], reverse=True)
            trending_list = trending_list[:10]
        else:
            # Use fallback if API calls failed
            logger.info("⚠️ Using fallback trending topics")
            trending_list = self.fallback_topics
        
        result = {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "total": len(trending_list),
            "topics": trending_list
        }
        
        # Cache the result
        self.cache['trending'] = result
        self.cache_expiry['trending'] = datetime.utcnow() + timedelta(seconds=self.cache_duration)
        
        logger.info(f"✅ Found {len(trending_list)} trending AI/ML topics")
        return result


# Global instance
trending_service = TrendingTopicsService()
