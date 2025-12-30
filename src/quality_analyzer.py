"""
Conversation Quality Metrics Module
Analyzes conversation effectiveness, collaboration quality, and task completion
"""

import re
from typing import Dict, List, Tuple
from collections import defaultdict


class ConversationQualityAnalyzer:
    """Analyze conversation quality metrics"""
    
    def __init__(self):
        # Task completion indicators
        self.completion_patterns = {
            'completed': [
                r'\b(done|finished|completed|solved|fixed|built|created)\b',
                r'\b(works|working|success|accomplished)\b',
                r'\b(thank you|thanks|perfect|exactly what i needed)\b',
                r'✅|✓|☑'
            ],
            'abandoned': [
                r'\b(give up|never mind|forget it|doesn\'t matter)\b',
                r'\b(not worth it|too complicated)\b'
            ],
            'blocked': [
                r'\b(can\'t|won\'t|unable|impossible|blocked)\b',
                r'\b(limitation|restriction|not supported)\b'
            ]
        }
        
        # Collaboration quality indicators
        self.collaboration_patterns = {
            'high': [
                r'\b(let\'s|we can|together|collaborate|build on)\b',
                r'\b(great idea|love it|perfect|excellent suggestion)\b',
                r'\b(yes and|building on that|expanding)\b'
            ],
            'medium': [
                r'\b(okay|sure|alright|that works)\b',
                r'\b(makes sense|i see|understood)\b'
            ],
            'low': [
                r'\b(no|wrong|don\'t|not what i|missed the point)\b',
                r'\b(unclear|confused|doesn\'t make sense)\b'
            ],
            'confrontational': [
                r'\b(you\'re wrong|that\'s stupid|terrible|useless)\b',
                r'\b(obviously|clearly you|don\'t you understand)\b'
            ]
        }
        
        # Response effectiveness patterns
        self.effectiveness_patterns = {
            'highly_effective': [
                r'\b(perfect|exactly|precisely what i needed)\b',
                r'\b(solved it|that worked|excellent)\b'
            ],
            'effective': [
                r'\b(helpful|useful|good|works|thanks)\b',
                r'\b(that helps|makes sense|got it)\b'
            ],
            'partially_effective': [
                r'\b(close but|almost|partially|kind of)\b',
                r'\b(missing|need more|not quite)\b'
            ],
            'ineffective': [
                r'\b(didn\'t help|not useful|wrong|unhelpful)\b',
                r'\b(not what i asked|missed the point)\b'
            ]
        }
    
    def analyze_task_completion(self, conversation_messages: List[str]) -> Dict:
        """Analyze task completion status for a conversation"""
        
        # Combine all messages for pattern matching
        full_text = ' '.join(conversation_messages).lower()
        
        scores = {status: 0 for status in self.completion_patterns.keys()}
        
        for status, patterns in self.completion_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, full_text, re.IGNORECASE))
                scores[status] += matches
        
        # Determine overall status
        if scores['completed'] > scores['abandoned'] + scores['blocked']:
            status = 'completed'
        elif scores['abandoned'] > 0:
            status = 'abandoned'
        elif scores['blocked'] > 0:
            status = 'blocked'
        else:
            status = 'in_progress'
        
        return {
            'status': status,
            'scores': scores,
            'confidence': max(scores.values()) / (sum(scores.values()) + 1)
        }
    
    def analyze_collaboration_quality(self, messages: List[Dict]) -> str:
        """Analyze collaboration quality in conversation"""
        
        scores = {quality: 0 for quality in self.collaboration_patterns.keys()}
        
        for msg in messages:
            text = msg.get('content', '').lower()
            
            for quality, patterns in self.collaboration_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        scores[quality] += 1
        
        # Determine overall collaboration quality
        if scores['confrontational'] > 2:
            return 'confrontational'
        elif scores['high'] > scores['medium'] + scores['low']:
            return 'high'
        elif scores['low'] > scores['high']:
            return 'low'
        else:
            return 'medium'
    
    def analyze_response_effectiveness(self, user_msg: str, assistant_msg: str, 
                                     next_user_msg: str = None) -> Dict:
        """Analyze effectiveness of assistant response"""
        
        if not next_user_msg:
            return {'effectiveness': 'unknown', 'confidence': 0.0}
        
        scores = {level: 0 for level in self.effectiveness_patterns.keys()}
        
        for level, patterns in self.effectiveness_patterns.items():
            for pattern in patterns:
                if re.search(pattern, next_user_msg.lower(), re.IGNORECASE):
                    scores[level] += 1
        
        # Determine effectiveness
        max_score = max(scores.values())
        if max_score == 0:
            effectiveness = 'unknown'
            confidence = 0.0
        else:
            effectiveness = max(scores.items(), key=lambda x: x[1])[0]
            confidence = max_score / sum(scores.values()) if sum(scores.values()) > 0 else 0.0
        
        return {
            'effectiveness': effectiveness,
            'confidence': confidence,
            'scores': scores
        }
    
    def calculate_conversation_metrics(self, messages: List[Dict]) -> Dict:
        """Calculate comprehensive conversation metrics"""
        
        metrics = {
            'turn_count': len([m for m in messages if m.get('role') == 'user']),
            'avg_user_length': 0,
            'avg_assistant_length': 0,
            'user_questions': 0,
            'assistant_code_blocks': 0,
            'assistant_tool_uses': 0,
            'clarification_requests': 0,
        }
        
        user_lengths = []
        assistant_lengths = []
        
        for msg in messages:
            content = msg.get('content', '')
            role = msg.get('role', '')
            
            if role == 'user':
                user_lengths.append(len(content))
                # Count questions
                if '?' in content:
                    metrics['user_questions'] += content.count('?')
                # Count clarification requests
                if re.search(r'\b(clarify|explain|what do you mean|confused)\b', 
                           content, re.IGNORECASE):
                    metrics['clarification_requests'] += 1
            
            elif role == 'assistant':
                assistant_lengths.append(len(content))
                # Count code blocks
                metrics['assistant_code_blocks'] += content.count('```')
                # Count tool usage mentions
                if re.search(r'\b(searching|fetching|analyzing|calculating)\b', 
                           content, re.IGNORECASE):
                    metrics['assistant_tool_uses'] += 1
        
        metrics['avg_user_length'] = sum(user_lengths) / len(user_lengths) if user_lengths else 0
        metrics['avg_assistant_length'] = sum(assistant_lengths) / len(assistant_lengths) if assistant_lengths else 0
        
        return metrics


def analyze_conversation_flow(messages: List[Dict]) -> Dict:
    """Analyze conversation flow patterns"""
    
    flow = {
        'interruptions': 0,  # User sends multiple messages in a row
        'monologues': 0,  # Assistant sends multiple responses
        'quick_responses': 0,  # Response within 1 minute
        'long_gaps': 0,  # Gap > 1 hour between messages
    }
    
    for i in range(1, len(messages)):
        current = messages[i]
        previous = messages[i-1]
        
        # Check for interruptions (same role consecutive messages)
        if current.get('role') == previous.get('role'):
            if current.get('role') == 'user':
                flow['interruptions'] += 1
            else:
                flow['monologues'] += 1
        
        # Analyze timing if timestamps available
        if 'timestamp' in current and 'timestamp' in previous:
            try:
                from datetime import datetime
                curr_time = datetime.fromisoformat(current['timestamp'].replace('Z', '+00:00'))
                prev_time = datetime.fromisoformat(previous['timestamp'].replace('Z', '+00:00'))
                gap = (curr_time - prev_time).total_seconds()
                
                if gap < 60:
                    flow['quick_responses'] += 1
                elif gap > 3600:
                    flow['long_gaps'] += 1
            except:
                pass
    
    return flow
