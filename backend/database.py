"""
Database setup and connection pooling
For MVP: Using JSON file storage and Supabase cloud DB
"""
import logging

logger = logging.getLogger(__name__)


def get_db():
    """Dependency to get database session - stub for compatibility"""
    return None


def init_db():
    """Initialize database - using Supabase (cloud) and JSON files"""
    try:
        logger.info("✅ Using Supabase cloud database + JSON storage for MVP")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


def drop_all_tables():
    """Drop all tables (for testing/cleanup)"""
    logger.warning("⚠️  Dropping tables not needed for MVP - using JSON storage")
