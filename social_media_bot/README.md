# Sisi Lola Social Media Bot

## Overview

Autonomous social media bot system for Sisi Lola that:
- Monitors comments on YouTube and Instagram
- Generates contextual, brand-aligned responses using N-ATLaS
- Logs all interactions for continuous model improvement
- Respects platform API limits and safety guidelines

## Architecture

```
social_media_bot/
├── youtube/
│   ├── youtube_bot.py          # YouTube Data API integration
│   └── requirements.txt         # YouTube-specific dependencies
├── instagram/
│   ├── instagram_bot.py         # Instagram Graph API integration
│   └── requirements.txt         # Instagram-specific dependencies
├── common/
│   ├── base_bot.py             # Shared bot functionality
│   └── response_generator.py   # N-ATLaS integration
└── README.md                    # This file
```

## Features

### YouTube Bot
- **Comment Monitoring**: Fetches recent comments using YouTube Data API v3
- **Intent Classification**: Categorizes comments (question, praise, spam, toxic)
- **Smart Replies**: Generates Sisi Lola-style responses
- **Training Data Ingestion**: Logs all interactions for model fine-tuning
- **Rate Limiting**: Respects API quotas (10,000 units/day)
- **Safety**: Filters toxic/spam content

### Instagram Bot
- **Comment/DM Monitoring**: Uses Instagram Graph API
- **Business Account Integration**: Requires Instagram Business/Creator account
- **Reply Automation**: Responds to comments and messages
- **Story Mention Tracking**: Monitors brand mentions
- **Engagement Metrics**: Tracks likes, shares, saves

## Setup

### Prerequisites

1. **YouTube Setup**:
   ```bash
   # Install Google API client
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   
   # Set environment variables
   export YOUTUBE_API_KEY="your-api-key"
   export SISILOLA_CHANNEL_ID="your-channel-id"
   ```

2. **Instagram Setup**:
   ```bash
   # Install Facebook SDK
   pip install facebook-sdk requests
   
   # Set environment variables
   export INSTAGRAM_ACCESS_TOKEN="your-long-lived-token"
   export INSTAGRAM_BUSINESS_ACCOUNT_ID="your-account-id"
   ```

3. **N-ATLaS Model**:
   ```bash
   export NATLAS_API_ENDPOINT="https://api.sisilola.io/natlas"
   export NATLAS_API_KEY="your-model-api-key"
   ```

### Installation

```bash
# Install all dependencies
pip install -r requirements.txt

# Test YouTube bot
python youtube/youtube_bot.py

# Test Instagram bot
python instagram/instagram_bot.py
```

## Usage

### YouTube Bot

```python
from social_media_bot.youtube import YouTubeBot

# Initialize
bot = YouTubeBot(
    api_key="your-key",
    channel_id="your-channel",
    model_endpoint="https://api.sisilola.io/natlas"
)

# Process comments (dry run - no actual posting)
stats = bot.process_comments(dry_run=True)
print(f"Processed {stats['fetched']} comments")
print(f"Would respond to {stats['responded']} comments")

# Process and post replies
stats = bot.process_comments(dry_run=False)
```

### Instagram Bot

```python
from social_media_bot.instagram import InstagramBot

bot = InstagramBot(
    access_token="your-token",
    business_account_id="your-id"
)

stats = bot.process_comments(dry_run=False)
```

### Automated Scheduling

Use cron or GitHub Actions to run periodically:

```bash
# Crontab example - run every 15 minutes
*/15 * * * * cd /path/to/project && python social_media_bot/youtube/youtube_bot.py
```

Or use the provided GitHub Actions workflow (see `.github/workflows/social_bot.yml`)

## Training Data Pipeline

All bot interactions are automatically logged to:
```
ml_training/data/chat_logs/chat_logs_raw.jsonl
```

To process into training data:

```bash
# Curate logs into training format
python ml_training/curate_training_data.py

# Output: ml_training/data/sisi_lola_chat_instructions.jsonl
```

Training data includes:
- User comment/message
- Bot response
- Platform (YouTube/Instagram)
- Intent classification
- Language detection
- Engagement metrics (likes, etc.)

## Safety & Moderation

### Built-in Filters

1. **Toxic Content Detection**:
   - Hate speech keywords
   - Threatening language
   - Harassment patterns

2. **Spam Detection**:
   - Promotional keywords
   - Link spam
   - Repeated messages

3. **Action Policy**:
   - Toxic/spam → Hide or ignore
   - Questions → Respond
   - Praise → Respond with gratitude
   - Unclear → Safe default response

### Manual Review

All auto-responses should be reviewed periodically:

```bash
# Check recent logs
tail -100 ml_training/data/chat_logs/chat_logs_raw.jsonl | jq

# Filter by rating
jq 'select(.rating >= 4)' ml_training/data/chat_logs/chat_logs_raw.jsonl
```

## Rate Limits

### YouTube
- **Daily Quota**: 10,000 units
- **Comment List**: 1 unit per request
- **Comment Insert**: 50 units per reply
- **Recommendation**: Max ~180 replies/day

### Instagram
- **Rate Limit**: 200 API calls/hour per user
- **Comment Read**: ~1 call per post
- **Comment Reply**: ~1 call per reply
- **Recommendation**: Check every 15-30 minutes

## Monitoring

### Metrics to Track

1. **Engagement**:
   - Comments responded to
   - Average response time
   - Follow-up engagement

2. **Quality**:
   - User ratings (if implemented)
   - Positive vs. negative reactions
   - Report/hide rate

3. **Training**:
   - Interactions logged
   - Training examples generated
   - Model performance improvement

### Dashboards

Create a simple dashboard:

```python
from ml_training.conversation_logger import ConversationLogger

logger = ConversationLogger()
recent = logger.get_recent_logs(limit=1000)

# Calculate stats
platforms = {}
for log in recent:
    platform = log.get('metadata', {}).get('platform', 'unknown')
    platforms[platform] = platforms.get(platform, 0) + 1

print(f"Interactions by platform: {platforms}")
```

## Integration with N-ATLaS

The bots use N-ATLaS for response generation:

### API Format

```python
import requests

response = requests.post(
    "https://api.sisilola.io/natlas/chat",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "messages": [
            {"role": "system", "content": "You are Sisi Lola..."},
            {"role": "user", "content": "How do I learn DevSecOps?"}
        ],
        "max_tokens": 150,
        "temperature": 0.8,
        "top_p": 0.9
    }
)

reply = response.json()["choices"][0]["message"]["content"]
```

### Fallback Strategies

1. **API Timeout**: Use pre-defined templates
2. **Rate Limit Hit**: Queue for later processing
3. **Error Response**: Log and alert, don't post

## Roadmap

- [x] Basic YouTube comment monitoring
- [x] Training data ingestion pipeline
- [x] Intent classification system
- [ ] Full N-ATLaS API integration
- [ ] Instagram bot implementation
- [ ] Real-time sentiment analysis
- [ ] A/B testing framework
- [ ] Advanced RL-based optimization
- [ ] Multi-language support (Yoruba, Igbo, Pidgin)
- [ ] Video reply generation
- [ ] Community engagement metrics

## Troubleshooting

### Common Issues

**"API key invalid"**
- Verify environment variables are set
- Check API console for key status
- Regenerate if necessary

**"Quota exceeded"**
- Wait 24 hours for reset
- Reduce polling frequency
- Prioritize high-engagement posts

**"No comments fetched"**
- Check channel ID is correct
- Verify OAuth scopes (if using)
- Ensure videos have comments enabled

## Contributing

To add new platforms or features:

1. Create a new module in `social_media_bot/`
2. Inherit from `BaseBot` (in `common/`)
3. Implement required methods
4. Add tests
5. Update this README

## License

Proprietary - BAMG Studio

## Contact

For issues or questions:
- GitHub Issues: https://github.com/BAMG-Studio/sisi-lola-project/issues
- Email: seun.beaconagiletech@gmail.com
