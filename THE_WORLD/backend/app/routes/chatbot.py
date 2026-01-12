"""
THE_WORLD - Chatbot Routes
API endpoints for AI-powered chatbot
"""

from flask import Blueprint, request, jsonify
from app.config import Config
import requests
import json

bp = Blueprint('chatbot', __name__)

# In-memory conversation storage (for development)
# For production, use Redis or database
conversations = {}


@bp.route('/message', methods=['POST'])
def send_message():
    """Send a message to the chatbot and receive a response"""
    try:
        data = request.get_json()
        message = data.get('message')
        conversation_id = data.get('conversation_id', 'default')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message field is required'
            }), 400
        
        # Get or create conversation history
        if conversation_id not in conversations:
            conversations[conversation_id] = []
        
        # Add system context about the application
        system_context = """You are a helpful assistant for THE_WORLD, a WebGIS system for monitoring disasters and Air Quality Index (AQI) data.
        
You can help users:
- Find information about current disaster events
- Get AQI (Air Quality Index) data for cities
- Compare AQI between cities
- Understand correlations between disasters and pollution
- Export/download data

Always provide accurate, helpful information based on the system's capabilities."""

        # Prepare messages for OpenRouter API
        messages = [
            {"role": "system", "content": system_context}
        ]
        
        # Add conversation history (last 10 messages)
        history = conversations[conversation_id][-10:]
        messages.extend(history)
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        # Call OpenRouter API
        openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {Config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",  # Optional
            "X-Title": "THE_WORLD WebGIS"  # Optional
        }
        
        payload = {
            "model": "meta-llama/llama-3.2-3b-instruct:free",  # Free model
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(openrouter_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            return jsonify({
                'success': False,
                'error': 'AI service error',
                'message': response.text
            }), 500
        
        ai_response = response.json()
        assistant_message = ai_response.get('choices', [{}])[0].get('message', {}).get('content', 'I apologize, I could not generate a response.')
        
        # Update conversation history
        conversations[conversation_id].append({"role": "user", "content": message})
        conversations[conversation_id].append({"role": "assistant", "content": assistant_message})
        
        # Generate suggested actions (simplified)
        suggested_actions = []
        message_lower = message.lower()
        
        if 'disaster' in message_lower:
            suggested_actions.append({
                'type': 'view_map',
                'label': 'View disasters on map',
                'url': '/map?filter=disasters'
            })
        
        if 'aqi' in message_lower or 'air quality' in message_lower:
            suggested_actions.append({
                'type': 'view_map',
                'label': 'View AQI data on map',
                'url': '/map?filter=aqi'
            })
        
        return jsonify({
            'success': True,
            'response': assistant_message,
            'conversation_id': conversation_id,
            'suggested_actions': suggested_actions
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id', 'default')
        
        if conversation_id in conversations:
            conversations[conversation_id] = []
        
        return jsonify({
            'success': True,
            'message': 'Conversation cleared'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
