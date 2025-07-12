import React, { useState } from 'react';
import './App.css';
import YouTubeUpload from './YouTubeUpload';
import TitleGenerator from './TitleGenerator';

interface Clip {
  id: number;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  duration: number;
  timestamp: number;
  filename: string;
  captionStyle?: string;
  fontStyle?: string;
  isViral?: boolean;
  fileSize?: number;
  failed?: boolean;
  error?: string;
  hook_type?: string;
  viral_score?: number;
  natural_flow_score?: number;
  quality_rating?: string;
  analysis_method?: string;
  post_analysis?: {
    quality_check: string;
    actual_content: string;
    language_confirmed: string;
  };
  // Enhanced speaker detection properties
  processing_method?: 'crop' | 'resize';
  has_visible_speaker?: boolean;
  content_type?: string;
  speaker_confidence?: number;
  detection_reasoning?: string[];
}

// SVG Icons as components
const SparkleIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 0l3.09 6.26L22 9.27l-5.45 5.32L18.18 24 12 20.27 5.82 24l1.63-9.41L2 9.27l6.91-3.01L12 0z"/>
  </svg>
);

const RocketIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M12 2L13.09 8.26L22 12L13.09 15.74L12 22L10.91 15.74L2 12L10.91 8.26L12 2Z"/>
  </svg>
);

const VideoIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
    <path d="M8 5v14l11-7z"/>
  </svg>
);

const ClockIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
    <circle cx="12" cy="12" r="10"/>
    <polyline points="12,6 12,12 16,14"/>
  </svg>
);

const DownloadIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="7,10 12,15 17,10"/>
    <line x1="12" y1="15" x2="12" y2="3"/>
  </svg>
);

const LoadingIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" className="animate-spin">
    <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" strokeDasharray="32" strokeDashoffset="32">
      <animate attributeName="stroke-dashoffset" dur="1s" values="32;0" repeatCount="indefinite"/>
    </circle>
  </svg>
);

const CheckIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
    <polyline points="20,6 9,17 4,12"/>
  </svg>
);

function App() {
  const API_URL = process.env.REACT_APP_API_URL || 'https://trilion-backend-r0a7.onrender.com';
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [clips, setClips] = useState<Clip[]>([]);
  const [numClips, setNumClips] = useState(3);
  const [clipDuration, setClipDuration] = useState(30);
  const [captionsEnabled, setCaptionsEnabled] = useState(true);
  const [captionStyle, setCaptionStyle] = useState('single-word');
  const [processingMode, setProcessingMode] = useState('auto'); // auto, crop, resize
  const [loadingVideos, setLoadingVideos] = useState<Set<number>>(new Set());
  const [currentView, setCurrentView] = useState<'generate' | 'upload'>('generate');
  const [uploadingClipIndex, setUploadingClipIndex] = useState<number | null>(null);
  const [uploadStatus, setUploadStatus] = useState<{[key: number]: string}>({});
  const [clipTitles, setClipTitles] = useState<{[key: number]: any[]}>({});
  const [demoMode, setDemoMode] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ytLink: demoMode ? '' : url,
          numClips: numClips,
          clipDuration: clipDuration,
          captionStyle: captionsEnabled ? captionStyle : 'none',
          fontStyle: 'impact',
          processingMode: processingMode,
          demoMode: demoMode
        }),
      });

      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        throw new Error('Server returned invalid JSON response. Please try again.');
      }
      
      if (!response.ok) {
        throw new Error(data.error || data.details || 'Server error occurred');
      }
      
      if (data.clips) {
        setClips(data.clips);
      } else {
        setError('No clips were generated. Please try again.');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An error occurred';
      setError(errorMessage);
      
      if (demoMode) {
        // Fallback to mock data for demo mode
        const mockClips = [];
        for (let i = 0; i < numClips; i++) {
          const startTime = i * clipDuration;
          const endTime = startTime + clipDuration;
          
          mockClips.push({
            id: Date.now() + i,
            title: `🔥 VIRAL MOMENT ${i + 1} - MUST WATCH! 🔥`,
            description: `Demo viral clip ${i + 1} - This would be AI-generated content based on the video analysis`,
            start_time: `${Math.floor(startTime / 60)}:${(startTime % 60).toString().padStart(2, '0')}`,
            end_time: `${Math.floor(endTime / 60)}:${(endTime % 60).toString().padStart(2, '0')}`,
            duration: clipDuration,
            timestamp: Date.now(),
            filename: `demo_clip_${i + 1}.mp4`,
            viral_score: Math.floor(Math.random() * 40) + 60,
            platform: 'tiktok',
            demo: true
          });
        }
        
        setClips(mockClips);
        setError(null);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Test server connectivity on component mount
  React.useEffect(() => {
    const testServer = async () => {
      try {
        const response = await fetch(`${API_URL}/`);
        if (!response.ok) {
          throw new Error(`Server responded with ${response.status}`);
        }
        let data;
        try {
          data = await response.json();
        } catch (parseError) {
          throw new Error('Server returned invalid JSON');
        }
        // Server test successful
        // Also test clips endpoint
        try {
          const clipsResponse = await fetch(`${API_URL}/clips-list`);
          if (clipsResponse.ok) {
            const clipsData = await clipsResponse.json();
            // Available clips count: clipsData.clips?.length || 0
          }
        } catch (clipsError) {
          // Clips endpoint not available, but main server is working
        }
      } catch (error) {
        // Server test failed - using mock mode
      }
    };
    testServer();
  }, [API_URL]);

  // Initialize loading state when clips change
  React.useEffect(() => {
    if (clips.length > 0) {
      setLoadingVideos(new Set(clips.map((_, index) => index)));
      
      // Fallback: Clear loading states after 30 seconds to prevent stuck loading
      const fallbackTimeout = setTimeout(() => {
        setLoadingVideos(new Set());
      }, 30000);
      
      return () => clearTimeout(fallbackTimeout);
    }
  }, [clips, API_URL]);

  // Handle title generation for a specific clip
  const handleTitlesGenerated = (clipIndex: number, titles: any[]) => {
    setClipTitles(prev => ({
      ...prev,
      [clipIndex]: titles
    }));
  };

  // Upload a single clip to YouTube
  const handleUploadToYouTube = async (clip: Clip, index: number) => {
    setUploadingClipIndex(index);
    setUploadStatus((prev) => ({ ...prev, [index]: 'Uploading...' }));
    
    // Use the best generated title if available
    const generatedTitles = clipTitles[index];
    const bestTitle = generatedTitles && generatedTitles.length > 0 
      ? generatedTitles[0].title 
      : clip.title || `Viral Clip #${index + 1}`;
    
    try {
      const response = await fetch(`${API_URL}/upload/youtube-shorts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          clipFilename: clip.filename,
          title: bestTitle,
          description: clip.description || '',
          originalVideoUrl: url
        })
      });
      const result = await response.json();
      if (result.success) {
        setUploadStatus((prev) => ({ ...prev, [index]: '✅ Uploaded! (Public)' }));
      } else {
        setUploadStatus((prev) => ({ ...prev, [index]: '❌ Upload failed' }));
      }
    } catch (err) {
      setUploadStatus((prev) => ({ ...prev, [index]: '❌ Upload failed' }));
    } finally {
      setUploadingClipIndex(null);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo-container">
            <img src="/logo-removebg-preview.png" alt="Viral Clip Generator" className="logo-image" />
            <span className="brand-text">Trilion</span>
          </div>
          <nav className="nav-menu">
            <a href="#features" className="nav-link">Features</a>
            <button 
              className={`nav-link ${currentView === 'generate' ? 'active' : ''}`}
              onClick={() => setCurrentView('generate')}
            >
              Generate Clips
            </button>
            <button 
              className={`nav-link ${currentView === 'upload' ? 'active' : ''}`}
              onClick={() => setCurrentView('upload')}
            >
              🚀 Upload to YouTube
            </button>
          </nav>
        </div>
      </header>
        
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-background"></div>
        <div className="hero-content">
          <div className="hero-badge">
            <SparkleIcon />
            <span>AI-Powered Viral Content Creation</span>
          </div>
          <h1 className="hero-title">
            Transform Your Videos into
            <span className="gradient-text"> Viral Clips</span>
          </h1>
          <p className="hero-description">
            Our advanced AI analyzes your content to identify and extract the most engaging moments, 
            creating perfectly timed clips optimized for maximum viral potential on social media.
          </p>
          <div className="hero-stats">
            <div className="stat-item">
              <div className="stat-number">10M+</div>
              <div className="stat-label">Clips Generated</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">98%</div>
              <div className="stat-label">Accuracy Rate</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">50x</div>
              <div className="stat-label">Faster Creation</div>
            </div>
          </div>
        </div>
        <div className="hero-visual">
          <div className="floating-elements">
            <div className="floating-icon" style={{animationDelay: '0s'}}><VideoIcon /></div>
            <div className="floating-icon" style={{animationDelay: '2s'}}><RocketIcon /></div>
            <div className="floating-icon" style={{animationDelay: '4s'}}><SparkleIcon /></div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <div className="features-container">
          <h2 className="section-title">Why Choose Our AI Clip Generator?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon gradient-bg-1">
                <SparkleIcon />
              </div>
              <h3>AI-Powered Analysis</h3>
              <p>Advanced machine learning identifies viral moments with 98% accuracy</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon gradient-bg-2">
                <RocketIcon />
              </div>
              <h3>Instant Generation</h3>
              <p>Create professional viral clips in seconds, not hours</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon gradient-bg-3">
                <VideoIcon />
              </div>
              <h3>Platform Optimized</h3>
              <p>Perfect formatting for TikTok, Instagram Reels, and YouTube Shorts</p>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="main-content">
        {currentView === 'generate' ? (
          <>
            {/* Input Section */}
            <section id="generate" className="generator-section">
          <div className="generator-container">
            <div className="generator-header">
              <h2 className="section-title">Create Your Viral Clips</h2>
              <p className="section-subtitle">
                Paste your YouTube URL and let our AI create engaging clips in seconds
              </p>
            </div>
            
            <form onSubmit={handleSubmit} className="generator-form">
              {/* Error Display */}
              {error && (
                <div className="error-message" style={{
                  background: '#fee',
                  border: '1px solid #fcc',
                  borderRadius: '8px',
                  padding: '12px',
                  marginBottom: '16px',
                  color: '#c33',
                  fontSize: '14px'
                }}>
                  <strong>Error:</strong> {error}
                </div>
              )}

              <div className="input-container">
                <div className="input-wrapper">
                  <input
                    type="text"
                    className="url-input"
                    placeholder={demoMode ? "Demo mode - no URL needed" : "Paste your YouTube URL here..."}
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    required={!demoMode}
                    disabled={demoMode}
                  />
                  <div className="input-icon">
                    <VideoIcon />
                  </div>
                </div>
                <button type="submit" className="submit-button" disabled={isLoading || (!url && !demoMode)}>
                  {isLoading ? (
                    <>
                      <LoadingIcon />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <RocketIcon />
                      <span>{demoMode ? 'Try Demo Mode' : 'Create Viral Clips'}</span>
                    </>
                  )}
                </button>
              </div>
              
              {/* Demo Mode Toggle */}
              <div className="demo-mode-toggle" style={{
                marginTop: '12px',
                padding: '8px 12px',
                background: '#f8f9fa',
                borderRadius: '6px',
                border: '1px solid #e9ecef'
              }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
                  <input
                    type="checkbox"
                    checked={demoMode}
                    onChange={(e) => {
                      setDemoMode(e.target.checked);
                      if (e.target.checked) {
                        setError(null);
                      }
                    }}
                  />
                  <span>🎬 Try Demo Mode (no YouTube URL needed)</span>
                </label>
                {demoMode && (
                  <div style={{ marginTop: '8px', fontSize: '12px', color: '#666' }}>
                    Demo mode generates sample clips to test the interface without downloading videos.
                  </div>
                )}
              </div>
              
              {/* Options Section */}
              <div className="options-container">
                {/* Row 1: Processing Mode, Captions, Caption Style */}
                <div className="options-row-1">
                  <div className="option-group">
                    <label className="option-label">
                      <VideoIcon />
                      Processing Mode
                    </label>
                    <select 
                      className="option-select"
                      value={processingMode}
                      onChange={(e) => setProcessingMode(e.target.value)}
                    >
                      <option value="auto">🤖 Auto-Detect (Recommended)</option>
                      <option value="crop">🎤 Cropped - Best for focusing on speaker</option>
                      <option value="resize">📱 Rescaled - Best when no speaker/voiceovers</option>
                    </select>
                  </div>

                  <div className="option-group">
                    <label className="option-label">
                      <SparkleIcon />
                      Captions
                    </label>
                    <div className="toggle-container">
                      <label className="toggle-switch">
                        <input
                          type="checkbox"
                          checked={captionsEnabled}
                          onChange={(e) => setCaptionsEnabled(e.target.checked)}
                        />
                        <span className="toggle-slider"></span>
                      </label>
                      <span className="toggle-text">{captionsEnabled ? 'On' : 'Off'}</span>
                    </div>
                  </div>

                  <div className="option-group">
                    <label className="option-label">
                      <SparkleIcon />
                      Caption Style
                    </label>
                    <select 
                      className="option-select"
                      value={captionStyle}
                      onChange={(e) => setCaptionStyle(e.target.value)}
                      disabled={!captionsEnabled}
                    >
                      <option value="single-word">Single Word</option>
                      <option value="engaging">Engaging Phrases</option>
                    </select>
                  </div>
                </div>

                {/* Row 2: Number of Clips, Clip Duration */}
                <div className="options-row-2">
                  <div className="option-group">
                    <label className="option-label">
                      <ClockIcon />
                      Number of Clips
                    </label>
                    <select 
                      className="option-select"
                      value={numClips}
                      onChange={(e) => setNumClips(parseInt(e.target.value))}
                    >
                      <option value={1}>1 clip</option>
                      <option value={2}>2 clips</option>
                      <option value={3}>3 clips</option>
                      <option value={4}>4 clips</option>
                      <option value={5}>5 clips</option>
                    </select>
                  </div>

                  <div className="option-group">
                    <label className="option-label">
                      <ClockIcon />
                      Clip Duration
                    </label>
                    <select 
                      className="option-select"
                      value={clipDuration}
                      onChange={(e) => setClipDuration(parseInt(e.target.value))}
                    >
                      <option value={15}>15 seconds</option>
                      <option value={30}>30 seconds</option>
                      <option value={60}>60 seconds</option>
                    </select>
                  </div>
                </div>
                
                {processingMode !== 'auto' && (
                  <div className="processing-mode-info" style={{ 
                    fontSize: '0.85rem', 
                    color: '#666', 
                    marginTop: '0.5rem',
                    padding: '0.5rem',
                    background: '#f8f9fa',
                    borderRadius: '4px',
                    borderLeft: '3px solid #007bff'
                  }}>
                    {processingMode === 'crop' ? (
                      <>
                        <strong>🎤 Cropped Mode:</strong> Uses AI face detection to focus on speakers. 
                        Best for talking head videos, interviews, presentations.
                      </>
                    ) : (
                      <>
                        <strong>📱 Rescaled Mode:</strong> Preserves all visual content by resizing. 
                        Best for graphics, animations, text overlays, or stock footage with voiceover.
                      </>
                    )}
                  </div>
                )}
              </div>
            </form>
          </div>
        </section>

        {/* Loading State */}
        {isLoading && (
          <section className="loading-section">
            <div className="loading-container">
              <div className="loading-animation">
                <div className="loading-spinner"></div>
                <div className="loading-dots">
                  <div className="dot"></div>
                  <div className="dot"></div>
                  <div className="dot"></div>
                </div>
              </div>
              <h3>Creating Your Viral Clips</h3>
              <p>Our AI is analyzing your video and extracting the most engaging moments...</p>
              <div className="progress-steps">
                <div className="step active">
                  <CheckIcon />
                  <span>Video Downloaded</span>
                </div>
                <div className="step active">
                  <LoadingIcon />
                  <span>AI Analysis</span>
                </div>
                <div className="step">
                  <span>Clip Generation</span>
                </div>
              </div>
            </div>
          </section>
        )}

            {/* Generated Clips Results */}
            {clips.length > 0 && (
              <section className="results-section">
                <div className="results-container">
                  {/* Success Message */}
                  <div className="results-success">
                    <h3>🎉 Success! Your viral clips are ready</h3>
                    <p>Our AI has analyzed your video and created {clips.length} optimized clips for maximum engagement</p>
                  </div>

                  <div className="results-header">
                    <h2 className="section-title">Your Viral Clips</h2>
                    <p className="section-subtitle">
                      AI-powered clips optimized for maximum engagement and viral potential
                    </p>
                  </div>
                  
                  <div className="results-grid">
                    {clips.map((clip, index) => (
                      <div key={index} className="result-card">
                        <div className="result-video-container">
                          <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: '#000', zIndex: 0}}></div>
                          {/* Debug info - remove in production */}
                          {process.env.NODE_ENV === 'development' && (
                            <div style={{position: 'absolute', top: '5px', left: '5px', zIndex: 10, color: 'yellow', fontSize: '10px', background: 'rgba(0,0,0,0.8)', padding: '2px'}}>
                              {clip.filename}
                            </div>
                          )}
                          <video 
                            className="result-video vertical-video" 
                            controls 
                            preload="metadata"
                            style={{position: 'relative', zIndex: 1}}
                            key={`video-${index}-${clip.filename}`}
                            onLoadStart={() => {
                              setLoadingVideos(prev => {
                                const newSet = new Set(prev);
                                newSet.add(index);
                                return newSet;
                              });
                            }}
                            onLoadedData={() => {
                              setLoadingVideos(prev => {
                                const newSet = new Set(prev);
                                newSet.delete(index);
                                return newSet;
                              });
                            }}
                            onError={(e) => {
                              setLoadingVideos(prev => {
                                const newSet = new Set(prev);
                                newSet.delete(index);
                                return newSet;
                              });
                            }}
                            onCanPlay={() => {
                              setLoadingVideos(prev => {
                                const newSet = new Set(prev);
                                newSet.delete(index);
                                return newSet;
                              });
                            }}
                            onLoadedMetadata={() => {
                              // Metadata loaded
                            }}
                          >
                            <source 
                              src={`${API_URL}/clips/${clip.filename}`} 
                              type="video/mp4"
                              onError={(e) => {
                                // Source error
                              }}
                            />
                            Your browser does not support the video tag.
                          </video>
                          {/* Show loading indicator only when video is loading */}
                          {loadingVideos.has(index) && (
                            <div className="video-loading-overlay">
                              <div className="video-loading-spinner"></div>
                              <p style={{ margin: 0, fontSize: '0.9rem' }}>Loading clip...</p>
                              <small style={{ opacity: 0.7, fontSize: '0.7rem' }}>
                                Clip #{index + 1}
                              </small>
                            </div>
                          )}
                        </div>
                        <div className="result-info">
                          <h3>🎬 Viral Clip #{index + 1}</h3>
                          <p>
                            {clip.description || `Engaging ${clip.duration || clipDuration}s clip optimized for viral growth and maximum audience engagement.`}
                          </p>
                          {clip.processing_method && (
                            <div style={{ fontSize: '0.8rem', opacity: 0.8, marginTop: '0.5rem' }}>
                              {clip.processing_method === 'crop' ? (
                                <span>🎤 Speaker-focused crop (confidence: {((clip.speaker_confidence || 0) * 100).toFixed(0)}%)</span>
                              ) : (
                                <span>📱 Content-preserving resize ({clip.content_type})</span>
                              )}
                            </div>
                          )}
                          <div className="result-actions">
                            <a 
                              href={`${API_URL}/clips/${clip.filename}`}
                              className="action-button download"
                              download={`viral_clip_${index + 1}.mp4`}
                              onClick={(e) => {
                                // Test if file exists first
                                fetch(`${API_URL}/clips/${clip.filename}`, {method: 'HEAD'})
                                  .then(response => {
                                    if (!response.ok) {
                                      e.preventDefault();
                                      alert('File not found on server');
                                    }
                                  })
                                  .catch(error => {
                                    e.preventDefault();
                                    alert('Cannot access file');
                                  });
                              }}
                            >
                              <DownloadIcon />
                              Download HD
                            </a>
                            <button 
                              className="action-button share"
                              onClick={() => {
                                const clipUrl = `${API_URL}/clips/${clip.filename}`;
                                if (navigator.share) {
                                  navigator.share({
                                    title: `Viral Clip #${index + 1}`,
                                    text: 'Check out this AI-generated viral clip!',
                                    url: clipUrl
                                  });
                                } else {
                                  navigator.clipboard.writeText(clipUrl);
                                  alert('Link copied to clipboard!');
                                }
                              }}
                            >
                              <SparkleIcon />
                              Share
                            </button>
                            <button
                              className="action-button upload"
                              style={{ background: '#ff0000', color: 'white', marginLeft: 8 }}
                              onClick={() => handleUploadToYouTube(clip, index)}
                              disabled={uploadingClipIndex === index}
                            >
                              {uploadingClipIndex === index ? 'Uploading...' : '🚀 Upload to YouTube'}
                            </button>
                            {uploadStatus[index] && (
                              <span style={{ marginLeft: 10, fontWeight: 500 }}>{uploadStatus[index]}</span>
                            )}
                          </div>
                          
                          {/* Title Generator Integration */}
                          <TitleGenerator 
                            clipFilename={clip.filename}
                            onTitlesGenerated={(titles) => handleTitlesGenerated(index, titles)}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </section>
            )}
          </>
        ) : (
          <YouTubeUpload />
        )}
      </main>
    </div>
  );
}

export default App;
