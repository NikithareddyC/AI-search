# Frontend Dashboard - React

## Quick Start

### Prerequisites
- Node.js 16+ installed
- Backend running on http://localhost:8000

### Installation & Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Opens automatically at http://localhost:3000
```

### Build for Production

```bash
npm run build

# Creates optimized build in 'build' folder
# Deploy the 'build' folder to your hosting
```

---

## Features

### Home Tab
- **Dashboard:** View key metrics (followers, posts, engagement)
- **Research:** Enter any AI/ML topic to auto-generate and post
- **Batch Research:** Click to research 4 topics at once
- **Generated Content:** Preview created posts before manual posting

### Content Tab
- **Post History:** See all researched topics
- **Post Count:** How many posts created per topic
- **Dates:** When each topic was researched

### Growth Tab
- **Metrics:** Current followers, posts, engagement
- **Predictions:** Follower growth for 1 week, month, 3 months, 6 months
- **Growth Tips:** Best practices for LinkedIn growth

---

## Customization

### Change Backend URL
Edit `src/App.tsx`:
```typescript
const API_URL = 'http://localhost:8000';

// Change to:
const API_URL = 'https://your-backend-url.com';
```

### Customize Themes
Edit `src/App.css`:
```css
:root {
  --primary: #0066cc;        /* Change main color */
  --success: #00cc66;        /* Change success color */
  --danger: #ff3333;         /* Change error color */
}
```

### Add More Features
The dashboard is built with React + Axios, making it easy to:
- Add charts using Chart.js or Recharts
- Integrate more endpoints
- Add user authentication
- Store preferences locally
- Add dark mode
- Export analytics to CSV

---

## Architecture

```
frontend/
├── src/
│   ├── App.tsx              # Main component
│   ├── App.css              # Styling
│   └── index.tsx            # React entry point
├── public/
│   └── index.html           # HTML template
└── package.json             # Dependencies
```

---

## Key Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Axios** - HTTP client
- **CSS3** - Responsive styling

---

## Deployment

### Deploy to Vercel (Easiest)
```bash
npm install -g vercel
vercel

# Follow prompts, connect your repo, deploy!
```

### Deploy to Netlify
```bash
npm run build
# Upload 'build' folder to Netlify
```

### Deploy to GitHub Pages
```bash
npm run build
# Upload 'build' to gh-pages branch
```

---

## Troubleshooting

### Frontend not connecting to backend
1. Ensure backend is running on port 8000
2. Check browser console for errors (F12)
3. Verify API_URL in App.tsx
4. Try `http://127.0.0.1:8000` instead of `localhost`

### Build fails
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
npm start
```

### Port 3000 already in use
```bash
# Use a different port
npm start -- --port 3001
```

---

## Next Steps

1. **Customize:** Add your branding, colors, logo
2. **Extend:** Add charts, analytics visualizations
3. **Deploy:** Host on Vercel, Netlify, or GitHub Pages
4. **Share:** Let others use your growth platform!

---

For backend documentation, see [SETUP_GUIDE.md](../SETUP_GUIDE.md)
