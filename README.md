# 🤖 AI Therapy Chat Bot

A compassionate Telegram bot powered by Groq that provides emotional support and music recommendations based on user mood. The bot creates a safe space for users to share their feelings and receive empathetic responses.

## 🌟 Features

- **Mood Check-ins**: Interactive mood rating system with emoji-based scale (1-10)
- **Empathetic Conversations**: AI-powered responses that acknowledge and validate user feelings
- **Music Therapy**: Personalized song recommendations based on emotional state
- **Follow-up Care**: Automated check-ins for users who reported low mood

## 🛠️ Tech Stack

- Python 3.12
- python-telegram-bot
- Groq API (Mixtral 8x7b)
- Azure Container Registry
- GitHub Actions for CI/CD

## 🚀 Getting Started

1. Clone the repository
```bash
git clone https://github.com/DiegoTheExplorar/DiegoWellness.git
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
```

4. Run the bot
```bash
python app.py
```

## 🐳 Docker Deployment

The bot can be deployed using Docker:

```bash
docker build -t therapy-bot \
  --build-arg BOT_TOKEN=your_telegram_bot_token \
  --build-arg GROQ_API_KEY=your_groq_api_key .
docker run therapy-bot
```

## 🔄 CI/CD Pipeline

The repository includes GitHub Actions workflows for:
- Automated builds on push to main branch
- Docker image pushing to Azure Container Registry
- Deployment automation

## 💡 Recommended Feature Additions

1. **Multi-language Support**
   - Implement language detection
   - Provide responses in the user's preferred language
   - Currently, bot can understand 
        1. English
        2. Spanish
        3. French
        4. German
        5. Italian

2. **Journaling Feature**
   - Allow users to maintain mood journals
   - Export journal entries

3. **Wellness Resources**
   - Integrate breathing exercises
   - Add guided meditation sessions
   - Provide crisis helpline information

4. **Exercise Integration**
   - Quick workout suggestions
   - Physical activity tracking
   - Movement reminders

5. **Expanded Media Support**
   - Video content recommendations
   - Podcast suggestions
   - Calming image galleries
   - Even let the user send images

6. **Customizable Check-ins**
   - User-defined check-in schedules
   - Customizable mood scales
   - Personalized follow-up preferences

## ⚠️ Disclaimer

This bot is not a replacement for professional mental health care. If you're experiencing serious mental health issues, please seek professional help. In case of emergency, contact your local emergency services or crisis helpline.
