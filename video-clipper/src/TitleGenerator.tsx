import React, { useState } from 'react';

interface TitleGeneratorProps {
  clipFilename: string;
  onTitlesGenerated: (titles: GeneratedTitle[]) => void;
}

interface GeneratedTitle {
  rank: number;
  title: string;
  viral_score: number;
  predicted_ctr: string;
  predicted_engagement: string;
  hook_type: string;
  platform_optimized: string;
  style: string;
  length: number;
  word_count: number;
  quality_scores: {
    viral_potential: number;
    psychological_impact: number;
    platform_optimization: number;
    emotional_resonance: number;
    curiosity_factor: number;
    clarity: number;
  };
}

interface TitleGenerationResponse {
  success: boolean;
  message: string;
  clipFilename: string;
  platform: string;
  style: string;
  totalTitles: number;
  titles: GeneratedTitle[];
  optimizationRecommendations: string[];
  performancePredictions: {
    viral_potential: string;
    best_title_ctr: number;
    best_title_engagement: number;
    average_score: number;
  };
  contentAnalysis: {
    key_topics: string[];
    viral_potential: string;
  };
}

const TitleGenerator: React.FC<TitleGeneratorProps> = ({ clipFilename, onTitlesGenerated }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedTitles, setGeneratedTitles] = useState<GeneratedTitle[]>([]);
  const [platform, setPlatform] = useState<string>('tiktok');
  const [style, setStyle] = useState<string>('mega_viral');
  const [numTitles, setNumTitles] = useState<number>(3);
  const [showResults, setShowResults] = useState(false);
  const [recommendations, setRecommendations] = useState<string[]>([]);
  const [predictions, setPredictions] = useState<any>(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  const generateTitles = async () => {
    setIsGenerating(true);
    setShowResults(false);

    try {
      console.log(`🎯 Generating titles for ${clipFilename} (${platform}, ${style})`);
      
      const response = await fetch(`${API_URL}/generate-titles-for-clip`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          clipFilename,
          platform,
          numTitles,
          style
        }),
      });

      const data: TitleGenerationResponse = await response.json();
      console.log('✅ Title generation response:', data);

      if (data.success && data.titles) {
        setGeneratedTitles(data.titles);
        setRecommendations(data.optimizationRecommendations || []);
        setPredictions(data.performancePredictions);
        setShowResults(true);
        onTitlesGenerated(data.titles);
      } else {
        console.error('❌ Title generation failed:', data);
        alert('Failed to generate titles. Please try again.');
      }
    } catch (error) {
      console.error('❌ Error generating titles:', error);
      alert('Error generating titles. Please check your connection.');
    } finally {
      setIsGenerating(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 8.0) return '#22c55e'; // Green
    if (score >= 7.0) return '#eab308'; // Yellow
    if (score >= 6.0) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const getViralPotentialEmoji = (potential: string): string => {
    switch (potential?.toLowerCase()) {
      case 'high': return '🚀';
      case 'moderate': return '📈';
      case 'low': return '📊';
      default: return '🎯';
    }
  };

  return (
    <div className="title-generator">
      <div className="title-generator-header">
        <h4>🎯 Generate Viral Titles</h4>
        <p>Create psychology-optimized titles that maximize clicks and engagement</p>
      </div>

      <div className="title-generator-controls">
        <div className="control-row">
          <div className="control-group">
            <label>Platform:</label>
            <select 
              value={platform} 
              onChange={(e) => setPlatform(e.target.value)}
              className="title-select"
            >
              <option value="tiktok">🎵 TikTok</option>
              <option value="youtube">📺 YouTube</option>
              <option value="instagram">📸 Instagram</option>
              <option value="twitter">🐦 Twitter</option>
            </select>
          </div>
          
          <div className="control-group">
            <label>Style:</label>
            <select 
              value={style} 
              onChange={(e) => setStyle(e.target.value)}
              className="title-select"
            >
              <option value="mega_viral">🔥 Mega Viral (10M+ views)</option>
              <option value="high_viral">🚀 High Viral (1M+ views)</option>
              <option value="platform_specific">📱 Platform Specific</option>
            </select>
          </div>

          <div className="control-group">
            <label>Number of Titles:</label>
            <select 
              value={numTitles} 
              onChange={(e) => setNumTitles(Number(e.target.value))}
              className="title-select"
            >
              <option value={2}>2 titles</option>
              <option value={3}>3 titles</option>
              <option value={5}>5 titles</option>
            </select>
          </div>
        </div>

        <button 
          onClick={generateTitles}
          disabled={isGenerating}
          className="generate-titles-button"
        >
          {isGenerating ? (
            <>
              <div className="loading-spinner-small"></div>
              Generating Titles...
            </>
          ) : (
            <>
              🎯 Generate Viral Titles
            </>
          )}
        </button>
      </div>

      {showResults && generatedTitles.length > 0 && (
        <div className="title-results">
          <div className="title-results-header">
            <h5>✨ Generated Viral Titles</h5>
            {predictions && (
              <div className="predictions-summary">
                <span className="prediction-item">
                  {getViralPotentialEmoji(predictions.viral_potential)} 
                  {predictions.viral_potential?.toUpperCase() || 'MODERATE'} viral potential
                </span>
                <span className="prediction-item">
                  📊 Best CTR: {(predictions.best_title_ctr * 100).toFixed(1)}%
                </span>
              </div>
            )}
          </div>

          <div className="titles-list">
            {generatedTitles.map((title, index) => (
              <div key={index} className="title-item">
                <div className="title-header">
                  <span className="title-rank">#{title.rank}</span>
                  <span 
                    className="title-score"
                    style={{ color: getScoreColor(title.viral_score) }}
                  >
                    {title.viral_score.toFixed(1)}/10
                  </span>
                </div>
                
                <div className="title-text">
                  {title.title}
                </div>
                
                <div className="title-metrics">
                  <span className="metric">
                    🎯 CTR: {title.predicted_ctr}
                  </span>
                  <span className="metric">
                    💡 Engagement: {title.predicted_engagement}
                  </span>
                  <span className="metric">
                    🔥 Hook: {title.hook_type.replace('_', ' ')}
                  </span>
                </div>

                <div className="title-quality-scores">
                  <div className="quality-bar">
                    <span className="quality-label">Viral Potential:</span>
                    <div className="quality-meter">
                      <div 
                        className="quality-fill"
                        style={{ 
                          width: `${(title.quality_scores.viral_potential / 10) * 100}%`,
                          backgroundColor: getScoreColor(title.quality_scores.viral_potential)
                        }}
                      ></div>
                    </div>
                    <span className="quality-value">{title.quality_scores.viral_potential.toFixed(1)}</span>
                  </div>

                  <div className="quality-bar">
                    <span className="quality-label">Psychology Impact:</span>
                    <div className="quality-meter">
                      <div 
                        className="quality-fill"
                        style={{ 
                          width: `${(title.quality_scores.psychological_impact / 10) * 100}%`,
                          backgroundColor: getScoreColor(title.quality_scores.psychological_impact)
                        }}
                      ></div>
                    </div>
                    <span className="quality-value">{title.quality_scores.psychological_impact.toFixed(1)}</span>
                  </div>

                  <div className="quality-bar">
                    <span className="quality-label">Curiosity Factor:</span>
                    <div className="quality-meter">
                      <div 
                        className="quality-fill"
                        style={{ 
                          width: `${(title.quality_scores.curiosity_factor / 10) * 100}%`,
                          backgroundColor: getScoreColor(title.quality_scores.curiosity_factor)
                        }}
                      ></div>
                    </div>
                    <span className="quality-value">{title.quality_scores.curiosity_factor.toFixed(1)}</span>
                  </div>
                </div>

                <div className="title-actions">
                  <button 
                    className="copy-title-button"
                    onClick={() => {
                      navigator.clipboard.writeText(title.title);
                      alert('Title copied to clipboard! 📋');
                    }}
                  >
                    📋 Copy Title
                  </button>
                </div>
              </div>
            ))}
          </div>

          {recommendations.length > 0 && (
            <div className="optimization-recommendations">
              <h6>💡 Optimization Tips:</h6>
              <ul>
                {recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TitleGenerator; 