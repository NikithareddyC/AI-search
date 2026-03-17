"""
Main FastAPI Application
AI Content & Growth Platform Backend
"""

from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

from config import settings, validate_settings
from database import init_db
from services.orchestrator import TaskOrchestrator
from services.buffer_linkedin import buffer_linkedin_service
from services.trending_service import trending_service

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Content & Growth Platform",
    description="Multi-agent AI system for learning AI/ML topics and auto-publishing to LinkedIn",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (configure for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
orchestrator = TaskOrchestrator()
active_websockets = []


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("🚀 Starting AI Content & Growth Platform...")
    validate_settings()
    init_db()
    logger.info("✅ Application ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down application...")


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    return orchestrator.get_agent_status()


@app.get("/api/trending-topics")
async def get_trending_topics():
    """Get trending AI/ML topics from around the world"""
    logger.info("🔍 Fetching trending AI/ML topics...")
    try:
        result = await trending_service.get_trending_topics()
        return result
    except Exception as e:
        logger.error(f"Error fetching trending topics: {e}")
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "total": len(trending_service.fallback_topics),
            "topics": trending_service.fallback_topics,
            "source": "cached"
        }


# ============================================================================
# RESEARCH & LEARNING ENDPOINTS
# ============================================================================

@app.post("/api/research/topic")
async def research_topic(topic: str, background_tasks: BackgroundTasks):
    """
    Research a topic
    Example: /api/research/topic?topic=RAG
    """
    logger.info(f"📚 Research request: {topic}")
    
    if not topic or len(topic) < 3:
        raise HTTPException(status_code=400, detail="Topic must be at least 3 characters")
    
    try:
        # Execute full pipeline in background
        result = await orchestrator.execute_full_pipeline(topic)
        
        return {
            "status": "success",
            "topic": topic,
            "execution_id": f"{topic}_{datetime.utcnow().timestamp()}",
            "result": result
        }
    
    except Exception as e:
        logger.error(f"Error researching topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/research/history")
async def get_research_history():
    """Get history of all research pipelines"""
    return {
        "total_researches": len(orchestrator.execution_history),
        "history": orchestrator.execution_history[-10:]  # Last 10
    }


# ============================================================================
# CONTENT ENDPOINTS
# ============================================================================

@app.get("/api/content/list")
async def list_generated_content():
    """List all generated content (from history)"""
    content_list = []
    
    for execution in orchestrator.execution_history:
        if execution.get("status") == "success" and "content" in execution:
            content_list.append({
                "topic": execution.get("topic"),
                "created_at": execution.get("start_time"),
                "posts_count": execution["content"].get("total_posts", 0),
                "content_pieces": execution["content"].get("content_pieces", [])
            })
    
    return {
        "total_content_created": len(content_list),
        "content": content_list
    }


@app.get("/api/content/draft/{topic}")
async def get_content_draft(topic: str):
    """Get draft content for a specific topic"""
    for execution in orchestrator.execution_history:
        if execution.get("topic") == topic and execution.get("status") == "success":
            return {
                "status": "success",
                "topic": topic,
                "content": execution.get("content", {})
            }
    
    raise HTTPException(status_code=404, detail=f"No content found for topic: {topic}")


# ============================================================================
# GROWTH & ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/growth/insights")
async def get_growth_insights():
    """Get current growth insights"""
    latest_execution = orchestrator.execution_history[-1] if orchestrator.execution_history else None
    
    if not latest_execution:
        return {"message": "No data yet. Run a research first."}
    
    return {
        "status": "success",
        "insights": latest_execution.get("growth_strategy", {})
    }


@app.get("/api/growth/predictions")
async def get_growth_predictions():
    """Get follower growth predictions"""
    latest_execution = orchestrator.execution_history[-1] if orchestrator.execution_history else None
    
    if not latest_execution:
        # Default prediction
        return {
            "current_followers": 2000,
            "predicted_1week": 2090,
            "predicted_1month": 2387,
            "predicted_3months": 3516,
            "predicted_6months": 5452
        }
    
    growth_strategy = latest_execution.get("growth_strategy", {})
    return growth_strategy.get("predicted_growth", {})


@app.get("/api/growth/schedule")
async def get_posting_schedule():
    """Get optimal posting schedule"""
    latest_execution = orchestrator.execution_history[-1] if orchestrator.execution_history else None
    
    if not latest_execution:
        return {"message": "No schedule available"}
    
    growth_strategy = latest_execution.get("growth_strategy", {})
    return growth_strategy.get("optimal_posting_schedule", [])


@app.post("/api/research-and-post")
async def research_and_auto_post(topic: str, auto_post: bool = True, with_images: bool = False):
    """
    Complete 3-in-1 workflow:
    1. Research the topic
    2. Generate content
    3. Auto-post to LinkedIn
    
    Example: /api/research-and-post?topic=RAG&auto_post=true&with_images=true
    """
    logger.info(f"🚀 Complete workflow: Research → Create → Post for: {topic} (with_images={with_images})")
    
    try:
        # Execute full pipeline with images option
        result = await orchestrator.execute_full_pipeline(topic, with_images=with_images)
        logger.info(f"Orchestrator result: {result}")
        
        # Always return consistent format
        if result.get("status") == "success":
            response = {
                "status": "success",
                "topic": topic,
                "content": result.get("content", {}),
                "research": result.get("research", {}),
                "growth_strategy": result.get("growth_strategy", {}),
                "posts_created": result.get("content", {}).get("total_posts", 0)
            }
            
            # Only post to LinkedIn if requested
            if auto_post:
                content_pieces = result.get("content", {}).get("content_pieces", [])
                posting_results = await orchestrator._post_content_to_linkedin(content_pieces)
                response["posts_to_linkedin"] = len(posting_results)
                response["posting_results"] = posting_results
                response["next_action"] = "Monitor engagement in your LinkedIn dashboard! 📊"
            
            return response
        else:
            return {
                "status": "error",
                "error": result.get("error", "Unknown error - result status is not success"),
                "topic": topic,
                "result": result
            }
    
    except Exception as e:
        logger.error(f"Error in complete workflow: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Exception: {str(e)}",
            "type": type(e).__name__,
            "topic": topic
        }


@app.post("/api/post-selected")
async def post_selected_content(request: dict) -> Dict[str, Any]:
    """
    Auto-post selected posts to LinkedIn using Selenium
    Spreads posts across Mon, Tue, Wed, Thu
    
    Example:
    POST /api/post-selected
    {
        "topic": "Retrieval Augmented Generation",
        "posts": [...],  // array of selected post objects
        "with_images": true
    }
    """
    logger.info(f"📤 Starting auto-posting of {len(request.get('posts', []))} posts to LinkedIn")
    
    try:
        from datetime import datetime, timedelta
        
        posts = request.get('posts', [])
        topic = request.get('topic', '')
        with_images = request.get('with_images', False)
        
        if not posts:
            return {
                "status": "error",
                "error": "No posts selected"
            }
        
        # Check if Buffer is authenticated
        if not buffer_linkedin_service.is_authenticated:
            logger.error("❌ Buffer not authenticated")
            return {
                "status": "error",
                "message": "Buffer not configured. Add BUFFER_ACCESS_TOKEN to .env",
                "authenticated": False,
                "setup_url": "https://buffer.com/app/connections/tokens",
                "instructions": "1. Sign up at https://buffer.com (free), 2. Get access token, 3. Add to .env as BUFFER_ACCESS_TOKEN"
            }
        
        # Prepare content for posting
        logger.info("📝 Preparing posts for Buffer/LinkedIn...")
        contents_to_post = []
        for idx, post in enumerate(posts):
            content = {
                "text": post.get("text", ""),
                "hashtags": post.get("hashtags", []),
                "type": post.get("type", "post"),
                "image_url": post.get("image_url") if with_images else None
            }
            contents_to_post.append(content)
        
        # Post to LinkedIn via Buffer
        logger.info(f"🚀 Scheduling {len(contents_to_post)} posts via Buffer...")
        buffer_result = await buffer_linkedin_service.post_batch(contents_to_post, spacing_hours=24)
        
        # Build response with schedule details
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday']
        times = ['09:00 AM', '02:00 PM', '10:00 AM', '03:00 PM']
        
        schedule = []
        now = datetime.utcnow()
        for idx, post in enumerate(posts):
            day_idx = idx % len(days)
            post_time = now + timedelta(hours=24 * (idx + 1))
            
            # Get corresponding post result from Buffer  
            buffer_post = buffer_result["posts"][idx] if idx < len(buffer_result.get("posts", [])) else {}
            
            schedule.append({
                "post_id": idx + 1,
                "day": days[day_idx],
                "time": times[day_idx],
                "scheduled_datetime": post_time.isoformat(),
                "post_type": post.get("type", "post"),
                "status": buffer_post.get("status", "scheduled"),
                "topic": topic,
                "has_image": "image_url" in post and bool(post.get("image_url")),
                "text": post.get("text", ""),
                "buffer_response": buffer_post
            })
        
        logger.info(f"✅ Successfully scheduled {len(posts)} posts via Buffer!")
        
        return {
            "status": "success",
            "message": f"✅ {len(posts)} posts scheduled on LinkedIn via Buffer!",
            "topic": topic,
            "total_posts": len(posts),
            "authenticated": True,
            "service": "Buffer",
            "schedule": schedule,
            "next_action": f"Posts will be published starting {schedule[0]['day']} at {schedule[0]['time']}",
            "posting_instructions": "🎉 Check your Buffer dashboard for posts being published! https://buffer.com/app"
        }
    
    except Exception as e:
        logger.error(f"❌ Error during LinkedIn posting: {e}")
        return {
            "status": "error",
            "message": f"Error posting to LinkedIn: {str(e)}",
            "error_details": str(e),
            "authenticated": False
        }
    
    except Exception as e:
        logger.error(f"Error scheduling posts: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }


# ============================================================================
# BATCH & BULK OPERATIONS ENDPOINTS
# ============================================================================

@app.post("/api/batch/research-multiple")
async def batch_research_topics(topics: list, auto_post: bool = False) -> Dict[str, Any]:
    """
    Research multiple topics and optionally auto-post all
    Perfect for planning a month of content in one go!
    
    Example:
    POST /api/batch/research-multiple
    {
        "topics": ["RAG", "Fine-tuning LLMs", "Prompt Engineering", "Vector Databases"],
        "auto_post": true
    }
    """
    logger.info(f"📚 Batch research starting for {len(topics)} topics...")
    
    results = {
        "status": "processing",
        "topics": topics,
        "total_topics": len(topics),
        "completed": 0,
        "failed": 0,
        "results": [],
        "total_posts_created": 0,
        "total_posts_to_linkedin": 0
    }
    
    for i, topic in enumerate(topics, 1):
        logger.info(f"[{i}/{len(topics)}] Processing: {topic}")
        
        try:
            # Execute pipeline
            result = await orchestrator.execute_full_pipeline(topic)
            
            if result.get("status") == "success":
                results["completed"] += 1
                posts_created = result.get("content", {}).get("total_posts", 0)
                results["total_posts_created"] += posts_created
                
                # Auto-post if enabled
                if auto_post:
                    content_pieces = result.get("content", {}).get("content_pieces", [])
                    posting_results = await orchestrator._post_content_to_linkedin(content_pieces)
                    results["total_posts_to_linkedin"] += len(posting_results)
                
                results["results"].append({
                    "topic": topic,
                    "status": "success",
                    "posts_created": posts_created
                })
            else:
                results["failed"] += 1
                results["results"].append({
                    "topic": topic,
                    "status": "failed",
                    "error": result.get("error", "Unknown error")
                })
        
        except Exception as e:
            results["failed"] += 1
            results["results"].append({
                "topic": topic,
                "status": "error",
                "error": str(e)
            })
            logger.error(f"Error processing {topic}: {e}")
    
    results["status"] = "completed"
    
    return results


# ============================================================================
# WEBSOCKET - REAL-TIME EXECUTION MONITORING
# ============================================================================

@app.websocket("/ws/monitor")
async def websocket_monitor(websocket: WebSocket):
    """
    WebSocket for real-time monitoring of agent execution
    Clients connect here to see live agent execution updates
    """
    await websocket.accept()
    active_websockets.append(websocket)
    
    logger.info("✅ Client connected to WebSocket monitor")
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Echo the current agent status
            agent_status = orchestrator.get_agent_status()
            await websocket.send_json({
                "type": "status_update",
                "agents": agent_status,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        active_websockets.remove(websocket)
        logger.info("❌ Client disconnected from WebSocket")


async def broadcast_update(message: dict):
    """Broadcast update to all connected WebSocket clients"""
    for websocket in active_websockets:
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error broadcasting to websocket: {e}")


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get overall dashboard summary"""
    history = orchestrator.execution_history
    
    total_posts = sum([
        execution.get("content", {}).get("total_posts", 0)
        for execution in history
    ])
    
    return {
        "platform": "AI Content & Growth Platform",
        "total_researches": len(history),
        "total_posts_created": total_posts,
        "current_follower_count": 2000,
        "agent_status": orchestrator.get_agent_status(),
        "last_research": history[-1] if history else None
    }


# ============================================================================
# SETTINGS ENDPOINTS
# ============================================================================

@app.get("/api/settings")
async def get_settings():
    """Get current platform settings"""
    return {
        "auto_post_enabled": settings.auto_post_enabled,
        "post_schedule": settings.post_schedule,
        "posts_per_week": settings.posts_per_week,
        "optimal_post_time": settings.optimal_post_time_est,
        "default_llm": settings.default_llm,
        "debug_mode": settings.debug
    }


@app.post("/api/settings/update")
async def update_settings(settings_update: dict):
    """Update platform settings"""
    logger.info(f"Settings update requested: {settings_update}")
    
    # In production, validate and update settings in database
    return {
        "status": "success",
        "message": "Settings updated (simulation)",
        "updated_fields": list(settings_update.keys())
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint not found",
            "path": request.url.path
        }
    )


@app.exception_handler(500)
async def internal_error(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error"
        }
    )


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "name": "AI Content & Growth Platform",
        "version": "1.0.0",
        "description": "Multi-agent AI system for learning AI/ML topics and auto-publishing to LinkedIn",
        "endpoints": {
            "health": "/health",
            "research": "/api/research/topic?topic=RAG",
            "content": "/api/content/list",
            "growth": "/api/growth/insights",
            "dashboard": "/api/dashboard/summary",
            "websocket": "ws://localhost:8000/ws/monitor",
            "docs": "/docs"
        },
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level=settings.log_level.lower()
    )
