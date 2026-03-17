# 🚀 Deployment Guide

## Quick Start (Tomorrow)

### Windows Users
Double-click `start.bat` in the project folder. This will:
- Automatically start the backend API on port 8000
- Automatically start the frontend on port 3001
- Open both in your default browser

### macOS/Linux Users
Run in terminal:
```bash
bash start.sh
```

## Step-by-Step Setup

### 1. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 2. Configure Environment

Edit `backend/.env`:
```
# LLM Provider (required - pick ONE)
OPENAI_API_KEY=your_key_here
# OR
ANTHROPIC_API_KEY=your_key_here
# OR leave blank to use Ollama (run locally with: ollama serve)

# LinkedIn Auto-Posting (optional - for future use)
BUFFER_ACCESS_TOKEN=get_from_https://publish.buffer.com/settings/api
```

### 3. Run Locally

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Then open: http://localhost:3001

## Features Ready to Use

### Search & Generate Content
1. Click on trending topics or search for your own (e.g., "RAG", "Fine-tuning", "Prompt Engineering")
2. ✅ AI automatically researches the topic
3. ✅ Generates 4 professional LinkedIn posts
4. ✅ Optional: Include topic-specific images
5. ✅ Select which posts to publish
6. ✅ Automatic scheduling (Mon-Thu pattern)

### Auto-Posting to LinkedIn
When you add your Buffer API token:
1. Selected posts automatically schedule to LinkedIn
2. Optimal times: Mon 9am, Tue 2pm, Wed 10am, Thu 3pm
3. Buffer handles all LinkedIn posting

## API Endpoints

### Content Generation
- `POST /api/research-and-post` - Search topic, generate posts
- `GET /api/trending-topics` - Get trending AI topics worldwide

### Example Usage
```bash
# Search and generate posts
curl -X POST "http://localhost:8000/api/research-and-post?topic=RAG&with_images=true"

# Get trending topics
curl "http://localhost:8000/api/trending-topics"

# Health check
curl "http://localhost:8000/health"
```

## Production Deployment

### Using Heroku (Free Tier)
```bash
# Initialize production (if needed)
heroku create your-app-name
git push heroku main
```

### Using Railway / Render
1. Connect your GitHub repo
2. Deploy backend to Railway/Render port 8000
3. Deploy frontend to Vercel
4. Update frontend API URL in `frontend/src/App.tsx`:
   ```typescript
   const API_URL = 'https://your-api.railway.app';
   ```

## Troubleshooting

**Backend won't start:**
- Kill existing Python: `taskkill /F /IM python.exe` (Windows)
- Check port 8000 is free: `netstat -ano | findstr :8000`

**Frontend not connecting to backend:**
- Check `API_URL` in `frontend/src/App.tsx` matches your backend

**No trending topics loading:**
- Trending feature uses HackerNews/Reddit APIs (falls back to defaults)
- No authentication required

**Posts not generating:**
- Ensure you have an LLM provider configured in `.env`
- Check `OPENAI_API_KEY` or set up Ollama locally

## Next Steps

1. **Tomorrow:** Open the app and start searching/posting
2. **This Week:** Add Buffer token for auto-posting
3. **This Month:** Push to GitHub and deploy
4. **Long Term:** Customize content strategy based on analytics

## Support

- Backend API Docs: http://localhost:8000/docs (when running)
- Check logs for any errors
- Contact support through GitHub Issues
