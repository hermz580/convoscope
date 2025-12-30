#!/usr/bin/env python3
"""
Claude Conversation Data Analyzer - Advanced Edition v2.0
Complete conversation analysis with quality metrics, temporal evolution, and visualizations
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

# Import analysis modules
from quality_analyzer import ConversationQualityAnalyzer, analyze_conversation_flow
from temporal_analyzer import TemporalEvolutionAnalyzer
from visualization_generator import VisualizationGenerator

# Import original analyzer base
import importlib.util
spec = importlib.util.spec_from_file_location("base_analyzer", "/home/claude/claude_conversation_analyzer.py")
base_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_module)
ClaudeConversationAnalyzer = base_module.ClaudeConversationAnalyzer


class AdvancedConversationAnalyzer(ClaudeConversationAnalyzer):
    """Enhanced analyzer with quality metrics and advanced features"""
    
    def __init__(self, json_path: str, **kwargs):
        super().__init__(json_path)
        
        # Configuration
        self.enable_privacy = kwargs.get('enable_privacy', True)
        self.enable_quality_analysis = kwargs.get('enable_quality_analysis', True)
        self.enable_temporal_analysis = kwargs.get('enable_temporal_analysis', True)
        self.enable_visualizations = kwargs.get('enable_visualizations', True)
        
        # Additional analyzers
        self.quality_analyzer = ConversationQualityAnalyzer() if self.enable_quality_analysis else None
        self.temporal_analyzer = None  # Initialized after parsing
        self.viz_generator = None  # Initialized after parsing
    
    def parse_conversations_advanced(self) -> pd.DataFrame:
        """Enhanced parsing with quality metrics"""
        
        print("Parsing conversations with advanced analysis...")
        
        # Use base parsing first
        self.df = super().parse_conversations()
        
        if self.df is None or len(self.df) == 0:
            print("⚠️  No data to analyze")
            return self.df
        
        # Apply privacy redaction
        if self.enable_privacy:
            print("Applying privacy redactions...")
            self.df[['content_preview', 'pii_redactions']] = self.df['content_preview'].apply(
                lambda x: pd.Series(self.redact_pii(x))
            )
        
        # Add quality metrics
        if self.enable_quality_analysis:
            print("Calculating quality metrics...")
            self.df = self._add_quality_metrics()
        
        # Initialize temporal analyzer
        if self.enable_temporal_analysis:
            self.temporal_analyzer = TemporalEvolutionAnalyzer(self.df)
        
        # Initialize visualization generator
        if self.enable_visualizations:
            self.viz_generator = VisualizationGenerator(self.df)
        
        print(f"✓ Advanced parsing complete: {len(self.df)} messages analyzed")
        return self.df
    
    def _add_quality_metrics(self) -> pd.DataFrame:
        """Add conversation quality metrics to dataframe"""
        
        df = self.df.copy()
        
        # Group messages by conversation
        conversations = df.groupby('conversation_id')
        
        quality_metrics = []
        
        for conv_id, conv_df in conversations:
            messages = conv_df.to_dict('records')
            
            # Calculate conversation-level metrics
            conv_metrics = self.quality_analyzer.calculate_conversation_metrics(messages)
            flow_metrics = analyze_conversation_flow(messages)
            
            # Collaboration quality
            collab_quality = self.quality_analyzer.analyze_collaboration_quality(messages)
            
            # Task completion
            message_texts = [m.get('content_preview', '') for m in messages]
            task_status = self.quality_analyzer.analyze_task_completion(message_texts)
            
            # Add to each message in conversation
            for idx in conv_df.index:
                quality_metrics.append({
                    'index': idx,
                    'collaboration_quality': collab_quality,
                    'task_completion_status': task_status['status'],
                    'task_completion_confidence': task_status['confidence'],
                    'conversation_turn_count': conv_metrics['turn_count'],
                    'conversation_questions': conv_metrics['user_questions'],
                    'conversation_code_blocks': conv_metrics['assistant_code_blocks'],
                    'flow_interruptions': flow_metrics['interruptions'],
                    'flow_quick_responses': flow_metrics['quick_responses'],
                })
        
        # Merge metrics into dataframe
        metrics_df = pd.DataFrame(quality_metrics).set_index('index')
        df = df.join(metrics_df)
        
        return df
    
    def generate_comprehensive_report(self, output_prefix: str = 'claude_analysis_v2') -> Dict[str, str]:
        """Generate comprehensive analysis report with all outputs"""
        
        print("\n" + "="*70)
        print("GENERATING COMPREHENSIVE ANALYSIS REPORT")
        print("="*70 + "\n")
        
        outputs = {}
        
        # 1. Standard CSV/Excel exports
        print("📄 Exporting data files...")
        csv_path, excel_path = self.export_results(output_prefix)
        outputs['csv'] = csv_path
        outputs['excel'] = excel_path
        
        # 2. Generate visualizations
        if self.viz_generator:
            print("\n📊 Generating visualizations...")
            viz_paths = self.viz_generator.generate_all_visualizations()
            outputs['visualizations'] = viz_paths
            
            if viz_paths:
                dashboard_path = self.viz_generator.create_dashboard_html(viz_paths)
                outputs['dashboard'] = dashboard_path
        
        # 3. Temporal analysis report
        if self.temporal_analyzer:
            print("\n⏱️  Generating temporal analysis...")
            temporal_report = self._generate_temporal_report(output_prefix)
            outputs['temporal_report'] = temporal_report
        
        # 4. Quality analysis report
        if self.enable_quality_analysis:
            print("\n✨ Generating quality analysis...")
            quality_report = self._generate_quality_report(output_prefix)
            outputs['quality_report'] = quality_report
        
        # 5. Executive summary
        print("\n📋 Generating executive summary...")
        summary_path = self._generate_executive_summary(output_prefix)
        outputs['executive_summary'] = summary_path
        
        print("\n" + "="*70)
        print("✅ COMPREHENSIVE ANALYSIS COMPLETE")
        print("="*70 + "\n")
        
        return outputs
    
    def _generate_temporal_report(self, output_prefix: str) -> str:
        """Generate temporal evolution report"""
        
        report_path = f"{output_prefix}_temporal_report.txt"
        
        summary = self.temporal_analyzer.generate_temporal_summary()
        
        with open(report_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("TEMPORAL EVOLUTION ANALYSIS REPORT\n")
            f.write("="*70 + "\n\n")
            
            # Date range
            if 'date_range' in summary:
                dr = summary['date_range']
                f.write(f"Analysis Period: {dr['start']} to {dr['end']}\n")
                f.write(f"Duration: {dr['duration_days']} days\n\n")
            
            # Activity patterns
            if 'activity_patterns' in summary:
                f.write("ACTIVITY PATTERNS:\n")
                f.write("-" * 50 + "\n")
                ap = summary['activity_patterns']
                
                if 'peak_hours' in ap:
                    f.write(f"Peak Hours: {', '.join(map(str, ap['peak_hours']))}\n")
                if 'busiest_days' in ap:
                    f.write(f"Busiest Days: {', '.join(ap['busiest_days'])}\n")
                f.write("\n")
            
            # Conversation streaks
            if 'streaks' in summary and summary['streaks']:
                f.write("CONVERSATION STREAKS:\n")
                f.write("-" * 50 + "\n")
                for i, streak in enumerate(summary['streaks'][:5], 1):
                    f.write(f"{i}. {streak['start_date']} to {streak['end_date']}\n")
                    f.write(f"   Length: {streak['length_days']} days, Messages: {streak['message_count']}\n")
                f.write("\n")
            
            # Pattern changes
            if 'pattern_changes' in summary and summary['pattern_changes']:
                f.write("SIGNIFICANT PATTERN CHANGES:\n")
                f.write("-" * 50 + "\n")
                for change in summary['pattern_changes'][:10]:
                    f.write(f"{change['timestamp']}: {change['type']} ({change['direction']}, magnitude: {change['magnitude']:.2f})\n")
        
        print(f"✓ Temporal report: {report_path}")
        return report_path
    
    def _generate_quality_report(self, output_prefix: str) -> str:
        """Generate conversation quality report"""
        
        report_path = f"{output_prefix}_quality_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("CONVERSATION QUALITY ANALYSIS REPORT\n")
            f.write("="*70 + "\n\n")
            
            # Collaboration quality distribution
            if 'collaboration_quality' in self.df.columns:
                f.write("COLLABORATION QUALITY DISTRIBUTION:\n")
                f.write("-" * 50 + "\n")
                collab_dist = self.df.groupby('conversation_id')['collaboration_quality'].first().value_counts()
                for quality, count in collab_dist.items():
                    pct = (count / len(collab_dist) * 100)
                    f.write(f"{quality}: {count} conversations ({pct:.1f}%)\n")
                f.write("\n")
            
            # Task completion rates
            if 'task_completion_status' in self.df.columns:
                f.write("TASK COMPLETION RATES:\n")
                f.write("-" * 50 + "\n")
                task_dist = self.df.groupby('conversation_id')['task_completion_status'].first().value_counts()
                for status, count in task_dist.items():
                    pct = (count / len(task_dist) * 100)
                    f.write(f"{status}: {count} conversations ({pct:.1f}%)\n")
                f.write("\n")
            
            # Average conversation metrics
            if 'conversation_turn_count' in self.df.columns:
                f.write("AVERAGE CONVERSATION METRICS:\n")
                f.write("-" * 50 + "\n")
                f.write(f"Average turns per conversation: {self.df.groupby('conversation_id')['conversation_turn_count'].first().mean():.1f}\n")
                f.write(f"Average questions per conversation: {self.df.groupby('conversation_id')['conversation_questions'].first().mean():.1f}\n")
                f.write(f"Average code blocks per conversation: {self.df.groupby('conversation_id')['conversation_code_blocks'].first().mean():.1f}\n")
        
        print(f"✓ Quality report: {report_path}")
        return report_path
    
    def _generate_executive_summary(self, output_prefix: str) -> str:
        """Generate executive summary"""
        
        summary_path = f"{output_prefix}_executive_summary.txt"
        stats = self.generate_statistics()
        
        with open(summary_path, 'w') as f:
            f.write("="*70 + "\n")
            f.write("EXECUTIVE SUMMARY - CLAUDE CONVERSATION ANALYSIS\n")
            f.write("="*70 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")
            
            f.write("KEY METRICS:\n")
            f.write("-" * 50 + "\n")
            f.write(f"Total Conversations: {stats['total_conversations']}\n")
            f.write(f"Total Messages: {stats['total_messages']}\n")
            f.write(f"User Messages: {stats['user_messages']}\n")
            f.write(f"Assistant Messages: {stats['assistant_messages']}\n")
            f.write(f"Average Message Length: {stats['avg_message_length']:.0f} characters\n")
            f.write(f"Average Words per Message: {stats['avg_words_per_message']:.1f}\n")
            f.write("\n")
            
            f.write("TOP TOPICS:\n")
            f.write("-" * 50 + "\n")
            for topic, count in stats['topic_distribution'].most_common(10):
                f.write(f"{topic}: {count}\n")
            f.write("\n")
            
            f.write("SENTIMENT OVERVIEW:\n")
            f.write("-" * 50 + "\n")
            for sentiment, count in sorted(stats['sentiment_distribution'].items(), key=lambda x: x[1], reverse=True):
                pct = (count / stats['total_messages'] * 100)
                f.write(f"{sentiment}: {count} ({pct:.1f}%)\n")
            f.write("\n")
            
            f.write("MODEL PERFORMANCE:\n")
            f.write("-" * 50 + "\n")
            f.write(f"Messages with Failures: {stats['messages_with_failures']}\n")
            f.write(f"Failure Rate: {stats['failure_rate']:.1f}%\n")
            f.write("\n")
            
            if stats['failure_type_distribution']:
                f.write("Top Failure Types:\n")
                for failure_type, count in stats['failure_type_distribution'].most_common(5):
                    f.write(f"  - {failure_type}: {count}\n")
        
        print(f"✓ Executive summary: {summary_path}")
        return summary_path


def main():
    """Main execution"""
    
    if len(sys.argv) < 2:
        print("Usage: python advanced_analyzer.py <json_export> [output_prefix] [options]")
        print("\nOptions:")
        print("  --no-privacy         Disable PII redaction")
        print("  --no-quality         Disable quality analysis")
        print("  --no-temporal        Disable temporal analysis")
        print("  --no-viz             Disable visualizations")
        print("\nExample: python advanced_analyzer.py export.json my_analysis --no-viz")
        sys.exit(1)
    
    json_path = sys.argv[1]
    output_prefix = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'claude_analysis_v2'
    
    # Parse options
    options = {
        'enable_privacy': '--no-privacy' not in sys.argv,
        'enable_quality_analysis': '--no-quality' not in sys.argv,
        'enable_temporal_analysis': '--no-temporal' not in sys.argv,
        'enable_visualizations': '--no-viz' not in sys.argv,
    }
    
    # Run analysis
    analyzer = AdvancedConversationAnalyzer(json_path, **options)
    analyzer.load_data()
    analyzer.parse_conversations_advanced()
    analyzer.print_summary()
    outputs = analyzer.generate_comprehensive_report(output_prefix)
    
    print("\n📁 OUTPUT FILES:")
    for output_type, path in outputs.items():
        if isinstance(path, list):
            print(f"\n{output_type}:")
            for p in path:
                print(f"  - {p}")
        else:
            print(f"{output_type}: {path}")
    
    print("\n✅ Analysis complete!")


if __name__ == '__main__':
    main()
