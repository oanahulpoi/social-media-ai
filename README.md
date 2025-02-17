# AI-Powered Social Media Assistant

A Python-based tool that leverages OpenAI's GPT to automate and enhance social media content management across multiple platforms. Perfect for content creators, social media managers, and developers exploring AI content generation.

## 🚀 Features

- **Content Extraction**: Automatically extract and analyze content from URLs
- **AI-Powered Generation**: Create platform-optimized posts for:
  - Twitter (with character limit and hashtag optimization)
  - LinkedIn (professional tone and formatting)
  - Facebook (engagement-focused content)
- **Smart Scheduling**: Plan and schedule posts for optimal timing
- **Content Library**: Maintain a persistent, organized content database
- **Keyword Analysis**: AI-powered keyword and hashtag extraction
- **Type-Safe Code**: Fully typed with Python type hints for reliability

## 🛠️ Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/social-media-ai.git
   cd social-media-ai
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the root directory with your OpenAI API key**
   ```bash
   OPENAI_API_KEY=<your_openai_api_key>
   ```

5. 💻 **Usage**
   Run the main script to start the social media assistant:
   ```bash
   python src/social_media_assistant.py
   ```
   The interactive menu will guide you through:
   - Processing new URLs for content    
   - Generating platform-specific posts
   - Managing your content library
   - Scheduling posts
   - Saving/loading your content database


## 📂 Project Structure
social-media-ai/
├── src/
│   ├── __init__.py
│   └── social_media_assistant.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md


## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request