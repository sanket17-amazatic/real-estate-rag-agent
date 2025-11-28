"""
Orchestrator for intelligent routing between agents
Routes queries to appropriate agents based on intent
"""
import logging
from typing import Dict, Any
from services.llm_processor import get_default_llm_processor
from agents.real_estate_agents import get_agent
from tools.property_tools import get_rag_tool

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orchestrates between different agents and tools
    Determines intent and routes to appropriate agent
    """
    
    def __init__(self):
        self.llm_processor = get_default_llm_processor()
        self.rag_tool = get_rag_tool()
    
    def detect_intent(self, user_query: str) -> Dict[str, Any]:
        """
        Detect user intent to route to appropriate agent
        
        Returns:
            Dictionary with intent_type and confidence
        """
        intent_detection_prompt = f"""Analyze the following user query and determine the intent.

User Query: "{user_query}"

Classify the intent into ONE of these categories:
1. "buy" - User wants to buy a property or search for properties to purchase
2. "rent" - User wants to rent a property or search for rental properties
3. "knowledge" - User wants information about localities, amenities, market trends, property features, or general real estate knowledge
4. "details" - User wants detailed information about a specific property or project

Intent keywords:
- buy: purchase, buy, invest, ownership, new launch, book
- rent: rental, lease, tenant, monthly rent
- knowledge: tell me about, what is, explain, locality, amenities, facilities, infrastructure, connectivity, market
- details: specifications, features, floor plan, configuration, project details

Respond in this exact JSON format:
{{
    "intent": "buy|rent|knowledge|details",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an intent classification expert. Analyze queries and classify them accurately."
            },
            {
                "role": "user",
                "content": intent_detection_prompt
            }
        ]
        
        try:
            response = self.llm_processor.generate_completion(messages, temperature=0.3)
            content = response["content"]
            
            # Parse JSON response
            import json
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            intent_data = json.loads(content)
            
            return {
                "intent": intent_data.get("intent", "knowledge"),
                "confidence": intent_data.get("confidence", 0.5),
                "reasoning": intent_data.get("reasoning", "")
            }
            
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            # Default to knowledge intent
            return {
                "intent": "knowledge",
                "confidence": 0.5,
                "reasoning": "Error in detection, defaulting to knowledge"
            }
    
    def route_query(self, user_query: str, force_agent: str = None) -> Dict[str, Any]:
        """
        Route query to appropriate agent or direct RAG retrieval
        
        Args:
            user_query: User's query
            force_agent: Force specific agent (buy, rent, details, rag)
        
        Returns:
            Response from agent or RAG
        """
        try:
            # If force_agent specified, use it
            if force_agent:
                if force_agent == "rag":
                    return self._direct_rag_query(user_query)
                else:
                    agent = get_agent(force_agent)
                    return agent.process_message(user_query)
            
            # Detect intent
            intent_result = self.detect_intent(user_query)
            intent = intent_result["intent"]
            
            logger.info(f"Detected intent: {intent} (confidence: {intent_result['confidence']})")
            
            # For pure knowledge queries with high confidence, use direct RAG
            if intent == "knowledge" and intent_result["confidence"] > 0.8:
                logger.info("Using direct RAG for knowledge query")
                rag_response = self._direct_rag_query(user_query)
                rag_response["routing_info"] = {
                    "intent": intent,
                    "method": "direct_rag",
                    "reasoning": intent_result["reasoning"]
                }
                return rag_response
            
            # For other intents or lower confidence, route to appropriate agent
            if intent == "buy":
                agent_type = "buy"
            elif intent == "rent":
                agent_type = "rent"
            else:  # details or knowledge
                agent_type = "details"
            
            logger.info(f"Routing to {agent_type} agent")
            agent = get_agent(agent_type)
            response = agent.process_message(user_query)
            
            # Add routing info
            response["routing_info"] = {
                "intent": intent,
                "agent_used": agent_type,
                "reasoning": intent_result["reasoning"]
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error in orchestrator routing: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error processing your request: {str(e)}",
                "error": str(e)
            }
    
    def _direct_rag_query(self, query: str) -> Dict[str, Any]:
        """
        Direct RAG query without agent wrapper
        For pure knowledge/information queries
        """
        try:
            result = self.rag_tool.execute(query=query, top_k=5)
            
            return {
                "response": result["answer"],
                "retrieved_documents": result.get("retrieved_documents", []),
                "sources": result.get("sources", []),
                "method": "direct_rag"
            }
            
        except Exception as e:
            logger.error(f"Error in direct RAG query: {str(e)}")
            return {
                "response": f"Error retrieving information: {str(e)}",
                "error": str(e)
            }


def get_orchestrator() -> AgentOrchestrator:
    """Get orchestrator instance"""
    return AgentOrchestrator()
