#!/usr/bin/env python3
"""
Generate mock Claude conversation data for testing the analyzer
"""

import json
from datetime import datetime, timedelta
import random

def generate_mock_export(num_conversations=10, messages_per_conv=15):
    """Generate mock Claude export data"""
    
    conversations = []
    
    topics = [
        "Help me debug this Python code",
        "Build a BlaqVox feature",
        "VA healthcare advocacy letter",
        "Ubuntu philosophy discussion",
        "Docker container optimization",
        "Generate AI art prompt",
        "Freestyle rap about Seattle",
        "Design system architecture",
        "Personal advice needed"
    ]
    
    user_messages = [
        "Can you help me with this?",
        "That's not quite right",
        "Perfect, thanks!",
        "This is urgent - need help now",
        "Let me clarify what I meant",
        "You're hallucinating - I didn't say that",
        "Too formal, just talk normally",
        "Wrong tool - you should have searched",
        "Excellent work, exactly what I needed",
        "Lost context again from earlier"
    ]
    
    assistant_messages = [
        "Here's what I found after searching...",
        "Let me build that for you:\n```python\ncode here\n```",
        "I understand you need help with...",
        "I apologize, but I cannot assist with that due to safety guidelines...",
        "**IMPORTANT:** Here are the key points:\n- Point 1\n- Point 2",
        "Based on our previous discussion about...",
        "I'll search for that information now.",
        "That's a great question! Let me explain...",
        "I made an error earlier - let me correct that.",
        "Here's the complete analysis..."
    ]
    
    base_time = datetime.now() - timedelta(days=90)
    
    for i in range(num_conversations):
        conv_time = base_time + timedelta(days=random.randint(0, 90))
        
        messages = []
        for j in range(messages_per_conv):
            role = 'user' if j % 2 == 0 else 'assistant'
            msg_time = conv_time + timedelta(minutes=j*2)
            
            if role == 'user':
                content = random.choice(user_messages)
            else:
                content = random.choice(assistant_messages)
            
            messages.append({
                "role": role,
                "text": content,
                "created_at": msg_time.isoformat() + "Z"
            })
        
        conversations.append({
            "id": f"conv-{i:04d}",
            "name": random.choice(topics),
            "created_at": conv_time.isoformat() + "Z",
            "updated_at": (conv_time + timedelta(minutes=messages_per_conv*2)).isoformat() + "Z",
            "model": random.choice(["claude-sonnet-4", "claude-sonnet-4.5", "claude-opus-4"]),
            "chat_messages": messages
        })
    
    return {"conversations": conversations}


if __name__ == '__main__':
    print("Generating mock Claude export data...")
    
    mock_data = generate_mock_export(num_conversations=20, messages_per_conv=10)
    
    output_file = "mock_claude_export.json"
    with open(output_file, 'w') as f:
        json.dump(mock_data, f, indent=2)
    
    print(f"✓ Generated {len(mock_data['conversations'])} conversations")
    print(f"✓ Saved to: {output_file}")
    print(f"\nTest the analyzer with:")
    print(f"  python claude_conversation_analyzer.py {output_file}")
