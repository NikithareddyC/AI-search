"""
Base Agent Class - Foundation for all agents
Agents are autonomous workers that collaborate to complete tasks
"""

from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status"""
    IDLE = "idle"
    THINKING = "thinking"
    EXECUTING = "executing"
    WAITING = "waiting"
    COMPLETE = "complete"
    ERROR = "error"


class Agent(ABC):
    """
    Base Agent class
    Each agent has specific responsibilities and can use tools/functions
    """
    
    def __init__(self, name: str, role: str, description: str):
        self.name = name
        self.role = role
        self.description = description
        self.status = AgentStatus.IDLE
        self.memory = []  # Conversation memory
        self.tools_used = []
        self.last_error = None
        self.created_at = datetime.utcnow()
        
        logger.info(f"✅ Initialized Agent: {name} ({role})")
    
    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the agent's main task"""
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """List tools this agent can use"""
        pass
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Call a tool/function
        Agents don't execute directly - they request tools
        """
        logger.info(f"[{self.name}] Requesting tool: {tool_name}")
        self.tools_used.append({
            "tool": tool_name,
            "timestamp": datetime.utcnow().isoformat(),
            "params": kwargs
        })
        # Actual tool execution happens in the orchestrator
        return await self._execute_tool(tool_name, **kwargs)
    
    async def _execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Override in subclasses to implement tool execution"""
        raise NotImplementedError(f"Tool {tool_name} not implemented")
    
    def add_memory(self, role: str, content: str):
        """Add to conversation memory"""
        self.memory.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_memory(self) -> List[Dict]:
        """Get conversation memory"""
        return self.memory
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory = []
    
    def set_status(self, status: AgentStatus, message: str = ""):
        """Update agent status"""
        self.status = status
        if message:
            logger.info(f"[{self.name}] {status.value}: {message}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status and metadata"""
        return {
            "name": self.name,
            "role": self.role,
            "status": self.status.value,
            "description": self.description,
            "tools_used": len(self.tools_used),
            "memory_size": len(self.memory),
            "last_error": self.last_error,
            "created_at": self.created_at.isoformat()
        }
    
    def handle_error(self, error: Exception):
        """Handle and log errors"""
        self.last_error = str(error)
        self.status = AgentStatus.ERROR
        logger.error(f"[{self.name}] Error: {error}")
    
    def __repr__(self) -> str:
        return f"Agent(name={self.name}, role={self.role}, status={self.status.value})"
