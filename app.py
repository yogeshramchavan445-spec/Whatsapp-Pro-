# ================================
# INSERT THIS CODE IN YOUR MAIN APPLICATION FILE
# (e.g., app.py, main.py, or server.py)
# ================================

import os
import json
import requests
from typing import List, Dict, Optional

class GPTAPIKeyManager:
    def __init__(self, api_keys: List[str]):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.failed_keys = set()
    
    def get_current_key(self) -> Optional[str]:
        """Get the current active API key"""
        if not self.api_keys:
            return None
        
        # If current key is failed, try to find next available key
        while (self.current_key_index < len(self.api_keys) and 
               self.api_keys[self.current_key_index] in self.failed_keys):
            self.current_key_index += 1
        
        if self.current_key_index >= len(self.api_keys):
            return None
        
        return self.api_keys[self.current_key_index]
    
    def mark_key_failed(self, key: str):
        """Mark an API key as failed/quota exceeded"""
        self.failed_keys.add(key)
        
        # If current key failed, move to next
        if (self.current_key_index < len(self.api_keys) and 
            self.api_keys[self.current_key_index] == key):
            self.current_key_index += 1
    
    def get_available_keys_count(self) -> int:
        """Get number of available API keys"""
        return len([key for key in self.api_keys if key not in self.failed_keys])

class GPTChatManager:
    def __init__(self, api_keys: List[str]):
        self.key_manager = GPTAPIKeyManager(api_keys)
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    def send_message(self, message: str, model: str = "gpt-3.5-turbo", max_tokens: int = 1000) -> Dict:
        """
        Send message to GPT API with automatic key rotation
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": message}],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        max_retries = self.key_manager.get_available_keys_count()
        
        for attempt in range(max_retries):
            current_key = self.key_manager.get_current_key()
            if not current_key:
                raise Exception("No available API keys")
            
            headers["Authorization"] = f"Bearer {current_key}"
            
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    print(f"API key quota exceeded for key {current_key[:10]}...")
                    self.key_manager.mark_key_failed(current_key)
                    continue
                elif response.status_code == 401:  # Invalid key
                    print(f"Invalid API key: {current_key[:10]}...")
                    self.key_manager.mark_key_failed(current_key)
                    continue
                else:
                    print(f"API error (status {response.status_code}) for key {current_key[:10]}...")
                    # Don't mark as failed for other errors, try next key
                    self.key_manager.mark_key_failed(current_key)
                    continue
                    
            except requests.exceptions.RequestException as e:
                print(f"Request failed for key {current_key[:10]}...: {str(e)}")
                self.key_manager.mark_key_failed(current_key)
                continue
        
        raise Exception("All API keys exhausted or failed")

# ================================
# CONFIGURE YOUR 20 API KEYS HERE
# ================================

# Option 1: Load from environment variables (Recommended for security)
API_KEYS = [
    os.getenv('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'),
    os.getenv('OPENAI_API_KEY_2'),
    os.getenv('OPENAI_API_KEY_3'),
    os.getenv('OPENAI_API_KEY_4'),
    os.getenv('OPENAI_API_KEY_5'),
    os.getenv('OPENAI_API_KEY_6'),
    os.getenv('OPENAI_API_KEY_7'),
    os.getenv('OPENAI_API_KEY_8'),
    os.getenv('OPENAI_API_KEY_9'),
    os.getenv('OPENAI_API_KEY_10'),
    os.getenv('OPENAI_API_KEY_11'),
    os.getenv('OPENAI_API_KEY_12'),
    os.getenv('OPENAI_API_KEY_13'),
    os.getenv('OPENAI_API_KEY_14'),
    os.getenv('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'),
    os.getenv('OPENAI_API_KEY_16'),
    os.getenv('OPENAI_API_KEY_17'),
    os.getenv('OPENAI_API_KEY_18'),
    os.getenv('OPENAI_API_KEY_19'),
    os.getenv('OPENAI_API_KEY_20')
]

# Filter out None values (if some environment variables are not set)
API_KEYS = [key for key in API_KEYS if key is not None]

# Option 2: Directly add keys (Less secure - only for testing)
# API_KEYS = [
#     "sk-your-first-api-key-here",
#     "sk-your-second-api-key-here",
#     # ... add all 20 keys
# ]

# ================================
# INITIALIZE GPT CHAT MANAGER
# ================================
gpt_manager = GPTChatManager(API_KEYS)

# ================================
# AUTO-RESPONDER WEB APP CODE
# INSERT THE ABOVE CODE BEFORE THIS SECTION
# ================================

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# HTML template for the web interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>GPT Auto-Responder</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .chat-box { border: 1px solid #ccc; padding: 20px; height: 400px; overflow-y: scroll; margin-bottom: 20px; }
        .message { margin-bottom: 10px; padding: 10px; border-radius: 5px; }
        .user { background-color: #e3f2fd; }
        .bot { background-color: #f3e5f5; }
        input, button { padding: 10px; margin: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>GPT Auto-Responder</h1>
        <div class="chat-box" id="chatBox">
            <div class="message bot">Hello! How can I help you today?</div>
        </div>
        <input type="text" id="messageInput" placeholder="Type your message..." style="width: 70%;">
        <button onclick="sendMessage()">Send</button>
        <div id="status">Available API Keys: {{ available_keys }}</div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message to chat
            const chatBox = document.getElementById('chatBox');
            const userMessage = document.createElement('div');
            userMessage.className = 'message user';
            userMessage.textContent = 'You: ' + message;
            chatBox.appendChild(userMessage);
            
            // Clear input
            input.value = '';
            
            // Send to server
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const botMessage = document.createElement('div');
                    botMessage.className = 'message bot';
                    botMessage.textContent = 'Bot: ' + data.response;
                    chatBox.appendChild(botMessage);
                    
                    // Update status
                    document.getElementById('status').textContent = 
                        'Available API Keys: ' + data.available_keys;
                } else {
                    alert('Error: ' + data.error);
                }
                
                // Scroll to bottom
                chatBox.scrollTop = chatBox.scrollHeight;
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        }
        
        // Allow sending message with Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, available_keys=gpt_manager.key_manager.get_available_keys_count())

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'success': False, 'error': 'Empty message'})
        
        # Get response from GPT
        gpt_response = gpt_manager.send_message(user_message)
        
        # Extract the response text
        response_text = gpt_response['choices'][0]['message']['content']
        
        return jsonify({
            'success': True,
            'response': response_text,
            'available_keys': gpt_manager.key_manager.get_available_keys_count()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'available_keys': gpt_manager.key_manager.get_available_keys_count()
        })

# ================================
# SERVER CONFIGURATION FOR RENDER
# ================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
