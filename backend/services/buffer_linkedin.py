"""
Buffer API Integration for LinkedIn Auto-Posting
Official, reliable LinkedIn scheduling and posting
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from config import settings

logger = logging.getLogger(__name__)


class BufferLinkedInService:
    """
    Manages LinkedIn posting via official Buffer API
    - Reliable and officially supported
    - No bot detection issues
    - Automatic scheduling
    """
    
    def __init__(self):
        self.is_authenticated = False
        self.access_token = getattr(settings, 'buffer_access_token', None)
        self.profile_id = None
        self.base_url = "https://api.bufferapp.com/1"
        self.post_history = []
        
        # Try to authenticate
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Buffer API"""
        if not self.access_token:
            logger.warning("⚠️  BUFFER_ACCESS_TOKEN not configured in .env")
            logger.info("To enable Buffer posting:")
            logger.info("1. Sign up at https://buffer.com (free tier available)")
            logger.info("2. Go to Buffer Developer: https://buffer.com/app/connections/tokens")
            logger.info("3. Create an access token")
            logger.info("4. Add to .env: BUFFER_ACCESS_TOKEN=your_token")
            return
        
        try:
            # Get user info to verify token
            url = f"{self.base_url}/user.json"
            params = {"access_token": self.access_token}
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"✅ Buffer authenticated: {user_data.get('name', 'User')}")
                
                # Get LinkedIn profile ID
                if user_data.get('profiles'):
                    for profile in user_data['profiles']:
                        if profile.get('service') == 'linkedin':
                            self.profile_id = profile.get('id')
                            logger.info(f"✅ Found LinkedIn profile: {profile.get('formatted_username')}")
                            self.is_authenticated = True
                            return
                
                if not self.is_authenticated:
                    logger.warning("⚠️  No LinkedIn profile found in Buffer account")
                    logger.info("Connect your LinkedIn profile at https://buffer.com/app/connections")
            else:
                logger.error(f"❌ Buffer authentication failed: {response.status_code}")
                logger.error(f"Response: {response.text[:200]}")
        
        except Exception as e:
            logger.error(f"❌ Could not authenticate with Buffer: {e}")
    
    async def post_content(self, content: Dict[str, Any], schedule_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Post content to LinkedIn via Buffer"""
        
        if not self.is_authenticated or not self.profile_id:
            return {
                "status": "error",
                "message": "Buffer not authenticated or no LinkedIn profile"
            }
        
        try:
            # Build post text with hashtags
            text = content.get("text", "")
            hashtags = content.get("hashtags", [])
            if hashtags:
                text += "\n\n" + " ".join([f"#{tag}" for tag in hashtags])
            
            # Prepare post data
            post_data = {
                "profile_ids": [self.profile_id],
                "text": text,
                "access_token": self.access_token
            }
            
            # Add schedule time if provided
            if schedule_time:
                # Convert to UTC timestamp
                timestamp = int(schedule_time.timestamp())
                post_data["scheduled_at"] = timestamp
                logger.info(f"📅 Scheduling post for: {schedule_time.isoformat()}")
            else:
                logger.info("📤 Posting immediately")
            
            # Send to Buffer
            url = f"{self.base_url}/updates/create.json"
            response = requests.post(url, json=post_data, timeout=10)
            
            if response.status_code in [200, 201]:
                result = response.json()
                post_id = result.get('id', f"buffer_{int(datetime.utcnow().timestamp())}")
                
                post_record = {
                    "status": "success",
                    "post_id": post_id,
                    "message": "✅ Posted to Buffer/LinkedIn!",
                    "posted_at": datetime.utcnow().isoformat(),
                    "content_preview": content.get("text", "")[:100],
                    "scheduled": schedule_time is not None
                }
                
                self.post_history.append(post_record)
                logger.info(f"✅ Posted via Buffer: {content.get('text', '')[:50]}...")
                
                return post_record
            else:
                logger.error(f"❌ Buffer post failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return {
                    "status": "error",
                    "message": f"Buffer API error: {response.status_code}"
                }
        
        except Exception as e:
            logger.error(f"❌ Error posting to Buffer: {e}")
            return {
                "status": "error",
                "message": f"Failed to post: {str(e)}"
            }
    
    async def post_batch(self, contents: List[Dict[str, Any]], spacing_hours: int = 24) -> Dict[str, Any]:
        """Post multiple contents with automatic scheduling"""
        
        logger.info(f"📅 Scheduling {len(contents)} posts via Buffer...")
        
        results = {
            "total_posts": len(contents),
            "posts": [],
            "schedule": [],
            "status": "scheduled"
        }
        
        now = datetime.utcnow()
        
        for i, content in enumerate(contents):
            # Calculate schedule time
            schedule_time = now + timedelta(hours=spacing_hours * (i + 1))
            
            logger.info(f"📍 Processing post {i+1} of {len(contents)}...")
            
            # Post with scheduled time
            post_result = await self.post_content(content, schedule_time=schedule_time)
            results["posts"].append(post_result)
            
            # Add to schedule
            results["schedule"].append({
                "post_number": i + 1,
                "scheduled_time": schedule_time.isoformat(),
                "content_preview": content.get("text", "")[:100],
                "result": post_result
            })
        
        logger.info(f"✅ All {len(contents)} posts scheduled!")
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get Buffer account status"""
        return {
            "authenticated": self.is_authenticated,
            "profile_id": self.profile_id,
            "posts_scheduled": len(self.post_history),
            "service": "Buffer"
        }


# Global service instance
buffer_linkedin_service = BufferLinkedInService()
