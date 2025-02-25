# AI-Powered Social Media Assistant

A Python-based tool that leverages OpenAI's GPT to automate and enhance social media content management across multiple platforms. Perfect for content creators, social media managers, and developers exploring AI content generation.

## 🚀 Features

- **Content Extraction**: Automatically extract and analyze content from URLs
- **AI-Powered Generation**: Create platform-optimized posts for:
  - X (with character limit and hashtag optimization)
  - LinkedIn (professional tone and formatting)
  - Facebook (engagement-focused content)
- **Multi-language Support**: Generate content in 8 different languages including English, Spanish, French, German, Italian, Portuguese, Dutch, and Romanian
- **Smart Scheduling**: Plan and schedule posts for optimal timing with automated publishing
- **Background Scheduler**: Runs in a separate thread to manage scheduled posts without interrupting the main application
- **Content Library**: Maintain a persistent, organized content database with JSON storage
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

## 💻 Usage

Run the main script to start the social media assistant:
```bash
python src/social_media_assistant.py
```

The interactive menu will guide you through:
- Processing new URLs for content
- Generating platform-specific posts in your preferred language
- Managing your content library
- Scheduling posts with specific date and time
- Viewing scheduled posts and their status
- Saving/loading your content database

## 📅 Scheduling System

The assistant includes a powerful scheduling system that:
- Runs in the background using a dedicated thread
- Allows scheduling posts for specific times
- Automatically publishes content at scheduled times
- Persists scheduled posts between application restarts
- Provides status tracking for scheduled/published content

## 📂 Project Structure

```
social-media-ai/
├── src/                           # Source code directory
│   ├── __init__.py                # Python package initializer
│   └── social_media_assistant.py  # Main application logic
├── .env                           # Environment variables configuration
├── .gitignore                     # Git ignore rules
├── requirements.txt               # Project dependencies
└── README.md                      # Project documentation
```

## 📦 Dependencies

- **openai**: Interface with OpenAI's GPT models
- **requests** & **beautifulsoup4**: Web scraping and content extraction
- **python-dotenv**: Environment variable management
- **schedule**: Handling post scheduling
- **threading**: Running scheduler in background

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.