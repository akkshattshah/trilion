import React, { useState, useEffect } from 'react';

interface Clip {
  filename: string;
  title: string;
  description: string;
  isViral?: boolean;
}

interface UploadResult {
  success: boolean;
  videoId?: string;
  videoUrl?: string;
  shortsUrl?: string;
  title?: string;
  privacyStatus?: string;
  error?: string;
}

const YouTubeUpload: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [clips, setClips] = useState<Clip[]>([]);
  const [selectedClips, setSelectedClips] = useState<string[]>([]);
  const [uploadResults, setUploadResults] = useState<UploadResult[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [loading, setLoading] = useState(true);

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
    loadClips();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await fetch(`${API_URL}/auth/youtube/status`);
      const data = await response.json();
      setIsAuthenticated(data.authenticated);
    } catch (error) {
      console.error('Failed to check auth status:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadClips = async () => {
    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await fetch(`${API_URL}/clips-list`);
      const data = await response.json();
      setClips(data.clips.map((clip: any) => ({
        filename: clip.filename,
        title: clip.filename.replace('.mp4', '').replace('VIRAL_', '').replace(/_/g, ' '),
        description: `Viral clip generated from your content`,
        isViral: clip.isViral
      })));
    } catch (error) {
      console.error('Failed to load clips:', error);
    }
  };

  const getAuthUrl = async () => {
    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await fetch(`${API_URL}/auth/youtube/url`);
      const data = await response.json();
      if (data.success) {
        window.open(data.authUrl, '_blank');
      }
    } catch (error) {
      console.error('Failed to get auth URL:', error);
    }
  };

  const handleClipSelection = (filename: string) => {
    setSelectedClips(prev => 
      prev.includes(filename) 
        ? prev.filter(f => f !== filename)
        : [...prev, filename]
    );
  };

  const uploadSelectedClips = async () => {
    if (selectedClips.length === 0) {
      alert('Please select at least one clip to upload');
      return;
    }

    setIsUploading(true);
    setUploadResults([]);

    try {
      const results: UploadResult[] = [];

      for (const clipFilename of selectedClips) {
        const clip = clips.find(c => c.filename === clipFilename);
        const title = clip?.title || `Viral Clip - ${clipFilename}`;
        
        console.log(`Uploading ${clipFilename} with title: ${title}`);

        const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
        const response = await fetch(`${API_URL}/upload/youtube-shorts`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            clipFilename,
            title,
            description: clip?.description || 'Viral content generated with AI',
            tags: ['viral', 'shorts', 'trending']
          }),
        });

        const result = await response.json();
        results.push(result);

        // Add delay between uploads
        if (selectedClips.indexOf(clipFilename) < selectedClips.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      }

      setUploadResults(results);
      
      const successful = results.filter(r => r.success);
      if (successful.length > 0) {
        alert(`✅ Successfully uploaded ${successful.length} clips to YouTube Shorts!`);
      }
      
    } catch (error) {
      console.error('Upload failed:', error);
      alert('❌ Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const makeVideoPublic = async (videoId: string) => {
    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
      const response = await fetch(`${API_URL}/upload/youtube/make-public`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ videoId }),
      });

      const result = await response.json();
      if (result.success) {
        alert('✅ Video is now public!');
        // Refresh results
        setUploadResults(prev => 
          prev.map(r => 
            r.videoId === videoId 
              ? { ...r, privacyStatus: 'public' }
              : r
          )
        );
      } else {
        alert('❌ Failed to make video public: ' + result.error);
      }
    } catch (error) {
      console.error('Failed to make video public:', error);
      alert('❌ Failed to make video public');
    }
  };

  if (loading) {
    return (
      <div className="youtube-upload-container">
        <div className="loading">Loading YouTube upload system...</div>
      </div>
    );
  }

  return (
    <div className="youtube-upload-container">
      <div className="youtube-header">
        <h2>🚀 YouTube Shorts Upload</h2>
        <p>Upload your viral clips directly to YouTube Shorts</p>
      </div>

      {/* Authentication Section */}
      <div className="auth-section">
        {!isAuthenticated ? (
          <div className="auth-prompt">
            <h3>🔐 YouTube Authentication Required</h3>
            <p>You need to authenticate with YouTube to upload Shorts.</p>
            <button 
              className="auth-button"
              onClick={getAuthUrl}
            >
              🔗 Connect YouTube Account
            </button>
            <p className="auth-note">
              This will open YouTube's authorization page. After authorizing, 
              you'll be redirected back and can start uploading.
            </p>
          </div>
        ) : (
          <div className="auth-success">
            <h3>✅ YouTube Connected</h3>
            <p>You're authenticated and ready to upload Shorts!</p>
          </div>
        )}
      </div>

      {/* Clip Selection */}
      {isAuthenticated && (
        <div className="clip-selection">
          <h3>📁 Select Clips to Upload</h3>
          <div className="clips-grid">
            {clips.map((clip) => (
              <div 
                key={clip.filename}
                className={`clip-item ${selectedClips.includes(clip.filename) ? 'selected' : ''}`}
                onClick={() => handleClipSelection(clip.filename)}
              >
                <div className="clip-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedClips.includes(clip.filename)}
                    onChange={() => handleClipSelection(clip.filename)}
                  />
                </div>
                <div className="clip-info">
                  <h4>{clip.title}</h4>
                  <p>{clip.description}</p>
                  {clip.isViral && <span className="viral-badge">🚀 VIRAL</span>}
                </div>
              </div>
            ))}
          </div>

          {selectedClips.length > 0 && (
            <div className="upload-actions">
              <button 
                className="upload-button"
                onClick={uploadSelectedClips}
                disabled={isUploading}
              >
                {isUploading ? '📤 Uploading...' : `📤 Upload ${selectedClips.length} Clip${selectedClips.length > 1 ? 's' : ''} to YouTube Shorts`}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Upload Results */}
      {uploadResults.length > 0 && (
        <div className="upload-results">
          <h3>📊 Upload Results</h3>
          <div className="results-grid">
            {uploadResults.map((result, index) => (
              <div key={index} className={`result-item ${result.success ? 'success' : 'error'}`}>
                {result.success ? (
                  <>
                    <h4>✅ Upload Successful</h4>
                    <p><strong>Title:</strong> {result.title}</p>
                    <p><strong>Video ID:</strong> {result.videoId}</p>
                    <p><strong>Status:</strong> {result.privacyStatus}</p>
                    <div className="result-actions">
                      <a 
                        href={result.videoUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="view-button"
                      >
                        👁️ View Video
                      </a>
                      <a 
                        href={result.shortsUrl} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="shorts-button"
                      >
                        📱 View Shorts
                      </a>
                      {result.privacyStatus === 'private' && (
                        <button 
                          className="public-button"
                          onClick={() => result.videoId && makeVideoPublic(result.videoId)}
                        >
                          🌍 Make Public
                        </button>
                      )}
                    </div>
                  </>
                ) : (
                  <>
                    <h4>❌ Upload Failed</h4>
                    <p><strong>Error:</strong> {result.error}</p>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>
      )}


    </div>
  );
};

export default YouTubeUpload; 