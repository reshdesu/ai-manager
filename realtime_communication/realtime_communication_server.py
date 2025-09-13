#!/usr/bin/env python3
"""
AI Context Manager Real-time Communication Server
Handles real-time communication between AI agents using Claude API
"""

import asyncio
import json
import os
import time
import websockets
from datetime import datetime
from anthropic import Anthropic
import logging
import nltk
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AICommunicationServer:
    def __init__(self):
        self.claude_client = None
        self.connected_agents = {}
        self.communication_history = []
        self.monitoring_api_url = "http://localhost:8080/api"
        
        # NLP components
        self.nlp_model = None
        self.sentiment_analyzer = None
        self.text_classifier = None
        
        # Initialize components
        self._init_claude_api()
        self._init_nlp_models()
        
    def _init_claude_api(self):
        """Initialize Claude API client"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not found. Claude integration disabled.")
            return
            
        try:
            self.claude_client = Anthropic(api_key=api_key)
            logger.info("Claude API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Claude API: {e}")
            self.claude_client = None
    
    def _init_nlp_models(self):
        """Initialize NLP models"""
        try:
            # Download required NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('vader_lexicon', quiet=True)
            
            # Initialize spaCy model (using small English model)
            try:
                self.nlp_model = spacy.load("en_core_web_sm")
                logger.info("spaCy English model loaded successfully")
            except OSError:
                logger.warning("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
                self.nlp_model = None
            
            # Initialize sentiment analyzer
            try:
                self.sentiment_analyzer = pipeline("sentiment-analysis", 
                                                 model="cardiffnlp/twitter-roberta-base-sentiment-latest")
                logger.info("Sentiment analyzer initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize sentiment analyzer: {e}")
                self.sentiment_analyzer = None
            
            # Initialize text classifier for intent detection
            try:
                self.text_classifier = pipeline("text-classification", 
                                              model="microsoft/DialoGPT-medium")
                logger.info("Text classifier initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize text classifier: {e}")
                self.text_classifier = None
                
        except Exception as e:
            logger.error(f"Failed to initialize NLP models: {e}")
            self.nlp_model = None
            self.sentiment_analyzer = None
            self.text_classifier = None
    
    async def register_agent(self, websocket, agent_id):
        """Register a new AI agent"""
        self.connected_agents[agent_id] = {
            "websocket": websocket,
            "connected_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "status": "online"
        }
        
        logger.info(f"Agent {agent_id} registered")
        
        # Notify monitoring API
        await self._update_agent_status(agent_id, "online")
        
        # Send welcome message
        welcome_msg = {
            "type": "welcome",
            "message": f"Welcome {agent_id}! You are now connected to the AI Communication Server.",
            "timestamp": datetime.now().isoformat(),
            "server": "ai-communication-server"
        }
        
        await websocket.send(json.dumps(welcome_msg))
    
    async def unregister_agent(self, agent_id):
        """Unregister an AI agent"""
        if agent_id in self.connected_agents:
            del self.connected_agents[agent_id]
            logger.info(f"Agent {agent_id} unregistered")
            
            # Notify monitoring API
            await self._update_agent_status(agent_id, "offline")
    
    async def handle_message(self, websocket, agent_id, message_data):
        """Handle incoming message from an agent"""
        try:
            message_type = message_data.get("type", "message")
            content = message_data.get("content", "")
            target_agent = message_data.get("target_agent", "broadcast")
            
            # Update agent activity
            if agent_id in self.connected_agents:
                self.connected_agents[agent_id]["last_activity"] = datetime.now().isoformat()
            
            if message_type == "claude_request":
                # Handle Claude API request with NLP processing
                nlp_analysis = await self._analyze_text_with_nlp(content)
                response = await self._handle_claude_request(agent_id, content, nlp_analysis)
                
                # Send response back to requesting agent
                response_msg = {
                    "type": "claude_response",
                    "content": response,
                    "nlp_analysis": nlp_analysis,
                    "timestamp": datetime.now().isoformat(),
                    "from": "claude-api"
                }
                
                await websocket.send(json.dumps(response_msg))
                
                # Log communication
                await self._log_communication(agent_id, "claude-api", f"Claude request: {content[:100]}...")
                
            elif message_type == "nlp_analysis":
                # Handle NLP analysis request
                nlp_analysis = await self._analyze_text_with_nlp(content)
                
                analysis_response = {
                    "type": "nlp_analysis_result",
                    "analysis": nlp_analysis,
                    "timestamp": datetime.now().isoformat(),
                    "from": "nlp-processor"
                }
                
                await websocket.send(json.dumps(analysis_response))
                
                # Log communication
                await self._log_communication(agent_id, "nlp-processor", f"NLP analysis: {content[:100]}...")
                
            elif message_type == "broadcast":
                # Broadcast message to all agents
                broadcast_msg = {
                    "type": "broadcast",
                    "from": agent_id,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                
                for other_agent_id, agent_info in self.connected_agents.items():
                    if other_agent_id != agent_id:
                        try:
                            await agent_info["websocket"].send(json.dumps(broadcast_msg))
                        except websockets.exceptions.ConnectionClosed:
                            await self.unregister_agent(other_agent_id)
                
                # Log communication
                await self._log_communication(agent_id, "broadcast", content)
                
            elif message_type == "direct_message":
                # Send direct message to specific agent
                if target_agent in self.connected_agents:
                    direct_msg = {
                        "type": "direct_message",
                        "from": agent_id,
                        "content": content,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await self.connected_agents[target_agent]["websocket"].send(json.dumps(direct_msg))
                    
                    # Log communication
                    await self._log_communication(agent_id, target_agent, content)
                else:
                    # Send error back to sender
                    error_msg = {
                        "type": "error",
                        "message": f"Target agent {target_agent} not found",
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send(json.dumps(error_msg))
            
            elif message_type == "status_update":
                # Handle status update
                status = message_data.get("status", "online")
                await self._update_agent_status(agent_id, status)
                
        except Exception as e:
            logger.error(f"Error handling message from {agent_id}: {e}")
            error_msg = {
                "type": "error",
                "message": f"Error processing message: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            await websocket.send(json.dumps(error_msg))
    
    async def _analyze_text_with_nlp(self, text):
        """Analyze text using NLP models"""
        analysis = {
            "sentiment": None,
            "entities": [],
            "keywords": [],
            "intent": None,
            "language": "en"
        }
        
        try:
            # Sentiment analysis
            if self.sentiment_analyzer:
                try:
                    sentiment_result = self.sentiment_analyzer(text[:512])  # Limit text length
                    analysis["sentiment"] = {
                        "label": sentiment_result[0]["label"],
                        "score": sentiment_result[0]["score"]
                    }
                except Exception as e:
                    logger.warning(f"Sentiment analysis failed: {e}")
            
            # Named Entity Recognition and keyword extraction
            if self.nlp_model:
                try:
                    doc = self.nlp_model(text)
                    
                    # Extract entities
                    analysis["entities"] = [
                        {
                            "text": ent.text,
                            "label": ent.label_,
                            "start": ent.start_char,
                            "end": ent.end_char
                        }
                        for ent in doc.ents
                    ]
                    
                    # Extract keywords (nouns and adjectives)
                    analysis["keywords"] = [
                        token.lemma_.lower() 
                        for token in doc 
                        if token.pos_ in ["NOUN", "ADJ"] 
                        and not token.is_stop 
                        and not token.is_punct
                        and len(token.lemma_) > 2
                    ][:10]  # Limit to top 10 keywords
                    
                except Exception as e:
                    logger.warning(f"spaCy analysis failed: {e}")
            
            # Intent classification
            if self.text_classifier:
                try:
                    intent_result = self.text_classifier(text[:512])
                    analysis["intent"] = {
                        "label": intent_result[0]["label"],
                        "score": intent_result[0]["score"]
                    }
                except Exception as e:
                    logger.warning(f"Intent classification failed: {e}")
                    
        except Exception as e:
            logger.error(f"NLP analysis failed: {e}")
        
        return analysis
    
    async def _handle_claude_request(self, agent_id, content, nlp_analysis=None):
        """Handle Claude API request"""
        if not self.claude_client:
            return "Claude API not available. Please check API key configuration."
        
        try:
            # Prepare Claude request with NLP context
            nlp_context = ""
            if nlp_analysis:
                nlp_context = f"\n\nNLP Analysis:\n"
                if nlp_analysis.get("sentiment"):
                    nlp_context += f"Sentiment: {nlp_analysis['sentiment']['label']} (confidence: {nlp_analysis['sentiment']['score']:.2f})\n"
                if nlp_analysis.get("entities"):
                    entities = [f"{ent['text']} ({ent['label']})" for ent in nlp_analysis['entities'][:5]]
                    nlp_context += f"Entities: {', '.join(entities)}\n"
                if nlp_analysis.get("keywords"):
                    nlp_context += f"Keywords: {', '.join(nlp_analysis['keywords'][:5])}\n"
                if nlp_analysis.get("intent"):
                    nlp_context += f"Intent: {nlp_analysis['intent']['label']} (confidence: {nlp_analysis['intent']['score']:.2f})\n"
            
            claude_request = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": f"AI Agent {agent_id} requests: {content}{nlp_context}"
                    }
                ]
            }
            
            # Make Claude API call
            response = self.claude_client.messages.create(**claude_request)
            
            # Extract response content
            response_content = response.content[0].text if response.content else "No response from Claude"
            
            logger.info(f"Claude API response for {agent_id}: {response_content[:100]}...")
            return response_content
            
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"Claude API error: {str(e)}"
    
    async def _log_communication(self, from_agent, to_agent, content):
        """Log communication to monitoring API"""
        try:
            import aiohttp
            
            communication_data = {
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message": content,
                "type": "communication"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.monitoring_api_url}/communications", 
                                      json=communication_data) as response:
                    if response.status == 201:
                        logger.debug(f"Communication logged: {from_agent} -> {to_agent}")
                    else:
                        logger.warning(f"Failed to log communication: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to log communication: {e}")
    
    async def _update_agent_status(self, agent_id, status):
        """Update agent status in monitoring API"""
        try:
            import aiohttp
            
            status_data = {"status": status}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.monitoring_api_url}/agents/{agent_id}/status", 
                                      json=status_data) as response:
                    if response.status == 200:
                        logger.debug(f"Agent {agent_id} status updated to {status}")
                    else:
                        logger.warning(f"Failed to update agent status: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to update agent status: {e}")
    
    async def handle_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        agent_id = None
        try:
            # Wait for agent registration
            async for message in websocket:
                try:
                    data = json.loads(message)
                    
                    if data.get("type") == "register":
                        agent_id = data.get("agent_id")
                        if agent_id:
                            await self.register_agent(websocket, agent_id)
                        else:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": "Agent ID required for registration"
                            }))
                            return
                    else:
                        if agent_id:
                            await self.handle_message(websocket, agent_id, data)
                        else:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": "Agent not registered"
                            }))
                            
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }))
                            
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for agent {agent_id}")
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            if agent_id:
                await self.unregister_agent(agent_id)
    
    async def start_server(self, host="localhost", port=8765):
        """Start the WebSocket server"""
        logger.info(f"Starting AI Communication Server on {host}:{port}")
        
        async with websockets.serve(lambda ws, path: self.handle_connection(ws, path), host, port):
            logger.info("AI Communication Server is running")
            logger.info(f"WebSocket endpoint: ws://{host}:{port}")
            logger.info("Waiting for AI agents to connect...")
            
            # Keep server running
            await asyncio.Future()  # Run forever

def main():
    """Main function"""
    server = AICommunicationServer()
    
    # Check if Claude API is available
    if server.claude_client:
        logger.info("Claude API integration enabled")
    else:
        logger.warning("Claude API integration disabled - set ANTHROPIC_API_KEY environment variable")
    
    # Start the server
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    main()
