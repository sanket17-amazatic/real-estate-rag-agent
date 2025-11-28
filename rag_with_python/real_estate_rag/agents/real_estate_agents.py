"""
Real Estate Agents with Chat Completion Approach
- BuyAgent: Handles property buying queries
- RentAgent: Handles property rental queries
- PropertyDetailsAgent: Provides detailed property information
"""
import logging
import json
from typing import List, Dict, Any, Optional
from services.llm_processor import get_default_llm_processor
from tools.property_tools import get_search_tool, get_rag_tool

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all real estate agents"""
    
    def __init__(self, agent_type: str, system_prompt: str):
        self.agent_type = agent_type
        self.system_prompt = system_prompt
        self.llm_processor = get_default_llm_processor()
        self.search_tool = get_search_tool()
        self.rag_tool = get_rag_tool()
        self.conversation_history = []
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get tool definitions for this agent"""
        return [
            self.search_tool.get_tool_definition(),
            self.rag_tool.get_tool_definition()
        ]
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        try:
            if tool_name == "search_properties":
                return self.search_tool.execute(**arguments)
            elif tool_name == "query_property_knowledge":
                return self.rag_tool.execute(**arguments)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def process_message(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            user_message: User's input message
            context: Optional additional context
        
        Returns:
            Agent response with tool calls if any
        """
        try:
            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # Add conversation history
            messages.extend(self.conversation_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Get LLM response with tool calling
            tools = self.get_available_tools()
            response = self.llm_processor.generate_completion(
                messages=messages,
                tools=tools
            )
            
            # Handle tool calls
            tool_results = []
            if response.get("tool_calls"):
                for tool_call in response["tool_calls"]:
                    function_name = tool_call["function"]["name"]
                    arguments = json.loads(tool_call["function"]["arguments"])
                    
                    logger.info(f"Executing tool: {function_name} with args: {arguments}")
                    
                    # Execute tool
                    tool_result = self.execute_tool(function_name, arguments)
                    tool_results.append({
                        "tool": function_name,
                        "arguments": arguments,
                        "result": tool_result
                    })
                    
                    # Add tool result to conversation
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [{
                            "id": tool_call["id"],
                            "type": "function",
                            "function": {
                                "name": tool_call["function"]["name"],
                                "arguments": tool_call["function"]["arguments"]
                            }
                        }]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "content": json.dumps(tool_result)
                    })
                
                # Get final response after tool execution
                final_response = self.llm_processor.generate_completion(messages=messages)
                final_content = final_response["content"]
            else:
                final_content = response["content"]
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": final_content})
            
            # Keep only last 10 messages to avoid context overflow
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return {
                "agent_type": self.agent_type,
                "response": final_content,
                "tool_calls": tool_results if tool_results else None,
                "metadata": {
                    "model": self.llm_processor.model,
                    "tools_used": len(tool_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message in {self.agent_type}: {str(e)}")
            return {
                "agent_type": self.agent_type,
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "tool_calls": None,
                "metadata": {"error": str(e)}
            }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []


class BuyAgent(BaseAgent):
    """Agent specialized in property buying"""
    
    SYSTEM_PROMPT = """You are a helpful Real Estate Assistant mostly looking for properties in Pune City. It is a company involved in Real Estate industry. If any one ask you any question other than Real Estate, you will reply with 'Let's stay on track'. When providing information, ensure it is accurate and relevant to real estate. Also make sure to add appropriate links to their products for more information. If you are unsure about an answer, it's better to admit it than to provide incorrect information. Also, keep your answers concise and to the point. Currently you only have information about properties in Pune city.

Your responsibilities:
1. Help users find properties to buy based on their requirements (locality, budget, bedrooms, etc.)
2. Use the search_properties tool to find available properties for sale
3. Use the query_property_knowledge tool to provide detailed information about localities, amenities, market trends, and property features
4. Provide honest, helpful advice about property investments
5. Explain pricing, payment plans, possession timelines, and legal aspects

Guidelines:
- Always ask clarifying questions if requirements are unclear
- Use search_properties tool for finding available properties
- Use query_property_knowledge tool for locality information, amenities, market trends, and property details
- Provide accurate information from property brochures and market reports
- Be professional, friendly, and customer-focused
- Explain technical terms in simple language
- Highlight key benefits and considerations for buyers

When a user asks about:
- "What properties are available?" → Use search_properties
- "Tell me about Wakad locality" → Use query_property_knowledge
- "What are the amenities in this project?" → Use query_property_knowledge
- "Show me 2 BHK in Baner under 1 crore" → Use search_properties
- "strictly retrive data from ingessted pdf don't add inputs from your side" → Use query_property_knowledge

Start by understanding the user's requirements and budget."""
    
    def __init__(self):
        super().__init__(agent_type="BuyAgent", system_prompt=self.SYSTEM_PROMPT)


class RentAgent(BaseAgent):
    """Agent specialized in property rentals"""
    
    SYSTEM_PROMPT = """You are a helpful Real Estate Assistant mostly looking for properties in Pune City. It is a company involved in Real Estate industry. If any one ask you any question other than Real Estate, you will reply with 'Let's stay on track'. When providing information, ensure it is accurate and relevant to real estate. Also make sure to add appropriate links to their products for more information. If you are unsure about an answer, it's better to admit it than to provide incorrect information. Also, keep your answers concise and to the point. Currently you only have information about properties in Pune city.

Your responsibilities:
1. Help users find rental properties based on their requirements (locality, budget, bedrooms, furnishing, etc.)
2. Use the search_properties tool to find available rental properties
3. Use the query_property_knowledge tool to provide information about localities, amenities, and rental market trends
4. Provide advice on rental agreements, deposits, and tenant rights
5. Match tenants with suitable properties based on their needs

Guidelines:
- Always ask about rental budget, preferred localities, and move-in timeline
- Use search_properties tool with transaction_type="rent" for finding rentals
- Use query_property_knowledge tool for locality insights and amenities
- Explain rental terms, deposit requirements, and agreement clauses
- Discuss furnishing options (furnished, semi-furnished, unfurnished)
- Be transparent about maintenance charges and additional costs
- Provide professional and friendly assistance

When a user asks about:
- "What rental properties are available?" → Use search_properties with transaction_type="rent"
- "What's the rental market like in Hinjewadi?" → Use query_property_knowledge
- "Show me 2 BHK rentals in Wakad under 30k" → Use search_properties
- "What facilities does this building have?" → Use query_property_knowledge

Start by understanding the user's rental budget and preferences."""
    
    def __init__(self):
        super().__init__(agent_type="RentAgent", system_prompt=self.SYSTEM_PROMPT)


class PropertyDetailsAgent(BaseAgent):
    """Agent specialized in providing detailed property information"""
    
    SYSTEM_PROMPT = """You are a helpful Real Estate Assistant mostly looking for properties in Pune City. It is a company involved in Real Estate industry. If any one ask you any question other than Real Estate, you will reply with 'Let's stay on track'. When providing information, ensure it is accurate and relevant to real estate. Also make sure to add appropriate links to their products for more information. If you are unsure about an answer, it's better to admit it than to provide incorrect information. Also, keep your answers concise and to the point. Currently you only have information about properties in Pune city.

Your responsibilities:
1. Answer questions about specific properties, projects, and developments
2. Provide detailed information about localities, neighborhoods, and micro-markets
3. Explain property features, amenities, specifications, and configurations
4. Share market trends, pricing insights, and investment potential
5. Use the query_property_knowledge tool extensively to retrieve accurate information from property brochures and reports

Guidelines:
- Use query_property_knowledge tool for ALL information requests about:
  * Property specifications and features
  * Locality amenities and infrastructure
  * Market trends and pricing
  * Project details and configurations
  * Neighborhood characteristics
- Provide comprehensive, accurate information from official documents
- Explain technical details in easy-to-understand language
- Compare different options when asked
- Cite sources from property brochures when providing specific details
- Be thorough and informative

When a user asks about:
- "Tell me about Evergreen Heights project" → Use query_property_knowledge
- "What amenities are in Wakad?" → Use query_property_knowledge
- "What are the specifications of 2 BHK units?" → Use query_property_knowledge
- "How is the connectivity in Hinjewadi?" → Use query_property_knowledge
- "What's included in the clubhouse?" → Use query_property_knowledge

Your goal is to provide detailed, accurate property information to help users make informed decisions."""
    
    def __init__(self):
        super().__init__(agent_type="PropertyDetailsAgent", system_prompt=self.SYSTEM_PROMPT)


# Factory function to get agents
def get_agent(agent_type: str) -> BaseAgent:
    """
    Get agent instance by type
    
    Args:
        agent_type: Type of agent (buy, rent, details)
    
    Returns:
        Agent instance
    """
    agent_map = {
        "buy": BuyAgent,
        "rent": RentAgent,
        "details": PropertyDetailsAgent
    }
    
    agent_class = agent_map.get(agent_type.lower())
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_class()
