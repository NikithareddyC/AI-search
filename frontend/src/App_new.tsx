import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8000';

export default function App() {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      console.log('Searching for:', topic);
      const response = await axios.post(
        `${API_URL}/api/research-and-post?topic=${encodeURIComponent(topic)}&auto_post=false`,
        {}
      );

      console.log('Response:', response.data);
      setResults(response.data);
      setError('');
    } catch (err: any) {
      console.error('Error:', err);
      setError(err.message || 'Failed to search');
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="navbar">
        <div className="nav-brand">
          <h1>🚀 AI Content Generator</h1>
          <p>Research AI/ML topics and generate LinkedIn posts</p>
        </div>
      </div>

      <div className="main-content">
        <div className="search-section">
          <h2>Search Topic</h2>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="e.g., what is LLM, RAG, Fine-tuning..."
            disabled={loading}
            autoFocus
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading ? 'Searching...' : 'Search & Generate'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {results && results.status === 'success' && (
          <div className="results-section">
            <h2>✅ Generated Posts for "{results.topic}"</h2>
            <div className="posts-container">
              {results.content?.content_pieces && results.content.content_pieces.length > 0 ? (
                results.content.content_pieces.map((post: any, idx: number) => (
                  <div key={idx} className="post-card">
                    <div className="post-type">{post.type}</div>
                    <p className="post-text">{post.text}</p>
                    <div className="hashtags">
                      {post.hashtags && post.hashtags.map((tag: string, i: number) => (
                        <span key={i}>#{tag}</span>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <p>No posts generated</p>
              )}
            </div>
            <button className="post-btn" onClick={() => alert('Ready for LinkedIn posting!')}>
              📤 Post to LinkedIn
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
