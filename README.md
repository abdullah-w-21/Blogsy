# Blogsy 🚀

A professional AI-powered blog post generator built with Streamlit, CrewAI, and Groq LLM. Create high-quality, engaging blog content with a team of AI agents working together to plan, write, and edit your posts.


## Features ✨

- **AI Agent Collaboration**: Utilizes three specialized AI agents:
  - Strategic Content Planner
  - Expert Content Creator
  - Senior Content Editor

- **Real-time Generation**: Watch the creative process unfold as agents work together
- **Comprehensive Research**: Integrates Wikipedia for thorough topic research
- **Professional Output**: Generates well-structured, SEO-optimized blog posts
- **Usage Analytics**: Track content generation metrics and performance
- **Export Options**: Download generated content in Markdown format
- **Interactive UI**: User-friendly interface built with Streamlit

## Technology Stack 🛠️

- **Frontend**: Streamlit
- **AI Framework**: CrewAI
- **Language Model**: Groq (llama-3.3-70b-versatile)
- **Research Tools**: Wikipedia API
- **Data Storage**: JSON-based local storage
- **Environment**: Python 3.x

## Installation 🔧

1. Clone the repository:
```bash
git clone https://github.com/abdullah-w-21/Blogsy.git
cd Blogsy
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file or set up Streamlit secrets with:
```
GROQ_API_KEY=your_groq_api_key
```

4. Run the application:
```bash
streamlit run app.py
```

## Usage 📝

1. Enter your blog post details:
   - Topic
   - Keywords (comma-separated)
   - Desired word count
   - Key points to cover

2. Click "Generate Blog Post ✨"

3. Monitor the generation process:
   - View real-time research progress
   - Watch AI agents collaborate
   - Track content development stages

4. Review and download the final output:
   - Read the generated blog post
   - Check content metadata
   - View usage statistics
   - Download in Markdown format

## Features in Detail 🔍

### Content Planning
- Trend analysis
- Audience targeting
- SEO optimization
- Content structure planning

### Content Creation
- EEAT principle implementation
- Data-driven insights
- Engaging narratives
- Professional tone

### Content Editing
- Grammar and style checks
- Flow optimization
- Fact verification
- Final polish

## Architecture 🏗️

The application follows a three-agent architecture:

1. **Planner Agent**: Develops content strategy and research
2. **Writer Agent**: Creates initial content draft
3. **Editor Agent**: Refines and polishes the content

Each agent uses the Groq LLM and specialized tools for their tasks.

## Data Storage 📊

- **Usage Statistics**: Tracked in `usage_stats.json`
- **Generated Content**: Stored in `generated_content.json`
- **Metrics Tracked**:
  - Generation time
  - Content length
  - Topic distribution
  - Performance trends

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- CrewAI framework
- Groq LLM
- Streamlit community
- Wikipedia API

## Contact 📧

Abdullah Wasim - [GitHub](https://github.com/abdullah-w-21)

Project Link: [https://github.com/abdullah-w-21/Blogsy](https://github.com/abdullah-w-21/Blogsy)

---

Made with ❤️ by [Abdullah Wasim](https://github.com/abdullah-w-21)
