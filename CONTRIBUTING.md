# Contributing to ConvoScope

Thank you for your interest in contributing to ConvoScope! This document provides guidelines and instructions for contributing.

## Code of Conduct

### Our Principles
- **Ubuntu Philosophy**: "I am because we are" - we build for collective benefit
- **Privacy First**: Always respect user data and privacy
- **Liberation Technology**: Build tools that empower, not extract
- **Open Collaboration**: Welcome diverse perspectives and approaches

### Expected Behavior
- Be respectful and constructive
- Welcome newcomers and help them learn
- Focus on what's best for the community
- Show empathy towards others

## How to Contribute

### Reporting Bugs

**Before submitting a bug report:**
- Check existing issues to avoid duplicates
- Test with the latest version
- Gather relevant information (OS, Python version, error messages)

**When submitting:**
- Use a clear, descriptive title
- Provide steps to reproduce
- Include error messages and stack traces
- Describe expected vs actual behavior
- Include sample data if possible (with PII removed)

### Suggesting Features

**Good feature requests include:**
- Clear use case and motivation
- Detailed description of proposed functionality
- Examples of how it would work
- Consideration of privacy implications
- Potential implementation approach (optional)

### Code Contributions

#### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/convoscope.git
cd convoscope

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

#### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Write code**
   - Follow existing code style (Black formatting)
   - Add docstrings to functions and classes
   - Keep functions focused and modular
   - Preserve privacy-first architecture

3. **Add tests**
   ```bash
   # Add tests in tests/ directory
   pytest tests/test_your_feature.py
   ```

4. **Update documentation**
   - Update README if adding features
   - Add docstrings for new functions
   - Update relevant docs/ files

5. **Format and lint**
   ```bash
   black src/
   flake8 src/
   ```

#### Code Style Guidelines

**Python Style:**
- Follow PEP 8
- Use Black for formatting
- Maximum line length: 100 characters
- Use type hints where helpful
- Write descriptive variable names

**Documentation:**
- Clear, concise docstrings
- Include parameter descriptions
- Provide usage examples
- Update README for user-facing changes

**Example:**
```python
def analyze_sentiment(text: str, intensity: bool = False) -> Dict[str, float]:
    """
    Analyze sentiment of given text.
    
    Args:
        text: Input text to analyze
        intensity: If True, return intensity scores for each sentiment
        
    Returns:
        Dictionary mapping sentiment labels to confidence scores
        
    Example:
        >>> analyze_sentiment("This is great!")
        {'positive': 0.95, 'neutral': 0.05, 'negative': 0.0}
    """
    # Implementation
    pass
```

#### Commit Messages

Follow conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(quality): add response effectiveness scoring

Implements new metric to track how effective assistant responses
are based on user follow-up messages.

Closes #42
```

```
fix(privacy): improve email detection regex

Previous pattern missed emails with + symbols. Updated regex
to handle all valid email formats per RFC 5322.
```

### Pull Request Process

1. **Before submitting:**
   - Ensure all tests pass
   - Update documentation
   - Add your changes to CHANGELOG.md
   - Rebase on latest main branch

2. **Submit PR:**
   - Use descriptive title
   - Reference related issues
   - Describe what changed and why
   - Include screenshots for UI changes
   - Mark as draft if work in progress

3. **Review process:**
   - Maintainers will review within 1 week
   - Address feedback constructively
   - Keep discussion focused and technical
   - Be patient with the review process

4. **After approval:**
   - Maintainer will merge
   - Delete your branch
   - Celebrate! 🎉

## Development Guidelines

### Module Structure

When adding new analysis modules:

```python
"""
Module Name - Brief Description
Detailed explanation of module purpose
"""

class YourAnalyzer:
    """
    One-line description of analyzer
    
    Detailed explanation of what it analyzes and how
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize analyzer with optional configuration."""
        pass
    
    def analyze(self, data: pd.DataFrame) -> Dict:
        """
        Main analysis method.
        
        Args:
            data: Input dataframe with conversation data
            
        Returns:
            Dictionary containing analysis results
        """
        pass
```

### Privacy Considerations

**Always:**
- Process data locally
- Redact PII by default
- Use hashing for consistent anonymization
- Document what data is processed
- Make privacy features configurable
- Test with real PII patterns

**Never:**
- Send data to external services without explicit opt-in
- Store raw conversation text
- Log sensitive information
- Make privacy features opt-in (they should be default)

### Testing

**Test Coverage Goals:**
- Core functionality: 80%+
- Privacy features: 95%+
- New features: 70%+

**Test Types:**
```python
# Unit tests
def test_sentiment_detection():
    analyzer = SentimentAnalyzer()
    result = analyzer.detect("This is great!")
    assert result['sentiment'] == 'positive'

# Integration tests
def test_full_analysis_pipeline():
    analyzer = AdvancedConversationAnalyzer('test_data.json')
    analyzer.load_data()
    df = analyzer.parse_conversations_advanced()
    assert len(df) > 0
    assert 'sentiment' in df.columns

# Privacy tests
def test_pii_redaction():
    text = "Email me at test@example.com"
    redacted, _ = analyzer.redact_pii(text)
    assert "test@example.com" not in redacted
    assert "EMAIL_REDACTED" in redacted
```

### Performance Considerations

- Profile code for datasets >10K messages
- Optimize slow operations
- Use vectorization for pandas operations
- Consider memory usage for large datasets
- Add progress indicators for long operations

## Documentation

### Types of Documentation

1. **Code Comments**: Explain why, not what
2. **Docstrings**: API documentation
3. **README**: User-facing overview
4. **Guides**: Detailed how-to documents
5. **Examples**: Practical use cases

### Documentation Standards

- Write for users who are new to the tool
- Include code examples
- Keep language clear and concise
- Update docs with code changes
- Test all code examples

## Community

### Getting Help

- Check [documentation](docs/)
- Search [existing issues](https://github.com/yourusername/convoscope/issues)
- Ask in [discussions](https://github.com/yourusername/convoscope/discussions)
- Reach out to maintainers

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

## Questions?

Don't hesitate to ask! Open an issue with the `question` label or start a discussion.

---

**Thank you for contributing to ConvoScope!** Your efforts help build liberation infrastructure that serves communities rather than extracting from them.
