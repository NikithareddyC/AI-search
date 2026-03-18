import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// API URL configuration for different environments
const API_URL = 
  typeof window !== 'undefined' && window.location.hostname === 'localhost' 
    ? 'http://localhost:8000'  // Local development
    : import.meta.env.VITE_API_URL || '';  // Production (Vercel uses VITE_API_URL, or relative if not set)

export default function App() {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [error, setError] = useState('');
  const [withImages, setWithImages] = useState(false);
  const [selectedPosts, setSelectedPosts] = useState<boolean[]>([]);
  const [posting, setPosting] = useState(false);
  const [postingSchedule, setPostingSchedule] = useState<any>(null);
  const [trendingTopics, setTrendingTopics] = useState<any[]>([]);

  // Load trending topics on component mount
  useEffect(() => {
    const fetchTrendingTopics = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/trending-topics`);
        if (response.data.topics) {
          setTrendingTopics(response.data.topics);
        }
      } catch (err) {
        console.error('Failed to fetch trending topics:', err);
      }
    };

    fetchTrendingTopics();
  }, []);

  const handlePostToLinkedIn = async () => {
    const selectedIndices = selectedPosts
      .map((selected, idx) => selected ? idx : -1)
      .filter(idx => idx !== -1);
    
    if (selectedIndices.length === 0) {
      setError('❌ Please select at least one post');
      return;
    }

    setPosting(true);
    setError('');

    try {
      const selectedPostsData = selectedIndices.map(idx => results.content.content_pieces[idx]);
      
      const response = await axios.post(
        `${API_URL}/api/post-selected`,
        {
          topic: results.topic,
          posts: selectedPostsData,
          with_images: withImages
        }
      );

      console.log('Posting response:', response.data);
      setPostingSchedule(response.data);
      setError('');
    } catch (err: any) {
      const msg = err.response?.data?.error || err.message || 'Failed to schedule posts';
      setError(`❌ Error: ${msg}`);
    } finally {
      setPosting(false);
    }
  };

  const handleSearch = async () => {
    if (!topic.trim()) {
      setError('❌ Please enter a topic');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/research-and-post?topic=${encodeURIComponent(topic)}&auto_post=false&with_images=${withImages}`,
        {}
      );

      console.log('API Response:', response.data);
      setResults(response.data);
      // Initialize post selection checkboxes (all unchecked by default)
      setSelectedPosts(new Array(response.data.content?.content_pieces?.length || 0).fill(false));
    } catch (err: any) {
      const msg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Unknown error';
      setError(`❌ Error: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTrendingTopicClick = async (trendingTopic: string) => {
    setTopic(trendingTopic);
    setLoading(true);
    setError('');
    setResults(null);

    try {
      const response = await axios.post(
        `${API_URL}/api/research-and-post?topic=${encodeURIComponent(trendingTopic)}&auto_post=false&with_images=${withImages}`,
        {}
      );

      console.log('API Response:', response.data);
      setResults(response.data);
      // Initialize post selection checkboxes (all unchecked by default)
      setSelectedPosts(new Array(response.data.content?.content_pieces?.length || 0).fill(false));
      
      // Scroll to results
      setTimeout(() => {
        document.querySelector('[data-section="results"]')?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err: any) {
      const msg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Unknown error';
      setError(`❌ Error: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', padding: '20px' }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        <h1>🚀 AI Content Generator</h1>
        <p style={{ fontSize: '16px', color: '#666' }}>Research topics and generate LinkedIn posts instantly</p>

        {/* Trending Topics Section */}
        {trendingTopics.length > 0 && (
          <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '30px', borderRadius: '8px', marginBottom: '20px', color: 'white' }}>
            <h2 style={{ margin: '0 0 20px 0', color: 'white' }}>⭐ Trending AI Topics Worldwide</h2>
            <p style={{ fontSize: '14px', color: 'rgba(255,255,255,0.9)', margin: '0 0 20px 0' }}>Click any topic to instantly generate posts</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '15px' }}>
              {trendingTopics.map((item: any, idx: number) => (
                <button
                  key={idx}
                  onClick={() => handleTrendingTopicClick(item.topic)}
                  disabled={loading}
                  style={{
                    padding: '20px',
                    background: 'rgba(255,255,255,0.15)',
                    border: '2px solid rgba(255,255,255,0.3)',
                    borderRadius: '8px',
                    color: 'white',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.3s',
                    opacity: loading ? 0.6 : 1,
                    backdropFilter: 'blur(10px)',
                    fontSize: '14px'
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) {
                      (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.25)';
                      (e.currentTarget as HTMLElement).style.transform = 'translateY(-2px)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!loading) {
                      (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.15)';
                      (e.currentTarget as HTMLElement).style.transform = 'translateY(0)';
                    }
                  }}
                >
                  <div style={{ fontWeight: '600', marginBottom: '8px', fontSize: '15px' }}>
                    {item.topic}
                  </div>
                  <div style={{ fontSize: '12px', opacity: 0.9, marginBottom: '10px' }}>
                    {item.description}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '11px', opacity: 0.8 }}>
                    <span>📍 {item.source}</span>
                    <span>🔥 {item.trending_score}%</span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        <div style={{ background: 'white', padding: '30px', borderRadius: '8px', marginBottom: '20px' }}>
          <h2>Search for a Topic</h2>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="e.g., what is LLM, Retrieval Augmented Generation..."
            disabled={loading}
            autoFocus
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '16px',
              border: '2px solid #ddd',
              borderRadius: '6px',
              marginBottom: '15px',
              boxSizing: 'border-box'
            }}
          />
          
          <div style={{ display: 'flex', gap: '15px', marginBottom: '15px', alignItems: 'center' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', userSelect: 'none' }}>
              <input
                type="checkbox"
                checked={withImages}
                onChange={(e) => setWithImages(e.target.checked)}
                disabled={loading}
                style={{ cursor: 'pointer', width: '18px', height: '18px' }}
              />
              <span style={{ fontSize: '14px', color: '#333', fontWeight: '500' }}>📸 Generate with Images</span>
            </label>
          </div>
          
          <button
            onClick={handleSearch}
            disabled={loading}
            style={{
              width: '100%',
              padding: '12px',
              fontSize: '16px',
              background: loading ? '#ccc' : '#0066cc',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            {loading ? '⏳ Searching...' : '🔍 Search & Generate'}
          </button>
        </div>

        {error && (
          <div style={{ background: '#ffebee', color: '#c62828', padding: '15px', borderRadius: '6px', marginBottom: '20px' }}>
            {error}
          </div>
        )}

        {results && results.status === 'success' && (
          <div data-section="results" style={{ background: 'white', padding: '30px', borderRadius: '8px' }}>
            <h2>✅ Generated Posts for "{results.topic}"</h2>
            
            {results.content?.content_pieces && results.content.content_pieces.length > 0 ? (
              <div>
                {results.content.content_pieces.map((post: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      background: selectedPosts[idx] ? '#e3f2fd' : '#f9f9f9',
                      border: selectedPosts[idx] ? '2px solid #0066cc' : '1px solid #ddd',
                      padding: '20px',
                      marginBottom: '15px',
                      borderRadius: '6px',
                      overflow: 'hidden',
                      transition: 'all 0.2s'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                      <input
                        type="checkbox"
                        checked={selectedPosts[idx] || false}
                        onChange={(e) => {
                          const newSelected = [...selectedPosts];
                          newSelected[idx] = e.target.checked;
                          setSelectedPosts(newSelected);
                        }}
                        style={{ cursor: 'pointer', width: '20px', height: '20px' }}
                      />
                      <div style={{ display: 'inline-block', background: '#0066cc', color: 'white', padding: '5px 10px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>
                        {post.type}
                      </div>
                      {selectedPosts[idx] && (
                        <span style={{ fontSize: '12px', color: '#0066cc', fontWeight: '600' }}>✓ Selected</span>
                      )}
                    </div>
                    
                    {post.image_url && (
                      <div style={{ marginBottom: '15px', borderRadius: '6px', overflow: 'hidden', backgroundColor: '#e0e0e0', height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <img
                          src={post.image_url}
                          alt={post.image_alt || 'Post image'}
                          style={{
                            width: '100%',
                            height: '100%',
                            objectFit: 'cover'
                          }}
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none';
                          }}
                        />
                      </div>
                    )}
                    
                    <p style={{ fontSize: '16px', lineHeight: '1.6', margin: '0 0 10px 0', whiteSpace: 'pre-wrap' }}>
                      {post.text}
                    </p>
                    <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {post.hashtags && post.hashtags.map((tag: string, i: number) => (
                        <span key={i} style={{ color: '#0066cc', fontWeight: '600' }}>
                          {tag.startsWith('#') ? tag : `#${tag}`}
                        </span>
                      ))}
                    </div>
                    <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
                      Engagement: {post.engagement_estimate}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>No posts generated</p>
            )}
            
            <div>
              <div style={{ marginBottom: '10px', fontSize: '14px', color: '#666' }}>
                {selectedPosts.filter(Boolean).length} of {selectedPosts.length} posts selected
              </div>
              <button
                style={{
                  width: '100%',
                  padding: '15px',
                  marginTop: '20px',
                  fontSize: '16px',
                  background: selectedPosts.filter(Boolean).length > 0 ? '#00cc66' : '#ccc',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: selectedPosts.filter(Boolean).length > 0 ? 'pointer' : 'not-allowed',
                  fontWeight: '600'
                }}
                onClick={() => handlePostToLinkedIn()}
                disabled={posting || selectedPosts.filter(Boolean).length === 0}
              >
                {posting ? '⏳ Posting...' : '📤 Post Selected to LinkedIn'}
              </button>
              
              {postingSchedule && (
                <div style={{ marginTop: '20px', background: '#f0f8ff', padding: '15px', borderRadius: '6px', border: '1px solid #0066cc' }}>
                  <h3 style={{ margin: '0 0 10px 0', color: '#0066cc' }}>✅ Posts Scheduled for LinkedIn</h3>
                  <p style={{ fontSize: '13px', color: '#666', margin: '0 0 10px 0' }}>
                    {postingSchedule.authenticated ? '🚀 Posts are queued!' : '📋 Ready to post - Copy each post below and paste to LinkedIn'}
                  </p>
                  {postingSchedule.schedule.map((item: any, idx: number) => (
                    <div key={idx} style={{ 
                      padding: '12px', 
                      marginBottom: '10px',
                      background: 'white',
                      borderLeft: '4px solid #0066cc',
                      borderRadius: '4px',
                      fontSize: '13px'
                    }}>
                      <div style={{ fontWeight: '600', color: '#0066cc', marginBottom: '5px' }}>
                        📅 {item.day} at {item.time}
                      </div>
                      <div style={{ color: '#333', marginBottom: '8px', lineHeight: '1.5' }}>
                        {item.text}
                      </div>
                      <button
                        style={{
                          padding: '6px 12px',
                          fontSize: '12px',
                          background: '#0066cc',
                          color: 'white',
                          border: 'none',
                          borderRadius: '3px',
                          cursor: 'pointer'
                        }}
                        onClick={() => {
                          navigator.clipboard.writeText(item.text);
                          alert('✅ Post copied! Paste it on LinkedIn now.');
                        }}
                      >
                        📋 Copy Post
                      </button>
                    </div>
                  ))}
                  <button
                    style={{
                      width: '100%',
                      padding: '10px',
                      marginTop: '10px',
                      fontSize: '14px',
                      background: '#999',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                    onClick={() => setPostingSchedule(null)}
                  >
                    👉 Generate New Posts
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
