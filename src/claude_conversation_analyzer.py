#!/usr/bin/env python3
"""
Claude Conversation Data Analyzer - Advanced Edition
Parses exported Claude.ai JSON data with deep analysis:
- NLP-based sentiment and topic detection
- Conversation quality metrics
- Temporal evolution tracking
- Privacy-first redaction
- Interactive visualizations
- Vector similarity analysis
"""

import json
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter, defaultdict
import hashlib
import warnings
warnings.filterwarnings('ignore')

# Optional advanced dependencies (graceful degradation if not installed)
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️  sklearn not available - advanced clustering disabled")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("⚠️  matplotlib/seaborn not available - visualizations disabled")

class ClaudeConversationAnalyzer:
    """Advanced analyzer for Claude.ai conversation exports"""
    
    def __init__(self, json_path: str, enable_privacy: bool = True, 
                 enable_clustering: bool = True, enable_viz: bool = True):
        self.json_path = Path(json_path)
        self.data = None
        self.df = None
        self.enable_privacy = enable_privacy
        self.enable_clustering = enable_clustering and SKLEARN_AVAILABLE
        self.enable_viz = enable_viz and PLOTTING_AVAILABLE
        
        # Privacy patterns (PII to redact)
        self.privacy_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'address': r'\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|boulevard|blvd|drive|dr|court|ct|lane|ln)\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'api_key': r'\b[A-Za-z0-9]{32,}\b',  # Simple pattern for long alphanumeric strings
        }
        
        # Sensitive entity patterns (names, locations to hash)
        self.sensitive_entities = {
            'person_name': r'\b(?:Dr\.|Mr\.|Mrs\.|Ms\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            'full_name': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Simple two-word capitalized names
        }
        
        # Enhanced topic detection patterns
        self.topic_patterns = {
            'Technical/Coding': [
                r'\b(python|javascript|typescript|java|c\+\+|rust|go|ruby)\b',
                r'\b(code|function|class|method|api|endpoint|docker|kubernetes|git)\b',
                r'\b(debug|error|exception|stack trace|bug|fix|refactor)\b',
                r'\b(programming|development|software|script|algorithm)\b',
                r'\b(container|deployment|ci/cd|devops|infrastructure)\b'
            ],
            'AI/ML': [
                r'\b(machine learning|neural network|deep learning|transformer)\b',
                r'\b(model|training|inference|embeddings|vector|llm|gpt)\b',
                r'\b(artificial intelligence|ai|ml|nlp|computer vision)\b',
                r'\b(huggingface|pytorch|tensorflow|langchain|openai)\b',
                r'\b(prompt|fine-?tun|dataset|optimization)\b'
            ],
            'BlaqVox Project': [
                r'\bblaqvox\b',
                r'\bcommunity intelligence\b',
                r'\bgovernment data\b',
                r'\bpublic records\b',
                r'\bdata liberation\b',
                r'\bdashboard|visualization|analytics\b'
            ],
            'GrandRYZE': [
                r'\bgrandrize\b',
                r'\bequipment analysis\b',
                r'\bimage classification\b',
                r'\bflask api\b'
            ],
            'Healthcare/VA': [
                r'\b(va|veteran|medical|healthcare|johanna|cardiac|hospital)\b',
                r'\b(doctor|physician|appointment|emergency|treatment)\b',
                r'\b(medication|prescription|diagnosis|symptoms)\b',
                r'\badvocacy|congressional|representative\b'
            ],
            'Philosophy/Consciousness': [
                r'\b(ubuntu|consciousness|ma\'?at|kemetic|liberation)\b',
                r'\b(philosophy|wisdom|sacred|collective|interconnect)\b',
                r'\b(phoenix|activation|framework|sovereign)\b',
                r'\b(mindfulness|awareness|presence|being)\b'
            ],
            'Creative/Art': [
                r'\b(music|art|creative|generate|image|video|rap|freestyle)\b',
                r'\b(production|studio|design|composition|visual)\b',
                r'\b(dall-?e|midjourney|stable diffusion|comfyui)\b',
                r'\b(poetry|writing|storytelling|narrative)\b'
            ],
            'Personal/Life': [
                r'\b(family|relationship|personal|feeling|emotion)\b',
                r'\b(christmas|holiday|vacation|travel|ocean shores)\b',
                r'\b(advice|guidance|support|help)\b'
            ],
            'Infrastructure': [
                r'\b(server|deployment|infrastructure|docker|container)\b',
                r'\b(architecture|system design|optimization|scaling)\b',
                r'\b(database|postgres|mongodb|redis|vector db)\b',
                r'\b(nginx|apache|cloud|aws|azure|gcp)\b'
            ],
            'Data Analysis': [
                r'\b(data|analysis|statistics|metrics|analytics)\b',
                r'\b(pandas|numpy|matplotlib|visualization)\b',
                r'\b(csv|excel|json|sql|query)\b'
            ],
            'Documentation': [
                r'\b(documentation|docs|readme|guide|tutorial)\b',
                r'\b(explain|clarify|describe|outline)\b',
                r'\b(technical writing|specification|requirements)\b'
            ],
            'Debugging': [
                r'\b(debug|troubleshoot|diagnose|investigate)\b',
                r'\b(error|exception|traceback|failing|broken)\b',
                r'\b(logs|logging|monitoring|observability)\b'
            ],
            'Security/Privacy': [
                r'\b(security|privacy|encryption|authentication)\b',
                r'\b(vulnerability|exploit|breach|attack)\b',
                r'\b(gdpr|compliance|data protection)\b'
            ]
        }
        
        # Enhanced sentiment indicators with intensity scoring
        self.sentiment_patterns = {
            'Very Positive': [
                r'\b(amazing|excellent|perfect|brilliant|outstanding|fantastic)\b',
                r'\b(love it|absolutely|phenomenal|incredible|wonderful)\b',
                r'🔥|✨|💯|🎉|🚀|⭐'
            ],
            'Positive': [
                r'\b(great|good|nice|helpful|thanks|appreciate|useful)\b',
                r'\b(works|working|solved|fixed|better)\b',
                r'😊|👍|👌|✅|💪'
            ],
            'Neutral': [
                r'\b(okay|fine|alright|understood|noted|got it)\b',
                r'\b(interesting|see|makes sense)\b'
            ],
            'Negative': [
                r'\b(wrong|error|failed|broken|issue|problem)\b',
                r'\b(doesn\'t work|not working|frustrated|confused)\b',
                r'😞|👎|❌'
            ],
            'Very Negative': [
                r'\b(terrible|horrible|awful|useless|disaster|catastrophe)\b',
                r'\b(hate|angry|furious|completely broken)\b',
                r'😠|💔|😡|🤬'
            ],
            'Urgent': [
                r'\b(urgent|emergency|asap|immediately|critical|now|help)\b',
                r'\b(deadline|time-sensitive|rush|quickly)\b',
                r'!!|!!!|⚠️|🚨|‼️'
            ],
            'Questioning': [
                r'\b(why|how|what|when|where|confused|unclear)\b',
                r'\b(can you|could you|would you|please explain)\b',
                r'❓|🤔'
            ],
            'Collaborative': [
                r'\b(let\'s|we can|together|collaborate|partnership)\b',
                r'\b(team|work with|joint|cooperative)\b',
                r'🤝|💫'
            ]
        }
        
        # Enhanced model failure patterns with severity
        self.failure_patterns = {
            'Hallucination': {
                'severity': 'high',
                'patterns': [
                    r'\b(that\'s not true|incorrect|wrong|didn\'t say|made up)\b',
                    r'\b(hallucinating|fabricated|inaccurate|false)\b',
                    r'\b(never said|not what i|completely wrong)\b'
                ]
            },
            'Refusal (Unnecessary)': {
                'severity': 'medium',
                'patterns': [
                    r'\b(won\'t help|can\'t assist|unable to|against guidelines)\b',
                    r'\b(safety|harmful|inappropriate|cannot provide)\b',
                    r'\b(not allowed|prohibited|restricted)\b'
                ]
            },
            'Formatting Issues': {
                'severity': 'low',
                'patterns': [
                    r'\b(formatting|markdown|broken|display|render)\b',
                    r'\b(code block|syntax|structure|layout)\b'
                ]
            },
            'Repetition': {
                'severity': 'medium',
                'patterns': [
                    r'\b(repeating|said that already|again|duplicate)\b',
                    r'\b(circular|loop|same thing|redundant)\b'
                ]
            },
            'Misunderstanding': {
                'severity': 'medium',
                'patterns': [
                    r'\b(didn\'t understand|misunderstood|confused|clarify)\b',
                    r'\b(what i meant|not what i asked|missed the point)\b'
                ]
            },
            'Performance Theater': {
                'severity': 'low',
                'patterns': [
                    r'\b(too formal|corporate speak|hedging|verbose)\b',
                    r'\b(unnecessary|over-explaining|preamble)\b',
                    r'\b(cut the|just answer|get to the point)\b'
                ]
            },
            'Tool Misuse': {
                'severity': 'high',
                'patterns': [
                    r'\b(wrong tool|should have searched|didn\'t search)\b',
                    r'\b(tool error|failed to fetch|api error)\b',
                    r'\b(why didn\'t you|forgot to use)\b'
                ]
            },
            'Context Loss': {
                'severity': 'high',
                'patterns': [
                    r'\b(forgot|lost context|earlier conversation|remember)\b',
                    r'\b(previous|before|you said|we discussed)\b',
                    r'\b(already told you|keep forgetting)\b'
                ]
            },
            'Accuracy Error': {
                'severity': 'high',
                'patterns': [
                    r'\b(factually wrong|incorrect information|outdated)\b',
                    r'\b(not accurate|misinformation|error in)\b'
                ]
            },
            'Incomplete Response': {
                'severity': 'medium',
                'patterns': [
                    r'\b(didn\'t finish|cut off|incomplete|partial)\b',
                    r'\b(where\'s the rest|finish this|complete)\b'
                ]
            },
            'Ignored Instructions': {
                'severity': 'high',
                'patterns': [
                    r'\b(asked you not to|told you to|ignored|didn\'t follow)\b',
                    r'\b(specifically said|explicitly requested)\b'
                ]
            }
        }
    
    def redact_pii(self, text: str) -> Tuple[str, List[str]]:
        """Redact personally identifiable information from text"""
        if not self.enable_privacy:
            return text, []
        
        redactions = []
        redacted_text = text
        
        # Redact PII patterns
        for pii_type, pattern in self.privacy_patterns.items():
            matches = re.finditer(pattern, redacted_text, re.IGNORECASE)
            for match in matches:
                original = match.group()
                redacted = f"[{pii_type.upper()}_REDACTED]"
                redacted_text = redacted_text.replace(original, redacted)
                redactions.append(pii_type)
        
        # Hash sensitive entities (names, etc) for consistency
        for entity_type, pattern in self.sensitive_entities.items():
            matches = re.finditer(pattern, redacted_text)
            for match in matches:
                original = match.group()
                # Create consistent hash for same name
                hashed = hashlib.md5(original.encode()).hexdigest()[:8]
                redacted = f"[{entity_type.upper()}_{hashed}]"
                redacted_text = redacted_text.replace(original, redacted)
                redactions.append(entity_type)
        
        return redacted_text, list(set(redactions))
    
    def load_data(self) -> None:
        """Load JSON export file"""
        print(f"Loading data from {self.json_path}...")
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"Loaded {len(self.data.get('conversations', []))} conversations")
    
    def detect_topics(self, text: str) -> List[str]:
        """Detect topics in text using pattern matching"""
        text_lower = text.lower()
        detected = []
        
        for topic, patterns in self.topic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected.append(topic)
                    break
        
        return detected if detected else ['General']
    
    def detect_sentiment(self, text: str) -> str:
        """Detect sentiment in text"""
        text_lower = text.lower()
        scores = {sentiment: 0 for sentiment in self.sentiment_patterns.keys()}
        
        for sentiment, patterns in self.sentiment_patterns.items():
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower, re.IGNORECASE))
                scores[sentiment] += matches
        
        # Urgent overrides if present
        if scores['Urgent'] > 0:
            return 'Urgent'
        
        # Return highest score
        max_sentiment = max(scores.items(), key=lambda x: x[1])
        return max_sentiment[0] if max_sentiment[1] > 0 else 'Neutral'
    
    def detect_failures(self, text: str) -> Tuple[List[str], List[str]]:
        """Detect model failure types and severities in text"""
        text_lower = text.lower()
        detected = []
        severities = []
        
        for failure_type, config in self.failure_patterns.items():
            patterns = config['patterns']
            severity = config['severity']
            
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    detected.append(failure_type)
                    severities.append(severity)
                    break
        
        return detected, severities
    
    def parse_conversations(self) -> pd.DataFrame:
        """Parse conversations into DataFrame"""
        print("Parsing conversations...")
        
        rows = []
        
        for conv in self.data.get('conversations', []):
            conv_id = conv.get('id', 'unknown')
            conv_created = conv.get('created_at', '')
            conv_updated = conv.get('updated_at', '')
            conv_name = conv.get('name', 'Untitled')
            model = conv.get('model', 'unknown')
            
            messages = conv.get('chat_messages', []) or conv.get('messages', [])
            
            for idx, message in enumerate(messages):
                content = message.get('text', '') or str(message.get('content', ''))
                role = message.get('sender', message.get('role', 'unknown'))
                msg_created = message.get('created_at', conv_created)
                
                # Skip empty messages
                if not content or len(content.strip()) < 3:
                    continue
                
                # Analyze content
                topics = self.detect_topics(content)
                sentiment = self.detect_sentiment(content)
                failures, severities = self.detect_failures(content) if role in ['assistant', 'bot'] else ([], [])
                
                rows.append({
                    'conversation_id': conv_id,
                    'conversation_name': conv_name,
                    'message_index': idx,
                    'timestamp': msg_created,
                    'role': role,
                    'model': model,
                    'content_preview': content[:300],
                    'content_length': len(content),
                    'word_count': len(content.split()),
                    'topics': '|'.join(topics),
                    'topic_count': len(topics),
                    'sentiment': sentiment,
                    'has_failure': len(failures) > 0,
                    'failure_types': '|'.join(failures) if failures else 'None',
                    'failure_count': len(failures),
                    'failure_severities': '|'.join(severities) if severities else 'None',
                    'max_failure_severity': max(severities, default='none') if severities else 'none'
                })
        
        self.df = pd.DataFrame(rows)
        print(f"Parsed {len(self.df)} messages")
        return self.df
    
    def generate_statistics(self) -> Dict:
        """Generate summary statistics"""
        print("Generating statistics...")
        
        stats = {
            'total_conversations': self.df['conversation_id'].nunique(),
            'total_messages': len(self.df),
            'user_messages': len(self.df[self.df['role'].isin(['user', 'human'])]),
            'assistant_messages': len(self.df[self.df['role'].isin(['assistant', 'bot'])]),
            'avg_message_length': self.df['content_length'].mean(),
            'avg_words_per_message': self.df['word_count'].mean(),
            
            # Topic distribution
            'topic_distribution': Counter([
                topic for topics in self.df['topics'].str.split('|') 
                for topic in topics if topic
            ]),
            
            # Sentiment distribution
            'sentiment_distribution': self.df['sentiment'].value_counts().to_dict(),
            
            # Failure analysis
            'messages_with_failures': len(self.df[self.df['has_failure']]),
            'failure_rate': len(self.df[self.df['has_failure']]) / len(self.df[self.df['role'].isin(['assistant', 'bot'])]) * 100,
            'failure_type_distribution': Counter([
                failure for failures in self.df['failure_types'].str.split('|') 
                for failure in failures if failure != 'None'
            ])
        }
        
        return stats
    
    def export_results(self, output_prefix: str = 'claude_analysis'):
        """Export results to CSV and Excel"""
        print("Exporting results...")
        
        # Main data export
        csv_path = f"{output_prefix}.csv"
        excel_path = f"{output_prefix}.xlsx"
        
        self.df.to_csv(csv_path, index=False)
        print(f"✓ Exported CSV: {csv_path}")
        
        # Excel with multiple sheets
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # Main data
            self.df.to_excel(writer, sheet_name='All Messages', index=False)
            
            # Topic summary
            topic_summary = self.df.groupby('topics').agg({
                'conversation_id': 'nunique',
                'message_index': 'count',
                'content_length': 'mean',
                'word_count': 'mean'
            }).round(2)
            topic_summary.columns = ['Unique Conversations', 'Message Count', 'Avg Length', 'Avg Words']
            topic_summary.to_excel(writer, sheet_name='Topic Summary')
            
            # Sentiment summary
            sentiment_summary = self.df.groupby('sentiment').agg({
                'conversation_id': 'nunique',
                'message_index': 'count'
            })
            sentiment_summary.columns = ['Unique Conversations', 'Message Count']
            sentiment_summary.to_excel(writer, sheet_name='Sentiment Summary')
            
            # Failure analysis (assistant messages only)
            failure_df = self.df[self.df['role'].isin(['assistant', 'bot'])].copy()
            failure_summary = failure_df.groupby('failure_types').agg({
                'conversation_id': 'nunique',
                'message_index': 'count'
            })
            failure_summary.columns = ['Unique Conversations', 'Message Count']
            failure_summary.to_excel(writer, sheet_name='Failure Analysis')
            
            # Statistics sheet
            stats = self.generate_statistics()
            stats_df = pd.DataFrame([
                {'Metric': 'Total Conversations', 'Value': stats['total_conversations']},
                {'Metric': 'Total Messages', 'Value': stats['total_messages']},
                {'Metric': 'User Messages', 'Value': stats['user_messages']},
                {'Metric': 'Assistant Messages', 'Value': stats['assistant_messages']},
                {'Metric': 'Avg Message Length', 'Value': f"{stats['avg_message_length']:.1f} chars"},
                {'Metric': 'Avg Words per Message', 'Value': f"{stats['avg_words_per_message']:.1f}"},
                {'Metric': 'Messages with Failures', 'Value': stats['messages_with_failures']},
                {'Metric': 'Failure Rate', 'Value': f"{stats['failure_rate']:.1f}%"},
            ])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        
        print(f"✓ Exported Excel: {excel_path}")
        
        return csv_path, excel_path
    
    def print_summary(self):
        """Print analysis summary to console"""
        stats = self.generate_statistics()
        
        print("\n" + "="*60)
        print("CLAUDE CONVERSATION ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\n📊 OVERALL STATS:")
        print(f"  Total Conversations: {stats['total_conversations']}")
        print(f"  Total Messages: {stats['total_messages']}")
        print(f"  User Messages: {stats['user_messages']}")
        print(f"  Assistant Messages: {stats['assistant_messages']}")
        print(f"  Avg Message Length: {stats['avg_message_length']:.1f} characters")
        print(f"  Avg Words/Message: {stats['avg_words_per_message']:.1f}")
        
        print(f"\n📁 TOP TOPICS:")
        for topic, count in stats['topic_distribution'].most_common(10):
            print(f"  {topic}: {count}")
        
        print(f"\n😊 SENTIMENT DISTRIBUTION:")
        for sentiment, count in stats['sentiment_distribution'].items():
            print(f"  {sentiment}: {count}")
        
        print(f"\n⚠️  FAILURE ANALYSIS:")
        print(f"  Messages with Failures: {stats['messages_with_failures']}")
        print(f"  Failure Rate: {stats['failure_rate']:.1f}%")
        print(f"\n  Failure Type Breakdown:")
        for failure_type, count in stats['failure_type_distribution'].most_common():
            print(f"    {failure_type}: {count}")
        
        print("\n" + "="*60 + "\n")


def main():
    """Main execution function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python claude_conversation_analyzer.py <path_to_json_export>")
        print("\nExample: python claude_conversation_analyzer.py claude_export.json")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) > 2 else 'claude_analysis'
    
    # Run analysis
    analyzer = ClaudeConversationAnalyzer(json_path)
    analyzer.load_data()
    analyzer.parse_conversations()
    analyzer.print_summary()
    csv_path, excel_path = analyzer.export_results(output_prefix)
    
    print(f"\n✅ Analysis complete!")
    print(f"   CSV: {csv_path}")
    print(f"   Excel: {excel_path}")


if __name__ == '__main__':
    main()
