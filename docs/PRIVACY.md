# Privacy & Security Guide

ConvoScope is designed with privacy as a core principle. This document explains how your data is protected and what you can do to ensure maximum privacy.

## Core Privacy Principles

### 1. Local-Only Processing
**All analysis happens on your machine.**
- No data sent to external servers
- No cloud processing
- No third-party analytics
- No telemetry or tracking

### 2. PII Redaction by Default
**Personal information is automatically removed.**
- Enabled by default (not opt-in)
- Runs before any analysis
- Consistent across all outputs
- Configurable if needed

### 3. Data Minimization
**Only process what's necessary.**
- Content preview limited to 300 characters
- Full text never stored in outputs
- Aggregate statistics instead of raw data
- Optional feature disabling

### 4. User Control
**You decide what gets processed.**
- Toggle privacy features
- Delete outputs at any time
- Choose what to export
- Control retention

## What Gets Protected

### Automatic PII Redaction

ConvoScope automatically detects and redacts:

#### Email Addresses
```
Original: "Contact me at john.doe@example.com"
Redacted: "Contact me at [EMAIL_REDACTED]"
```

#### Phone Numbers
All formats including:
```
555-123-4567 → [PHONE_REDACTED]
(555) 123-4567 → [PHONE_REDACTED]
+1-555-123-4567 → [PHONE_REDACTED]
555.123.4567 → [PHONE_REDACTED]
```

#### Social Security Numbers
```
123-45-6789 → [SSN_REDACTED]
```

#### Credit Card Numbers
```
4111 1111 1111 1111 → [CREDIT_CARD_REDACTED]
4111-1111-1111-1111 → [CREDIT_CARD_REDACTED]
```

#### Physical Addresses
```
123 Main Street → [ADDRESS_REDACTED]
456 Oak Avenue → [ADDRESS_REDACTED]
```

#### IP Addresses
```
192.168.1.1 → [IP_ADDRESS_REDACTED]
```

#### API Keys & Tokens
Long alphanumeric strings:
```
sk_live_51H8xB2... → [API_KEY_REDACTED]
```

### Entity Hashing

Instead of simple redaction, some entities are consistently hashed to preserve analytical patterns:

#### Person Names
```
Original mentions:
- "John Smith said..."
- "I spoke with John Smith"
- "John Smith's idea"

Hashed output:
- "[PERSON_NAME_a1b2c3d4] said..."
- "I spoke with [PERSON_NAME_a1b2c3d4]"
- "[PERSON_NAME_a1b2c3d4]'s idea"
```

**Why hashing instead of redaction?**
- Preserves relationship patterns
- Enables frequency analysis
- Maintains conversation flow
- Consistent anonymization

#### Organizations (Optional)
Can be configured to hash company names while preserving patterns.

## Privacy Configuration

### Default Settings

```python
# Privacy enabled by default
analyzer = AdvancedConversationAnalyzer(
    'export.json',
    enable_privacy=True  # Default
)
```

### Disabling Privacy (Not Recommended)

```python
# Only use if you're sure data contains no PII
analyzer = AdvancedConversationAnalyzer(
    'export.json',
    enable_privacy=False
)
```

Or via command line:
```bash
python src/advanced_analyzer.py export.json output --no-privacy
```

**Warning**: Disabling privacy redaction will include raw content in outputs. Only use this if:
- You're certain there's no PII in conversations
- You're processing in a secure environment
- You need full text for specific analysis
- You'll delete outputs after review

### Custom Privacy Patterns

Add your own PII patterns:

```python
from src.advanced_analyzer import AdvancedConversationAnalyzer

analyzer = AdvancedConversationAnalyzer('export.json')

# Add custom pattern
analyzer.privacy_patterns['employee_id'] = r'\bEMP\d{6}\b'
analyzer.privacy_patterns['project_code'] = r'\bPROJ-\d{4}\b'

# Now these will be redacted as:
# EMP123456 → [EMPLOYEE_ID_REDACTED]
# PROJ-1234 → [PROJECT_CODE_REDACTED]
```

## Data Security

### Storage Security

**Where data is stored:**
1. **Input**: Your downloaded export file
   - Store in encrypted folder if possible
   - Delete after analysis if desired
   - Never commit to version control

2. **Outputs**: Generated analysis files
   - CSV, Excel, reports, visualizations
   - Contain redacted data
   - Safe to share externally (after review)

3. **Temporary**: None
   - No temp files created
   - All processing in memory
   - Clean shutdown

### Recommendations

**For maximum security:**

1. **Encrypt storage**
   ```bash
   # On macOS - create encrypted disk image
   hdiutil create -size 1g -encryption AES-256 -fs HFS+ -volname "Secure" secure.dmg
   
   # On Linux - use encrypted directory
   sudo cryptsetup luksFormat /dev/sdX
   ```

2. **Secure deletion**
   ```bash
   # After analysis, securely delete original
   # macOS/Linux:
   shred -uvz conversations.json
   
   # Windows:
   cipher /w:C:\path\to\file
   ```

3. **Encrypted backups**
   - Use encrypted cloud storage if backing up
   - Enable device encryption
   - Use strong passwords

4. **Access control**
   ```bash
   # Restrict file permissions
   chmod 600 conversations.json
   chmod 600 *analysis*.csv
   ```

### Network Security

**ConvoScope never:**
- Opens network connections
- Makes HTTP/HTTPS requests
- Sends data anywhere
- Phones home
- Checks for updates automatically

**Verification:**
```bash
# Monitor network activity during analysis
# On macOS/Linux:
sudo tcpdump -i any 'host your.ip.address'

# You should see NO traffic from Python process
```

## Privacy in Outputs

### What's Included in Outputs

**CSV/Excel files contain:**
- Redacted content previews (300 chars max)
- Aggregate statistics
- Anonymized entity references
- Metadata (timestamps, counts)
- Analysis results (topics, sentiment)

**What's NOT included:**
- Full conversation text
- Unredacted PII
- User identifiers
- System information
- File paths

### Reviewing Outputs Before Sharing

**Before sharing analysis outputs:**

1. **Open the CSV/Excel**
   - Scan the `content_preview` column
   - Look for any missed PII
   - Check `pii_redactions` column

2. **Review visualizations**
   - Charts contain aggregated data only
   - No individual messages shown
   - Safe to share

3. **Check reports**
   - Text reports contain statistics
   - No raw conversation content
   - Review for context clues

4. **Example review checklist:**
   ```python
   import pandas as pd
   
   df = pd.read_csv('analysis.csv')
   
   # Check for potential PII leaks
   def check_pii(text):
       patterns = [
           r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',  # Names
           r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
           r'\b\w+@\w+\.\w+\b',  # Email
       ]
       for pattern in patterns:
           if re.search(pattern, str(text)):
               return True
       return False
   
   # Scan content previews
   leaked = df[df['content_preview'].apply(check_pii)]
   if len(leaked) > 0:
       print(f"⚠️  Found {len(leaked)} potential PII leaks")
       print(leaked[['content_preview']])
   else:
       print("✓ No obvious PII found")
   ```

## Compliance

### GDPR Compliance

ConvoScope helps with GDPR compliance:

**Right to Access**: ✓
- You control your data export
- All data viewable locally

**Right to Erasure**: ✓
- Delete files at any time
- No external copies

**Data Minimization**: ✓
- Only processes what's needed
- Automatic PII redaction

**Privacy by Design**: ✓
- Privacy features default-on
- Local-only processing

**Data Protection**: ✓
- No data transmission
- Encrypted storage recommended

### CCPA Compliance

**Transparency**: ✓
- Open source code
- Clear data handling

**No Sale**: ✓
- Data never sold or shared
- Fully local processing

**Deletion Rights**: ✓
- Full control over data
- Easy to delete

## Best Practices

### For Personal Use

1. **Enable all privacy features** (default)
2. **Review outputs** before sharing
3. **Store securely** (encrypted volume)
4. **Delete when done** (if sensitive)
5. **Keep software updated**

### For Team/Organization Use

1. **Establish data handling policy**
   - Who can run analysis
   - Where data is stored
   - Retention policies

2. **Use dedicated secure workstation**
   - Encrypted disk
   - No network access during processing
   - Restricted physical access

3. **Audit trail**
   ```bash
   # Log analysis runs
   echo "$(date): Analyzed conversations.json" >> analysis.log
   ```

4. **Regular security reviews**
   - Verify privacy settings
   - Check for PII leaks
   - Update patterns as needed

### For Research/Academic Use

1. **IRB approval** for human subjects
2. **Informed consent** from participants
3. **Anonymization validation**
   - Manual review of sample outputs
   - Statistical disclosure control
4. **Secure aggregation**
   - Only share aggregate statistics
   - k-anonymity for small groups
5. **Data retention limits**
   - Delete after research complete
   - Documented retention policy

## Privacy Incident Response

If you discover unredacted PII in outputs:

1. **Immediate actions:**
   - Stop sharing the file
   - Delete exposed copies
   - Notify anyone who received it

2. **Investigation:**
   - Identify what was exposed
   - How it happened (missed pattern?)
   - Scope of exposure

3. **Remediation:**
   - Update privacy patterns
   - Rerun analysis with fixes
   - Generate clean outputs

4. **Prevention:**
   - Document the incident
   - Update patterns
   - Improve review process
   - Consider additional validation

## Questions & Support

### Common Questions

**Q: Is my data really safe?**
A: Yes. All processing is local, code is open source for verification, and no network connections are made.

**Q: Can I verify no data is sent out?**
A: Yes. Monitor network traffic during analysis or run in air-gapped environment.

**Q: What if I find PII in outputs?**
A: Report it as an issue, update patterns, and rerun analysis. We'll fix detection.

**Q: Can I use this for regulated data?**
A: Check with your compliance team. Tool supports privacy but you're responsible for your use case.

**Q: Is hashing reversible?**
A: No. We use one-way cryptographic hashing. Original values cannot be recovered.

### Getting Help

Privacy concerns? Contact:
- GitHub Issues: [Security issues](https://github.com/yourusername/convoscope/issues)
- Email: [Your security contact]
- Discussions: [Privacy & Security](https://github.com/yourusername/convoscope/discussions)

---

**Remember**: Privacy is a shared responsibility. ConvoScope provides tools, but you must use them appropriately for your context.
