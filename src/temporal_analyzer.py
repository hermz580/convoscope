"""
Temporal Evolution Analyzer Module
Tracks how conversations, topics, and quality evolve over time
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict


class TemporalEvolutionAnalyzer:
    """Analyze temporal patterns and evolution in conversations"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
        # Ensure timestamp is datetime
        if 'timestamp' in self.df.columns:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'], errors='coerce')
            self.df['date'] = self.df['timestamp'].dt.date
            self.df['hour'] = self.df['timestamp'].dt.hour
            self.df['day_of_week'] = self.df['timestamp'].dt.day_name()
            self.df['week'] = self.df['timestamp'].dt.isocalendar().week
            self.df['month'] = self.df['timestamp'].dt.to_period('M')
    
    def analyze_activity_patterns(self) -> Dict:
        """Analyze when conversations happen"""
        
        patterns = {}
        
        # Daily patterns
        if 'hour' in self.df.columns:
            hourly = self.df.groupby('hour').size()
            patterns['peak_hours'] = hourly.nlargest(3).index.tolist()
            patterns['quiet_hours'] = hourly.nsmallest(3).index.tolist()
            patterns['hourly_distribution'] = hourly.to_dict()
        
        # Weekly patterns
        if 'day_of_week' in self.df.columns:
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily = self.df.groupby('day_of_week').size().reindex(day_order)
            patterns['busiest_days'] = daily.nlargest(3).index.tolist()
            patterns['quietest_days'] = daily.nsmallest(3).index.tolist()
            patterns['daily_distribution'] = daily.to_dict()
        
        return patterns
    
    def analyze_topic_evolution(self) -> pd.DataFrame:
        """Track how topics change over time"""
        
        if 'topics' not in self.df.columns or 'month' not in self.df.columns:
            return pd.DataFrame()
        
        # Explode topics (split multi-topic messages)
        topic_df = self.df[['month', 'topics']].copy()
        topic_df['topics'] = topic_df['topics'].str.split('|')
        topic_df = topic_df.explode('topics')
        
        # Count topics per month
        evolution = topic_df.groupby(['month', 'topics']).size().unstack(fill_value=0)
        
        # Calculate growth rates
        growth = evolution.pct_change() * 100
        
        return evolution
    
    def analyze_quality_trends(self) -> Dict:
        """Analyze how conversation quality changes over time"""
        
        trends = {}
        
        if 'month' in self.df.columns and 'sentiment' in self.df.columns:
            # Sentiment trend
            sentiment_monthly = self.df.groupby('month')['sentiment'].value_counts(normalize=True).unstack(fill_value=0)
            trends['sentiment_trend'] = sentiment_monthly
            
            # Calculate positive sentiment ratio
            positive_cols = [col for col in sentiment_monthly.columns if 'positive' in col.lower()]
            if positive_cols:
                trends['positive_ratio_trend'] = sentiment_monthly[positive_cols].sum(axis=1)
        
        if 'month' in self.df.columns and 'has_failure' in self.df.columns:
            # Failure rate trend
            failure_monthly = self.df.groupby('month')['has_failure'].agg(['sum', 'count'])
            failure_monthly['failure_rate'] = (failure_monthly['sum'] / failure_monthly['count'] * 100)
            trends['failure_rate_trend'] = failure_monthly['failure_rate']
        
        if 'month' in self.df.columns and 'word_count' in self.df.columns:
            # Message length trend
            length_monthly = self.df.groupby('month')['word_count'].agg(['mean', 'median'])
            trends['message_length_trend'] = length_monthly
        
        return trends
    
    def detect_pattern_changes(self, window_days: int = 30) -> List[Dict]:
        """Detect significant changes in conversation patterns"""
        
        if 'timestamp' not in self.df.columns:
            return []
        
        changes = []
        
        # Sort by timestamp
        df_sorted = self.df.sort_values('timestamp')
        
        # Calculate rolling metrics
        df_sorted['rolling_sentiment_score'] = 0
        df_sorted.loc[df_sorted['sentiment'].str.contains('Positive', na=False), 'rolling_sentiment_score'] = 1
        df_sorted.loc[df_sorted['sentiment'].str.contains('Negative', na=False), 'rolling_sentiment_score'] = -1
        
        # Rolling average
        df_sorted['sentiment_ma'] = df_sorted['rolling_sentiment_score'].rolling(window=10, min_periods=1).mean()
        
        # Detect significant shifts (change > 0.5 in moving average)
        df_sorted['sentiment_shift'] = df_sorted['sentiment_ma'].diff().abs()
        
        significant_shifts = df_sorted[df_sorted['sentiment_shift'] > 0.5]
        
        for idx, row in significant_shifts.iterrows():
            changes.append({
                'timestamp': row['timestamp'],
                'type': 'sentiment_shift',
                'magnitude': row['sentiment_shift'],
                'direction': 'positive' if row['sentiment_ma'] > 0 else 'negative'
            })
        
        return changes
    
    def calculate_engagement_score(self) -> pd.DataFrame:
        """Calculate engagement score over time"""
        
        if 'date' not in self.df.columns:
            return pd.DataFrame()
        
        daily_metrics = self.df.groupby('date').agg({
            'message_index': 'count',  # Message count
            'word_count': 'mean',  # Avg message length
            'conversation_id': 'nunique',  # Unique conversations
        }).reset_index()
        
        daily_metrics.columns = ['date', 'message_count', 'avg_length', 'conversation_count']
        
        # Engagement score = normalized combination of metrics
        daily_metrics['engagement_score'] = (
            (daily_metrics['message_count'] / daily_metrics['message_count'].max()) * 0.4 +
            (daily_metrics['avg_length'] / daily_metrics['avg_length'].max()) * 0.3 +
            (daily_metrics['conversation_count'] / daily_metrics['conversation_count'].max()) * 0.3
        ) * 100
        
        return daily_metrics
    
    def identify_conversation_streaks(self, min_days: int = 3) -> List[Dict]:
        """Identify periods of consistent daily activity"""
        
        if 'date' not in self.df.columns:
            return []
        
        # Get unique dates with activity
        active_dates = sorted(self.df['date'].dropna().unique())
        
        if len(active_dates) < min_days:
            return []
        
        streaks = []
        current_streak = [active_dates[0]]
        
        for i in range(1, len(active_dates)):
            # Check if consecutive day
            if (active_dates[i] - active_dates[i-1]).days == 1:
                current_streak.append(active_dates[i])
            else:
                # Streak ended
                if len(current_streak) >= min_days:
                    streaks.append({
                        'start_date': current_streak[0],
                        'end_date': current_streak[-1],
                        'length_days': len(current_streak),
                        'message_count': len(self.df[
                            (self.df['date'] >= current_streak[0]) & 
                            (self.df['date'] <= current_streak[-1])
                        ])
                    })
                current_streak = [active_dates[i]]
        
        # Check final streak
        if len(current_streak) >= min_days:
            streaks.append({
                'start_date': current_streak[0],
                'end_date': current_streak[-1],
                'length_days': len(current_streak),
                'message_count': len(self.df[
                    (self.df['date'] >= current_streak[0]) & 
                    (self.df['date'] <= current_streak[-1])
                ])
            })
        
        return sorted(streaks, key=lambda x: x['length_days'], reverse=True)
    
    def generate_temporal_summary(self) -> Dict:
        """Generate comprehensive temporal summary"""
        
        summary = {}
        
        if 'timestamp' in self.df.columns:
            summary['date_range'] = {
                'start': self.df['timestamp'].min(),
                'end': self.df['timestamp'].max(),
                'duration_days': (self.df['timestamp'].max() - self.df['timestamp'].min()).days
            }
        
        summary['activity_patterns'] = self.analyze_activity_patterns()
        summary['engagement_trend'] = self.calculate_engagement_score().to_dict('records')
        summary['streaks'] = self.identify_conversation_streaks()
        summary['pattern_changes'] = self.detect_pattern_changes()
        
        return summary
