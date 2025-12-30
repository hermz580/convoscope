# ConvoScope Examples

This directory contains examples and utilities for working with ConvoScope.

## Files

### generate_mock_data.py

Generates mock conversation data for testing ConvoScope without real Claude exports.

**Usage:**
```bash
python generate_mock_data.py
# Creates: mock_claude_export.json
```

**Then analyze:**
```bash
python ../src/advanced_analyzer.py mock_claude_export.json test_analysis --no-viz
```

### Future Examples

Coming soon:
- Custom pattern detection examples
- Integration with pandas workflows
- Database export examples
- Batch processing scripts
- Visualization customization
- Privacy pattern templates

## Contributing Examples

Have a useful example? Submit a PR with:
- Clear documentation
- Sample data (anonymized)
- Expected outputs
- Use case description
