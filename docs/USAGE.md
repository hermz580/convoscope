# ConvoScope Usage Guide

Complete guide to using ConvoScope for conversation analysis.

## Table of Contents
- [Getting Started](#getting-started)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Understanding Outputs](#understanding-outputs)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Claude.ai account with conversation history
- ~500MB free disk space for analysis outputs

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/convoscope.git
cd convoscope

# Install dependencies
pip install -r requirements.txt

# Verify installation
python src/advanced_analyzer.py --help
```

### Getting Your Data

1. **Request Export**
   - Navigate to [claude.ai/settings](https://claude.ai/settings)
   - Click Privacy tab
   - Click "Download my data"
   - Confirm email

2. **Wait for Email**
   - Usually arrives within 1-3 days
   - Check spam folder if not received
   - Email contains download link

3. **Extract Data**
   ```bash
   # Download the ZIP file
   # Extract to a known location
   unzip claude_export.zip
   # You should see a conversations.json file
   ```

## Basic Usage

### Simple Analysis

```bash
# Run with all features enabled
python src/advanced_analyzer.py conversations.json

# This creates:
# - claude_analysis_v2.csv
# - claude_analysis_v2.xlsx
# - claude_analysis_v2_executive_summary.txt
# - claude_analysis_v2_quality_report.txt
# - claude_analysis_v2_temporal_report.txt
# - Multiple visualization PNGs
# - dashboard.html
```

### Custom Output Name

```bash
# Specify output prefix
python src/advanced_analyzer.py conversations.json my_analysis

# Creates files like:
# - my_analysis.csv
# - my_analysis.xlsx
# - etc.
```

### Quick Analysis (No Visualizations)

```bash
# Skip visualizations for faster processing
python src/advanced_analyzer.py conversations.json quick --no-viz

# Reduces processing time by ~60%
# Still generates all text reports and data files
```

## Advanced Usage

### Selective Features

```bash
# Disable specific features
python src/advanced_analyzer.py conversations.json output \
  --no-viz \          # Skip visualizations
  --no-privacy \      # Skip PII redaction (not recommended)
  --no-quality \      # Skip quality analysis
  --no-temporal       # Skip temporal analysis

# Minimal analysis (fastest)
python src/advanced_analyzer.py conversations.json minimal \
  --no-viz --no-quality --no-temporal
```

### Python API

```python
from src.advanced_analyzer import AdvancedConversationAnalyzer

# Initialize analyzer with custom options
analyzer = AdvancedConversationAnalyzer(
    json_path='conversations.json',
    enable_privacy=True,
    enable_quality_analysis=True,
    enable_temporal_analysis=True,
    enable_visualizations=False  # Disable viz for speed
)

# Load and parse data
analyzer.load_data()
df = analyzer.parse_conversations_advanced()

# Access the dataframe
print(f"Analyzed {len(df)} messages")
print(df.head())

# Generate reports
outputs = analyzer.generate_comprehensive_report('custom_output')

# Work with specific data
tech_convos = df[df['topics'].str.contains('Technical')]
high_quality = df[df['collaboration_quality'] == 'high']
recent_failures = df[df['has_failure'] == True]
```

### Custom Filtering

```python
import pandas as pd

# Load the CSV
df = pd.read_csv('claude_analysis_v2.csv')

# Filter by topic
ai_ml_convos = df[df['topics'].str.contains('AI/ML')]

# Filter by date range
df['timestamp'] = pd.to_datetime(df['timestamp'])
recent = df[df['timestamp'] > '2024-12-01']

# Filter by quality
completed_tasks = df[df['task_completion_status'] == 'completed']
high_collab = df[df['collaboration_quality'] == 'high']

# Combine filters
high_quality_tech = df[
    (df['topics'].str.contains('Technical')) &
    (df['collaboration_quality'] == 'high') &
    (df['has_failure'] == False)
]

# Export filtered data
high_quality_tech.to_csv('high_quality_technical.csv', index=False)
```

### Batch Processing

```python
import glob
from pathlib import Path

# Process multiple exports
export_files = glob.glob('exports/*.json')

for export_file in export_files:
    name = Path(export_file).stem
    print(f"Processing {name}...")
    
    analyzer = AdvancedConversationAnalyzer(
        export_file,
        enable_visualizations=False  # Faster batch processing
    )
    analyzer.load_data()
    analyzer.parse_conversations_advanced()
    analyzer.generate_comprehensive_report(f'batch_{name}')
```

## Understanding Outputs

### CSV File Structure

The main CSV contains 25+ columns:

**Identification:**
- `conversation_id`: Unique conversation identifier
- `conversation_name`: Title of conversation
- `message_index`: Position in conversation
- `timestamp`: When message was sent
- `role`: user or assistant
- `model`: Claude model version used

**Content:**
- `content_preview`: First 300 characters (PII redacted)
- `content_length`: Character count
- `word_count`: Word count

**Topic Analysis:**
- `topics`: Pipe-separated topic list
- `topic_count`: Number of topics detected

**Sentiment:**
- `sentiment`: Detected sentiment level
  - Very Positive, Positive, Neutral, Negative, Very Negative
  - Urgent, Questioning, Collaborative

**Failure Detection:**
- `has_failure`: Boolean flag
- `failure_types`: Pipe-separated failure types
- `failure_count`: Number of failures
- `failure_severities`: Severity levels (high/medium/low)
- `max_failure_severity`: Highest severity in message

**Quality Metrics:**
- `collaboration_quality`: high, medium, low, confrontational
- `task_completion_status`: completed, in_progress, abandoned, blocked
- `task_completion_confidence`: 0.0 to 1.0
- `conversation_turn_count`: Total turns in conversation
- `conversation_questions`: User questions count
- `conversation_code_blocks`: Assistant code blocks count
- `flow_interruptions`: Consecutive same-role messages
- `flow_quick_responses`: Responses < 1 minute

**Privacy:**
- `pii_redactions`: Types of PII removed

### Excel Workbook Sheets

**Sheet 1: All Messages**
- Complete dataset with all columns
- Sortable and filterable

**Sheet 2: Topic Summary**
- Topics ranked by frequency
- Unique conversations per topic
- Average message metrics per topic

**Sheet 3: Sentiment Summary**
- Sentiment distribution
- Conversation and message counts
- Percentage breakdowns

**Sheet 4: Failure Analysis**
- Failure type frequencies
- Severity distributions
- Impact on conversation quality

**Sheet 5: Statistics**
- High-level overview metrics
- Total counts
- Averages and rates
- Top categories

### Report Files

**Executive Summary (`*_executive_summary.txt`)**
- Key metrics at a glance
- Top topics and sentiments
- Model performance overview
- Major failure types

**Quality Report (`*_quality_report.txt`)**
- Collaboration quality distribution
- Task completion rates
- Average conversation metrics
- Quality trends

**Temporal Report (`*_temporal_report.txt`)**
- Activity patterns (peak hours, busiest days)
- Conversation streaks
- Significant pattern changes
- Evolution over time

### Visualizations

**Topic Distribution (`topic_distribution.png`)**
- Horizontal bar chart
- Shows frequency of each topic
- Useful for understanding focus areas

**Sentiment Trend (`sentiment_trend.png`)**
- Line chart over time
- Tracks sentiment changes
- Identifies positive/negative periods

**Activity Heatmap (`activity_heatmap.png`)**
- Day × Hour grid
- Shows peak activity times
- Useful for productivity analysis

**Failure Analysis (`failure_analysis.png`)**
- Bar chart of failure types
- Highlights problem areas
- Guides quality improvements

**Conversation Length Distribution (`conversation_length_dist.png`)**
- Histogram of message counts
- Shows typical conversation patterns
- Median line for reference

**Word Count Evolution (`word_count_evolution.png`)**
- Trends in message length
- Separate lines for user/assistant
- Tracks communication style changes

**Dashboard (`dashboard.html`)**
- Interactive HTML page
- All visualizations in one place
- Professional presentation format

## Customization

### Adding Custom Topics

Edit `src/claude_conversation_analyzer.py`:

```python
self.topic_patterns = {
    # Existing topics...
    
    # Add your custom topic
    'Your Custom Topic': [
        r'\byour|keywords|here\b',
        r'\bother|patterns\b',
        r'\bspecific phrases\b'
    ]
}
```

### Custom Sentiment Patterns

```python
self.sentiment_patterns = {
    # Existing sentiments...
    
    # Add custom sentiment
    'Your Sentiment': [
        r'\bpattern|here\b',
        r'emoji: 🔥'
    ]
}
```

### Custom Failure Detection

```python
self.failure_patterns = {
    # Existing failures...
    
    # Add custom failure type
    'Your Failure Type': {
        'severity': 'medium',  # high, medium, or low
        'patterns': [
            r'\berror|pattern\b',
            r'\bspecific|indicator\b'
        ]
    }
}
```

### Custom Privacy Patterns

```python
self.privacy_patterns = {
    # Existing patterns...
    
    # Add custom PII pattern
    'your_pii_type': r'\byour|pattern|here\b'
}
```

## Troubleshooting

### Common Issues

**Issue: "No module named 'pandas'"**
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue: "File not found: conversations.json"**
```bash
# Solution: Provide full path
python src/advanced_analyzer.py /full/path/to/conversations.json
```

**Issue: Memory error with large datasets**
```python
# Solution: Process in chunks
# For files > 100MB, split the JSON first
import json

with open('large_export.json') as f:
    data = json.load(f)

# Process 1000 conversations at a time
chunk_size = 1000
for i in range(0, len(data['conversations']), chunk_size):
    chunk = {'conversations': data['conversations'][i:i+chunk_size]}
    
    with open(f'chunk_{i}.json', 'w') as f:
        json.dump(chunk, f)
    
    # Analyze each chunk separately
    analyzer = AdvancedConversationAnalyzer(f'chunk_{i}.json')
    analyzer.load_data()
    analyzer.parse_conversations_advanced()
    analyzer.generate_comprehensive_report(f'chunk_{i}_analysis')
```

**Issue: Visualization errors**
```bash
# Solution: Install visualization dependencies
pip install matplotlib seaborn

# Or skip visualizations
python src/advanced_analyzer.py export.json output --no-viz
```

**Issue: Slow processing**
```bash
# Solution: Disable optional features
python src/advanced_analyzer.py export.json fast \
  --no-viz --no-temporal --no-quality

# Or process smaller date ranges
```

### Performance Tips

**For datasets > 10K messages:**
- Use `--no-viz` flag
- Consider disabling quality analysis
- Process in chunks if memory limited
- Use SSD storage for faster I/O

**For datasets > 100K messages:**
- Definitely process in chunks
- Use command-line only (no Python API)
- Consider using a server/cloud instance
- Export to database for querying

### Getting Help

If you encounter issues:

1. Check [documentation](../README.md)
2. Search [GitHub issues](https://github.com/yourusername/convoscope/issues)
3. Review [troubleshooting guide](TROUBLESHOOTING.md)
4. Ask in [discussions](https://github.com/yourusername/convoscope/discussions)
5. Open a new issue with:
   - Your OS and Python version
   - Complete error message
   - Steps to reproduce
   - Sample data (with PII removed)

---

For more examples, see the [examples](../examples/) directory.
