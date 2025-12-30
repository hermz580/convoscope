"""
Visualization Generator Module
Creates charts and graphs for conversation analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


class VisualizationGenerator:
    """Generate visualizations for conversation data"""
    
    def __init__(self, df: pd.DataFrame, output_dir: str = '.'):
        self.df = df
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        if PLOTTING_AVAILABLE:
            # Set style
            sns.set_style('whitegrid')
            plt.rcParams['figure.figsize'] = (12, 6)
            plt.rcParams['font.size'] = 10
    
    def plot_topic_distribution(self, save_path: Optional[str] = None) -> Optional[str]:
        """Create bar chart of topic distribution"""
        
        if not PLOTTING_AVAILABLE or 'topics' not in self.df.columns:
            return None
        
        # Count topics
        all_topics = []
        for topics_str in self.df['topics'].dropna():
            all_topics.extend(topics_str.split('|'))
        
        topic_counts = pd.Series(all_topics).value_counts().head(15)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(14, 8))
        topic_counts.plot(kind='barh', ax=ax, color='steelblue')
        ax.set_xlabel('Count')
        ax.set_title('Top 15 Topics in Conversations', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Save
        if save_path is None:
            save_path = self.output_dir / 'topic_distribution.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_sentiment_trend(self, save_path: Optional[str] = None) -> Optional[str]:
        """Create line chart of sentiment over time"""
        
        if not PLOTTING_AVAILABLE or 'timestamp' not in self.df.columns or 'sentiment' not in self.df.columns:
            return None
        
        # Prepare data
        df_time = self.df.copy()
        df_time['timestamp'] = pd.to_datetime(df_time['timestamp'])
        df_time['date'] = df_time['timestamp'].dt.date
        
        # Count sentiments per day
        sentiment_daily = df_time.groupby(['date', 'sentiment']).size().unstack(fill_value=0)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(14, 8))
        sentiment_daily.plot(ax=ax, marker='o', linewidth=2)
        ax.set_xlabel('Date')
        ax.set_ylabel('Count')
        ax.set_title('Sentiment Trends Over Time', fontsize=14, fontweight='bold')
        ax.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save
        if save_path is None:
            save_path = self.output_dir / 'sentiment_trend.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_failure_analysis(self, save_path: Optional[str] = None) -> Optional[str]:
        """Create stacked bar chart of failure types"""
        
        if not PLOTTING_AVAILABLE or 'failure_types' not in self.df.columns:
            return None
        
        # Get failures
        failures_df = self.df[self.df['has_failure'] == True].copy()
        
        if len(failures_df) == 0:
            return None
        
        # Count failure types
        all_failures = []
        for failures_str in failures_df['failure_types'].dropna():
            if failures_str != 'None':
                all_failures.extend(failures_str.split('|'))
        
        if not all_failures:
            return None
        
        failure_counts = pd.Series(all_failures).value_counts()
        
        # Create plot
        fig, ax = plt.subplots(figsize=(14, 8))
        failure_counts.plot(kind='bar', ax=ax, color='coral')
        ax.set_xlabel('Failure Type')
        ax.set_ylabel('Count')
        ax.set_title('Model Failure Type Distribution', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save
        if save_path is None:
            save_path = self.output_dir / 'failure_analysis.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_activity_heatmap(self, save_path: Optional[str] = None) -> Optional[str]:
        """Create heatmap of activity by day and hour"""
        
        if not PLOTTING_AVAILABLE or 'timestamp' not in self.df.columns:
            return None
        
        # Prepare data
        df_time = self.df.copy()
        df_time['timestamp'] = pd.to_datetime(df_time['timestamp'])
        df_time['hour'] = df_time['timestamp'].dt.hour
        df_time['day_of_week'] = df_time['timestamp'].dt.day_name()
        
        # Pivot for heatmap
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = df_time.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        heatmap_data = heatmap_data.reindex(day_order)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(16, 8))
        sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='d', ax=ax, cbar_kws={'label': 'Message Count'})
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Day of Week')
        ax.set_title('Activity Heatmap: Messages by Day and Hour', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        # Save
        if save_path is None:
            save_path = self.output_dir / 'activity_heatmap.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_conversation_length_distribution(self, save_path: Optional[str] = None) -> Optional[str]:
        """Create histogram of conversation lengths"""
        
        if not PLOTTING_AVAILABLE or 'conversation_id' not in self.df.columns:
            return None
        
        # Calculate conversation lengths
        conv_lengths = self.df.groupby('conversation_id').size()
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        conv_lengths.plot(kind='hist', bins=30, ax=ax, color='skyblue', edgecolor='black')
        ax.set_xlabel('Messages per Conversation')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Conversation Lengths', fontsize=14, fontweight='bold')
        ax.axvline(conv_lengths.median(), color='red', linestyle='--', label=f'Median: {conv_lengths.median():.0f}')
        ax.legend()
        plt.tight_layout()
        
        # Save
        if save_path is None:
            save_path = self.output_dir / 'conversation_length_dist.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def plot_word_count_evolution(self, save_path: Optional[str] = None) -> Optional[str]:
        """Create line chart showing evolution of message lengths over time"""
        
        if not PLOTTING_AVAILABLE or 'timestamp' not in self.df.columns or 'word_count' not in self.df.columns:
            return None
        
        # Prepare data
        df_time = self.df.copy()
        df_time['timestamp'] = pd.to_datetime(df_time['timestamp'])
        df_time['date'] = df_time['timestamp'].dt.date
        
        # Calculate rolling average by role
        daily_words = df_time.groupby(['date', 'role'])['word_count'].mean().unstack(fill_value=0)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(14, 8))
        daily_words.plot(ax=ax, marker='o', linewidth=2)
        ax.set_xlabel('Date')
        ax.set_ylabel('Average Word Count')
        ax.set_title('Message Length Evolution Over Time', fontsize=14, fontweight='bold')
        ax.legend(title='Role', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save
        if save_path is None:
            save_path = self.output_dir / 'word_count_evolution.png'
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(save_path)
    
    def generate_all_visualizations(self) -> List[str]:
        """Generate all available visualizations"""
        
        if not PLOTTING_AVAILABLE:
            print("⚠️  Plotting libraries not available - skipping visualizations")
            return []
        
        visualizations = []
        
        viz_functions = [
            ('topic_distribution', self.plot_topic_distribution),
            ('sentiment_trend', self.plot_sentiment_trend),
            ('failure_analysis', self.plot_failure_analysis),
            ('activity_heatmap', self.plot_activity_heatmap),
            ('conversation_length_dist', self.plot_conversation_length_distribution),
            ('word_count_evolution', self.plot_word_count_evolution),
        ]
        
        for name, func in viz_functions:
            try:
                path = func()
                if path:
                    visualizations.append(path)
                    print(f"✓ Generated: {name}")
            except Exception as e:
                print(f"⚠️  Failed to generate {name}: {e}")
        
        return visualizations
    
    def create_dashboard_html(self, viz_paths: List[str], save_path: Optional[str] = None) -> str:
        """Create HTML dashboard with all visualizations"""
        
        if save_path is None:
            save_path = self.output_dir / 'dashboard.html'
        
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Claude Conversation Analysis Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .subtitle {
            opacity: 0.9;
            margin-top: 10px;
        }
        .viz-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 20px;
        }
        .viz-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .viz-card img {
            width: 100%;
            border-radius: 5px;
        }
        .viz-title {
            font-size: 1.2em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Claude Conversation Analysis Dashboard</h1>
        <div class="subtitle">Comprehensive analysis of conversation patterns, topics, and quality metrics</div>
    </div>
    
    <div class="viz-grid">
"""
        
        # Add visualizations
        for viz_path in viz_paths:
            viz_name = Path(viz_path).stem.replace('_', ' ').title()
            html += f"""
        <div class="viz-card">
            <div class="viz-title">{viz_name}</div>
            <img src="{Path(viz_path).name}" alt="{viz_name}">
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        with open(save_path, 'w') as f:
            f.write(html)
        
        print(f"✓ Created dashboard: {save_path}")
        return str(save_path)
