"""
Task Orchestrator
Coordinates multiple agents to complete complex tasks
Manages agent workflow and dependencies
"""

from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime, timedelta
from agents.researcher_agent import ResearcherAgent
from agents.content_creator_agent import ContentCreatorAgent
from agents.growth_optimizer_agent import GrowthOptimizerAgent
from config import settings

logger = logging.getLogger(__name__)


class TaskOrchestrator:
    """
    Orchestrates workflow between multiple agents
    Manages dependencies and data flow
    """
    
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.content_creator = ContentCreatorAgent()
        self.growth_optimizer = GrowthOptimizerAgent()
        self.execution_history = []
        self.task_queue = []
    
    async def execute_full_pipeline(self, topic: str, context: Dict[str, Any] = None, with_images: bool = False) -> Dict[str, Any]:
        """
        Execute full pipeline: Research → Content → Optimization
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🚀 STARTING FULL PIPELINE FOR: {topic}")
        logger.info(f"{'='*80}\n")
        
        start_time = datetime.utcnow()
        execution_log = {
            "topic": topic,
            "start_time": start_time.isoformat(),
            "stages": {}
        }
        
        try:
            # STAGE 1: Research
            logger.info("📚 STAGE 1: RESEARCH")
            logger.info("-" * 80)
            research_result = await self.researcher.execute(topic, context)
            execution_log["stages"]["research"] = research_result
            logger.info(f"✅ Found {research_result.get('sources_found', 0)} sources\n")
            
            if research_result.get("status") == "error":
                logger.error(f"Research failed: {research_result.get('error')}")
                return {"status": "error", "error": "Research stage failed"}
            
            # STAGE 2: Content Creation
            logger.info("📝 STAGE 2: CONTENT CREATION")
            logger.info("-" * 80)
            content_result = await self.content_creator.execute(
                f"Create posts about {topic}",
                research_result.get("research_data", {}),
                with_images=with_images
            )
            execution_log["stages"]["content_creation"] = content_result
            logger.info(f"✅ Created {content_result.get('total_posts', 0)} content pieces\n")
            
            if content_result.get("status") == "error":
                logger.error(f"Content creation failed: {content_result.get('error')}")
                return {"status": "error", "error": "Content creation stage failed"}
            
            # STAGE 3: Growth Optimization
            logger.info("📊 STAGE 3: GROWTH OPTIMIZATION")
            logger.info("-" * 80)
            
            # Simulated metrics (in production, fetch from LinkedIn)
            metrics = {
                "avg_impressions": 2400,
                "avg_engagement_rate": 0.68,
                "avg_likes": 180,
                "avg_comments": 24,
                "follower_growth": 0.045
            }
            
            optimization_result = await self.growth_optimizer.execute(
                f"Optimize growth for {topic}",
                metrics
            )
            execution_log["stages"]["growth_optimization"] = optimization_result
            logger.info(f"✅ Generated optimal posting schedule\n")
            
            if optimization_result.get("status") == "error":
                logger.error(f"Growth optimization failed: {optimization_result.get('error')}")
            
            # STAGE 4: LinkedIn Auto-Posting (if enabled)
            logger.info("📤 STAGE 4: LINKEDIN AUTO-POSTING")
            logger.info("-" * 80)
            
            posting_results = []
            if settings.auto_post_enabled:
                posting_results = await self._post_content_to_linkedin(
                    content_result.get("content_pieces", []),
                    optimization_result.get("optimal_posting_schedule", [])
                )
                execution_log["stages"]["linkedin_posting"] = {
                    "status": "completed",
                    "posts_posted": len(posting_results),
                    "results": posting_results
                }
                logger.info(f"✅ Posted {len(posting_results)} posts to LinkedIn\n")
            else:
                logger.info("⏭️  Auto-posting disabled. Posts ready for manual posting.\n")
                execution_log["stages"]["linkedin_posting"] = {
                    "status": "skipped",
                    "reason": "auto_post_enabled=False"
                }
            
            # Compile final result
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            execution_log["end_time"] = end_time.isoformat()
            execution_log["execution_time_seconds"] = execution_time
            
            final_result = {
                "status": "success",
                "topic": topic,
                "execution_log": execution_log,
                "research": research_result,
                "content": content_result,
                "growth_strategy": optimization_result,
                "linkedin_posting": {
                    "enabled": settings.auto_post_enabled,
                    "posts_posted": len(posting_results),
                    "results": posting_results
                },
                "next_steps": self._generate_next_steps(content_result, optimization_result, posting_results),
                "execution_time": f"{execution_time:.1f} seconds"
            }
            
            self.execution_history.append(final_result)
            
            logger.info("=" * 80)
            logger.info("✅ FULL PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info(f"📖 Topics researched: 1 | 📝 Posts created: {content_result.get('total_posts')} | 📤 Posted: {len(posting_results)} | ⏱️ Time: {execution_time:.0f}s")
            logger.info("=" * 80)
            
            return final_result
        
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "execution_log": execution_log
            }
    
    def _generate_next_steps(self, content_result: Dict, growth_result: Dict, posting_results: List[Dict] = None) -> List[str]:
        """Generate next steps for the user"""
        steps = []
        
        if content_result.get("status") == "success":
            steps.append(f"📝 Review {content_result.get('total_posts', 0)} generated posts")
            
            if posting_results and len(posting_results) > 0:
                steps.append(f"✅ {len(posting_results)} posts posted to LinkedIn!")
                steps.append("📊 Monitor engagement in your LinkedIn dashboard")
            else:
                steps.append("✏️ Make any edits or personalizations")
            
            if growth_result.get("status") == "success":
                steps.append("📅 Posts scheduled according to optimal times")
                steps.append("📊 Set up analytics tracking")
        
        steps.append("🔄 Next topic: Choose another AI/ML topic to research")
        
        return steps
    
    async def _post_content_to_linkedin(self, content_pieces: List[Dict], schedule: List[Dict] = None) -> List[Dict]:
        """
        Post content pieces to LinkedIn with optimal scheduling
        
        Args:
            content_pieces: List of content dicts to post
            schedule: Optional list of scheduled times
        
        Returns:
            List of posting results
        """
        if not content_pieces:
            return []
        
        logger.info(f"\n📤 Preparing to post {len(content_pieces)} content pieces to LinkedIn...")
        
        results = []
        now = datetime.utcnow()
        
        for i, content in enumerate(content_pieces):
            # Determine posting time
            if schedule and i < len(schedule):
                post_time = datetime.fromisoformat(schedule[i].get("timestamp", now.isoformat()))
            else:
                # Default: space posts 12 hours apart starting tomorrow morning
                post_time = now + timedelta(days=1, hours=9)
                post_time = now + timedelta(hours=(i + 1) * 12)
            
            try:
                # Post to LinkedIn (via Buffer API in main.py)
                results.append({
                    "status": "scheduled",
                    "content": content,
                    "schedule_time": post_time.isoformat()
                })
                logger.info(f"   [{i+1}/{len(content_pieces)}] Scheduled for posting")
            
            except Exception as e:
                logger.error(f"   [{i+1}/{len(content_pieces)}] Error: {e}")
                results.append({
                    "status": "error",
                    "error": str(e),
                    "content": content
                })
        
        return results
    
    async def post_manually(self, content_pieces: List[Dict]) -> Dict[str, Any]:
        """
        Post content pieces to LinkedIn right now
        Useful for manual triggering
        
        Args:
            content_pieces: List of content to post
        
        Returns:
            Dict with posting results
        """
        logger.info(f"📤 Manually posting {len(content_pieces)} contents to LinkedIn...")
        
        results = await self._post_content_to_linkedin(content_pieces, schedule=None)
        
        return {
            "status": "success" if all(r.get("status") == "success" for r in results) else "partial_failure",
            "total_posted": len([r for r in results if r.get("status") == "success"]),
            "total_failed": len([r for r in results if r.get("status") != "success"]),
            "results": results
        }
    
    async def execute_parallel(self, tasks: List[str]) -> Dict[str, Any]:
        """Execute multiple research tasks in parallel"""
        logger.info(f"🔄 Executing {len(tasks)} tasks in parallel...")
        
        # Run all research tasks concurrently
        results = await asyncio.gather(*[
            self.researcher.execute(task)
            for task in tasks
        ])
        
        return {
            "status": "success",
            "tasks_executed": len(tasks),
            "results": results
        }
    
    def get_execution_history(self) -> List[Dict]:
        """Get history of all executed pipelines"""
        return self.execution_history
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of all agents"""
        return {
            "researcher": self.researcher.get_status(),
            "content_creator": self.content_creator.get_status(),
            "growth_optimizer": self.growth_optimizer.get_status(),
            "total_executions": len(self.execution_history)
        }
