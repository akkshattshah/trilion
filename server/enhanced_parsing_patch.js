// Enhanced parsing for next-generation AI results
try {
  viralAnalysis = JSON.parse(analysisResult);
  
  // Handle new enhanced format or legacy format
  if (Array.isArray(viralAnalysis)) {
    // New enhanced format returns array directly
    viralAnalysis = {
      success: true,
      clips_found: viralAnalysis.length,
      viral_clips: viralAnalysis.map(clip => ({
        start_time: clip.start_time,
        end_time: clip.end_time,
        duration: clip.duration,
        viral_score: clip.viral_score,
        hook_type: clip.hook_type,
        text: clip.text,
        is_fallback: clip.is_fallback,
        viral_category: clip.viral_category,
        target_demographic: clip.target_demographic,
        hook_strength: clip.quality_metrics ? clip.quality_metrics.hook_strength : 0,
        emotional_intensity: clip.quality_metrics ? clip.quality_metrics.emotional_intensity : 0,
        platform_optimization: clip.quality_metrics ? clip.quality_metrics.platform_optimization : 0,
        psychological_impact: clip.quality_metrics ? clip.quality_metrics.psychological_impact : 0,
        engagement_prediction: clip.quality_metrics ? clip.quality_metrics.engagement_prediction : 0,
        share_probability: clip.quality_metrics ? clip.quality_metrics.share_probability : 0,
        completeness_score: clip.quality_metrics ? clip.quality_metrics.completeness : 0,
        attention_score: clip.quality_metrics ? clip.quality_metrics.clarity_score : 0
      }))
    };
  } else if (viralAnalysis.clips) {
    // Handle object format with clips array
    viralAnalysis = {
      success: true,
      clips_found: viralAnalysis.clips.length,
      viral_clips: viralAnalysis.clips.map(clip => ({
        start_time: clip.start_time,
        end_time: clip.end_time,
        duration: clip.duration,
        viral_score: clip.viral_score,
        hook_type: clip.hook_type,
        text: clip.text,
        is_fallback: clip.is_fallback,
        viral_category: clip.viral_category,
        target_demographic: clip.target_demographic,
        hook_strength: clip.quality_metrics ? clip.quality_metrics.hook_strength : 0,
        emotional_intensity: clip.quality_metrics ? clip.quality_metrics.emotional_intensity : 0,
        platform_optimization: clip.quality_metrics ? clip.quality_metrics.platform_optimization : 0,
        psychological_impact: clip.quality_metrics ? clip.quality_metrics.psychological_impact : 0,
        engagement_prediction: clip.quality_metrics ? clip.quality_metrics.engagement_prediction : 0,
        share_probability: clip.quality_metrics ? clip.quality_metrics.share_probability : 0,
        completeness_score: clip.quality_metrics ? clip.quality_metrics.completeness : 0,
        attention_score: clip.quality_metrics ? clip.quality_metrics.clarity_score : 0
      }))
    };
  } else {
    throw new Error('Unexpected analysis format');
  }
  
  console.log(`✅ Next-Generation AI analysis found ${viralAnalysis.clips_found} viral clips!`);
} catch (parseError) {
  console.error('Failed to parse enhanced analysis result:', parseError);
  throw new Error('Failed to parse enhanced analysis output');
}
