"""
Content Creator Agent
Transforms research into LinkedIn posts and content
Optimizes for engagement and reach
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
from agents.base_agent import Agent, AgentStatus
from services.llm_provider import llm_manager

logger = logging.getLogger(__name__)


class ContentCreatorAgent(Agent):
    """
    Content Creator Agent
    Responsible for:
    - Transforming research into content
    - Creating multiple content variations
    - Optimizing for LinkedIn engagement
    - Generating hashtags and hooks
    """
    
    def __init__(self):
        super().__init__(
            name="Content Creator",
            role="LinkedIn Content Strategist",
            description="Creates engaging LinkedIn posts optimized for reach and engagement"
        )
        self.content_formats = []
    
    def get_available_tools(self) -> List[str]:
        return [
            "generate_post",
            "generate_thread",
            "generate_infographic_brief",
            "optimize_for_engagement",
            "generate_hashtags",
            "generate_hook"
        ]
    
    def _get_topic_images(self, topic: str) -> Dict[str, str]:
        """Get topic-specific image URLs for LinkedIn posts"""
        topic_lower = topic.lower()
        
        # Generic AI/ML images
        ai_general = "https://images.unsplash.com/photo-1677442d019cecf8d6e44706c2b1f4b6?w=800&q=80"
        code_laptop = "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80"
        data_science = "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=800&q=80"
        neural_network = "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"
        server_tech = "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80"
        
        # Topic-specific mapping
        if any(word in topic_lower for word in ["rag", "retrieval", "augmented generation", "vector"]):
            return {
                "technical": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
                "lessons": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
                "architecture": "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=800&q=80",
                "optimization": "https://images.unsplash.com/photo-1639762681033-9461497caf0f?w=800&q=80"
            }
        elif any(word in topic_lower for word in ["llm", "language model", "gpt", "bert", "transformer"]):
            return {
                "technical": "https://images.unsplash.com/photo-1677442d019cecf8d6e44706c2b1f4b6?w=800&q=80",
                "lessons": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80",
                "architecture": "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=800&q=80",
                "optimization": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"
            }
        elif any(word in topic_lower for word in ["prompt", "engineering", "tuning"]):
            return {
                "technical": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80",
                "lessons": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
                "architecture": "https://images.unsplash.com/photo-1599658880455-8a1f47e2e532?w=800&q=80",
                "optimization": "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=800&q=80"
            }
        elif any(word in topic_lower for word in ["fine-tuning", "transfer learning", "training"]):
            return {
                "technical": "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=800&q=80",
                "lessons": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
                "architecture": "https://images.unsplash.com/photo-1439694458606-4d190b379cbf?w=800&q=80",
                "optimization": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"
            }
        elif any(word in topic_lower for word in ["embedding", "vector", "similarity"]):
            return {
                "technical": "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=800&q=80",
                "lessons": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80",
                "architecture": "https://images.unsplash.com/photo-1639762681033-9461497caf0f?w=800&q=80",
                "optimization": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"
            }
        elif any(word in topic_lower for word in ["gpu", "inference", "deployment", "production"]):
            return {
                "technical": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80",
                "lessons": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
                "architecture": "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=800&q=80",
                "optimization": "https://images.unsplash.com/photo-1639762681033-9461497caf0f?w=800&q=80"
            }
        elif any(word in topic_lower for word in ["vision", "image", "computer vision", "cv"]):
            return {
                "technical": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80",
                "lessons": "https://images.unsplash.com/photo-1633356122544-f134324ef6db?w=800&q=80",
                "architecture": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&q=80",
                "optimization": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80"
            }
        else:
            # Default images for any AI topic
            return {
                "technical": ai_general,
                "lessons": code_laptop,
                "architecture": data_science,
                "optimization": neural_network
            }
    
    async def execute(self, task: str, research_data: Dict[str, Any], with_images: bool = False) -> Dict[str, Any]:
        """
        Transform research into professional LinkedIn content
        Example: "Create posts about RAG from the research data"
        """
        self.set_status(AgentStatus.THINKING, "Planning content strategy...")
        
        try:
            self.add_memory("user", task)
            
            # Extract topic from task
            topic = task.replace("Create posts about ", "").replace("posts about", "").strip()
            
            # Map topics to relevant image URLs
            topic_images = self._get_topic_images(topic)
            
            # Natural, engaging LinkedIn posts focused on value and insights
            contents = [
                {
                    "type": "practical_insight",
                    "text": f"Just spent the last week diving deep into {topic}, and I'm genuinely impressed by how much this simplifies building smarter systems.\n\n" +
                           "The biggest thing I learned? Most people overcomplicate this. You don't need the fanciest setup—you need the right fundamentals.\n\n" +
                           "Here's what actually matters:\n" +
                           "• Understanding your actual constraints (speed, cost, accuracy) beats theoretically perfect solutions\n" +
                           "• Simple implementations that work beat complex ones that don't\n" +
                           "• Your monitoring setup matters as much as your main code\n" +
                           "• Failure happens—design for it, don't hope it won't\n\n" +
                           "If you're building production systems, start with these principles. The rest follows naturally.\n\n" +
                           "What's your biggest challenge when implementing this? Would love to hear from the community. #AI #ProductionML",
                    "hashtags": ["#AI", "#MachineLearning", "#ProductionML", "#SoftwareEngineering"],
                    "engagement_estimate": "Very High 📊",
                    **({"image_url": topic_images["technical"], "image_alt": f"Production insights on {topic}"} if with_images else {})
                },
                {
                    "type": "lessons_learned",
                    "text": f"Been building production systems long enough to know: {topic} implementations fail for surprisingly consistent reasons.\n\n" +
                           "Here's what separates systems that scale from ones that break:\n\n" +
                           "First, data quality is everything. No algorithm, no matter how sophisticated, survives bad input. Invest in validation.\n\n" +
                           "Second, observability isn't optional. If you can't measure it, you can't fix it. Build monitoring in from day one, not after things break.\n\n" +
                           "Third, graceful degradation saves systems. Design your fallbacks before you need them. Your users will appreciate it.\n\n" +
                           "Fourth, the boring solution often wins. Boring is reliable. Reliable is profitable. Profitable is what keeps projects alive.\n\n" +
                           "The teams that succeed with this don't cut corners—they cut complexity. They focus on what actually matters for their specific constraints.\n\n" +
                           "If you're planning a production rollout, these patterns matter more than framework choices. #Production #Engineering #BestPractices",
                    "hashtags": ["#Production", "#Engineering", "#SoftwareEng", "#BestPractices"],
                    "engagement_estimate": "Very High 🔥",
                    **({"image_url": topic_images["lessons"], "image_alt": f"Production lessons learned from {topic}"} if with_images else {})
                },
                {
                    "type": "architecture_pattern",
                    "text": f"The architecture that actually works for {topic} in production follows a pattern we see repeatedly:\n\n" +
                           "You need clean separation between input validation, core logic, output verification, and monitoring. This isn't fancy—it's essential.\n\n" +
                           "Input validation prevents bad data from propagating through your system. One bad request shouldn't cascade into system failure.\n\n" +
                           "Core logic should be isolated and testable. The easier it is to test in isolation, the fewer production fires you'll fight. Experienced teams obsess over this.\n\n" +
                           "Output verification catches issues before they reach users. Sanity checks on results cost milliseconds of latency and save hours of debugging.\n\n" +
                           "Monitoring and logging throughout let you understand what's happening when (not if) problems occur. Observability is your safety net.\n\n" +
                           "The supporting pieces matter too: proper error handling, sensible timeouts, retry logic, and circuit breakers. These aren't \"advanced\"—they're what separates production systems from prototypes.\n\n" +
                           "This pattern scales. Whether it's a small service or massive distributed system, these principles hold. #SystemsDesign #Architecture #Production",
                    "hashtags": ["#SystemsDesign", "#Architecture", "#Production", "#Engineering"],
                    "engagement_estimate": "Very High 📈",
                    **({"image_url": topic_images["architecture"], "image_alt": f"Production architecture pattern for {topic}"} if with_images else {})
                },
                {
                    "type": "cost_optimization",
                    "text": f"Real talk: {topic} systems become expensive fast if you're not intentional about costs.\n\n" +
                           "I've seen teams cut costs by 30-50% without sacrificing quality. Here's the pattern:\n\n" +
                           "Start by understanding where your money actually goes. Most teams guess wrong. Profile everything. Measure before optimizing.\n\n" +
                           "Caching is a superpower. If you're computing the same thing twice, you're throwing money away. Smart caching reduces load dramatically.\n\n" +
                           "Right-size your infrastructure for actual usage, not hypothetical maximum load. This is where I see the biggest waste. Monitoring helps here—scale with demand, not fear.\n\n" +
                           "Batch processing when possible multiplies efficiency. Processing in batches beats one-off requests for throughput and cost.\n\n" +
                           "Finally, track cost per unit of output. This simple metric changes how you think about optimization. Are you getting more value per dollar? That's the real question.\n\n" +
                           "The teams winning on costs don't cut corners—they cut waste. Systematic optimization beats heroic gestures every time. #CostOptimization #ML #Engineering",
                    "hashtags": ["#CostOptimization", "#MachineLearning", "#Efficiency", "#Engineering"],
                    "engagement_estimate": "High 💡",
                    **({"image_url": topic_images["optimization"], "image_alt": f"Cost optimization strategies for {topic}"} if with_images else {})
                }
            ]
            
            self.set_status(AgentStatus.COMPLETE, "Content created successfully")
            
            return {
                "status": "success",
                "content_pieces": contents,
                "total_posts": len(contents),
                "with_images": with_images,
                "suggested_schedule": [
                    {"day": "Monday", "time": "09:00", "post": "practical_insight"},
                    {"day": "Wednesday", "time": "10:30", "post": "lessons_learned"},
                    {"day": "Friday", "time": "14:00", "post": "architecture_pattern"},
                    {"day": "Sunday", "time": "11:00", "post": "cost_optimization"}
                ]
            }
        
        except Exception as e:
            self.handle_error(e)
            return {"status": "error", "error": str(e)}
    
    async def _create_quick_tip(self, research_data: Dict) -> Dict[str, Any]:
        """Create a quick, engaging post (150-200 chars)"""
        logger.info("[Content Creator] Creating quick tip...")
        
        prompt = f"""
        Create a super engaging LinkedIn post based on this research:
        {str(research_data)[:1000]}
        
        Requirements:
        - 150-200 characters (fits in preview)
        - Starts with hook: "Just learned...", "Mind-blowing...", "Game-changer..."
        - 1 key insight
        - Call to action at end
        - Professional but conversational tone
        - Include emoji strategically
        
        Format: Just return the post content, no other text.
        """
        
        content = llm_manager.generate(prompt, max_tokens=300)
        
        hashtags = await self.use_tool("generate_hashtags", 
                                      topic=research_data.get("topic", "AI"),
                                      num=5)
        
        return {
            "type": "quick_tip",
            "content": content,
            "character_length": len(content),
            "hashtags": hashtags or ["#AI", "#MachineLearning", "#Learning"],
            "expected_engagement": "Best for viral reach (2-5K impressions)",
            "best_posting_day": "Tuesday-Thursday",
            "best_time_est": "9:00 AM"
        }
    
    async def _create_technical_thread(self, research_data: Dict) -> Dict[str, Any]:
        """Create 5-part educational thread"""
        logger.info("[Content Creator] Creating technical thread...")
        
        prompt = f"""
        Create a 5-part LinkedIn thread based on this research:
        {str(research_data)[:1500]}
        
        Thread should:
        - Part 1: Hook (make them stop scrolling)
        - Part 2-4: Progressive deeper explanation
        - Part 5: Call to action (ask what they use this for)
        
        Each part: 200-300 characters max
        Use simple language, avoid jargon when possible
        Include 1-2 relevant emojis per part
        
        Format as JSON: {{"part_1": "...", "part_2": "...", ...}}
        """
        
        import json
        import re
        
        response = llm_manager.generate(prompt, max_tokens=2000)
        
        try:
            # Extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                thread = json.loads(json_match.group())
            else:
                thread = {"part_1": response}
        except:
            thread = {"part_1": response}
        
        return {
            "type": "technical_thread",
            "content": thread,
            "total_parts": len(thread),
            "expected_engagement": "High engagement from technical audience",
            "best_posting_day": "Wednesday",
            "best_time_est": "10:00 AM"
        }
    
    async def _create_hot_take(self, research_data: Dict) -> Dict[str, Any]:
        """Create controversial/thought-provoking post"""
        logger.info("[Content Creator] Creating hot take...")
        
        prompt = f"""
        Create a thought-provoking LinkedIn post (NOT offensive, just edgy/interesting):
        {str(research_data)[:1000]}
        
        Make it:
        - Slightly contrarian (challenges conventional wisdom)
        - Backed by the research data
        - Engaging (gets people to comment/debate)
        - Professional
        - 250-400 characters
        
        Example style: "Everyone says X, but actually Y because Z"
        
        Return just the post content.
        """
        
        content = llm_manager.generate(prompt, max_tokens=500)
        
        return {
            "type": "hot_take",
            "content": content,
            "engagement_driver": "Debate/Discussion",
            "expected_comments": "High (this gets people talking!)",
            "best_posting_day": "Thursday",
            "best_time_est": "2:00 PM"
        }
    
    async def _create_visual_brief(self, research_data: Dict) -> Dict[str, Any]:
        """Create brief for infographic/visual"""
        logger.info("[Content Creator] Creating visual brief...")
        
        prompt = f"""
        Create a detailed brief for an infographic about:
        {str(research_data)[:1000]}
        
        Include:
        - Title
        - 5 key data points/statistics that would look good as visuals
        - Color scheme suggestion
        - Visual metaphor/icon suggestions
        - 1-2 sentence caption
        
        Format as JSON.
        """
        
        import json
        import re
        
        response = llm_manager.generate(prompt, max_tokens=1500)
        
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                brief = json.loads(json_match.group())
            else:
                brief = {"description": response}
        except:
            brief = {"description": response}
        
        return {
            "type": "infographic_brief",
            "content": brief,
            "expected_engagement": "Highest reach (visual content)",
            "best_posting_day": "Tuesday",
            "best_time_est": "9:00 AM"
        }
    
    def _generate_schedule(self, contents: List[Dict]) -> List[Dict]:
        """Generate optimal posting schedule"""
        schedule = [
            {
                "day": "Tuesday",
                "time": "9:00 AM EST",
                "type": "Quick Tip or Infographic",
                "content_index": 0
            },
            {
                "day": "Wednesday",
                "time": "10:00 AM EST",
                "type": "Technical Thread",
                "content_index": 1
            },
            {
                "day": "Thursday",
                "time": "2:00 PM EST",
                "type": "Hot Take",
                "content_index": 2
            },
            {
                "day": "Saturday",
                "time": "10:00 AM EST",
                "type": "Recap or New Topic",
                "content_index": 3 if len(contents) > 3 else 0
            }
        ]
        return schedule
    
    async def _execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute content creation tools"""
        
        if tool_name == "generate_hashtags":
            topic = kwargs.get("topic", "AI")
            return [f"#{tag}" for tag in ["AI", "MachineLearning", "Learning", topic]]
        
        elif tool_name == "generate_hook":
            return "Just learned something mind-blowing about AI"
        
        return None
