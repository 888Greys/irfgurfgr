# AI Readiness Assessment

A comprehensive AI readiness assessment tool for Kenyan businesses, featuring an intuitive React frontend and a powerful FastAPI backend with AI-powered guidance.

## 🌟 Features

- **21 Assessment Questions** across 6 key categories
- **AI-Powered Guidance** with Kenya-specific context
- **Real-time Chat Interface** for personalized help
- **Vertical Progress Tracking** with animated indicators
- **Business Information Collection** with location-based insights
- **Structured AI Responses** with proper formatting
- **FastAPI Backend** with LangChain agents
- **Modern React Frontend** with TypeScript and Tailwind CSS

## 📋 Categories Assessed

1. **Data Infrastructure** - Data collection, storage, and quality
2. **Technology Infrastructure** - Cloud, connectivity, and digital tools
3. **Human Resources & Skills** - AI talent and training programs
4. **Business Process Maturity** - Digital transformation and automation
5. **Strategic & Financial Readiness** - AI strategy and budget planning
6. **Regulatory & Compliance Readiness** - Data protection and legal compliance

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (Backend)
- **Node.js 18+** (Frontend)
- **Git**

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/888Greys/irfgurfgr.git
   cd irfgurfgr
   ```

## 🐍 Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the backend directory:
   ```env
   # Required: Choose one LLM provider
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   CEREBRAS_API_KEY=your_cerebras_api_key_here

   # Optional: Database configuration (uses JSON files by default)
   # DATABASE_URL=your_database_url_here
   ```

5. **Run the backend server:**
   ```bash
   python api_server.py
   ```

   The backend will start on `http://localhost:8000`

## ⚛️ Frontend Setup

1. **Open a new terminal and navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

   The frontend will start on `http://localhost:3000`

## 🌐 Usage

1. **Access the application:**
   Open your browser and go to `http://localhost:3000`

2. **Start Assessment:**
   - Fill in your business information
   - Answer the 21 assessment questions
   - Use the AI chat for guidance on each question
   - View your progress with the vertical indicator

3. **AI Guidance:**
   - Click on any question to get AI-powered explanations
   - Ask follow-up questions in the chat interface
   - Receive structured responses with tips and Kenya-specific context

## 🔧 API Endpoints

### Assessment Management
- `POST /api/assessment/start` - Start a new assessment
- `GET /api/assessment/{assessment_id}/next` - Get next question
- `POST /api/assessment/{assessment_id}/answer` - Submit answer
- `POST /api/assessment/{assessment_id}/guidance` - Get AI guidance

### Data Models
- **Business Info**: name, industry, size, location
- **Questions**: 21 structured questions with scoring rubrics
- **Guidance**: AI responses with explanation, tips, and context

## 🏗️ Architecture

### Backend (FastAPI)
- **LangChain Agents**: Assessment guide, scoring, and recommendation agents
- **LLM Integration**: OpenAI GPT-4 or Cerebras models
- **Data Persistence**: JSON-based storage (easily replaceable with database)
- **Kenya Context**: Localized content and regulatory guidance

### Frontend (Next.js)
- **React 19** with TypeScript
- **Tailwind CSS v4** for styling
- **Framer Motion** for animations
- **React Markdown** for formatted AI responses
- **Responsive Design** with mobile-first approach

## 🔐 Environment Variables

### Backend (.env)
```env
# LLM Configuration (choose one)
OPENAI_API_KEY=sk-your-openai-key
CEREBRAS_API_KEY=your-cerebras-key

# Optional Database
DATABASE_URL=postgresql://user:pass@localhost/db
```

### Frontend
No environment variables required for development. API calls are made to `http://localhost:8000`.

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest ai_readiness_assessment/tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🚀 Production Deployment

### Backend Deployment
```bash
# Build and run with gunicorn
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment
```bash
cd frontend
npm run build
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built for Kenyan businesses to assess AI readiness
- Uses modern web technologies and AI best practices
- Designed with user experience and accessibility in mind

## 📞 Support

For questions or support, please open an issue on GitHub or contact the development team.

---

**Happy assessing! 🎯**</content>
<parameter name="filePath">README.md