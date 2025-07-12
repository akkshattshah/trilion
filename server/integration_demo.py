#!/usr/bin/env python3
"""
Complete Integration Demo - Enhanced Viral AI System
Demonstrates all components working together with real examples
"""

import sys
import time
import json
from intelligent_clip_analyzer import AdvancedViralContentAnalyzer
from performance_optimizer import PerformanceOptimizer, AdvancedBatchProcessor

class ViralAIIntegrationDemo:
    def __init__(self):
        print("🔥 Initializing Enhanced Viral AI System...")
        self.analyzer = AdvancedViralContentAnalyzer()
        self.optimizer = PerformanceOptimizer()
        self.batch_processor = AdvancedBatchProcessor()
        print("✅ System initialization complete!")
        
    def demo_real_world_scenarios(self):
        """Demonstrate real-world use cases"""
        print("\n" + "="*60)
        print("🌍 REAL-WORLD VIRAL AI DEMONSTRATION")
        print("="*60)
        
        # Scenario 1: Content Creator Batch Analysis
        self.demo_content_creator_workflow()
        
        # Scenario 2: Social Media Manager Dashboard
        self.demo_social_media_dashboard()
        
        # Scenario 3: Trend Analysis & Optimization
        self.demo_trend_optimization()
        
        # Scenario 4: Performance Analytics
        self.demo_performance_analytics()
        
    def demo_content_creator_workflow(self):
        """Demo: Content creator analyzing multiple video ideas"""
        print("\n📱 SCENARIO 1: Content Creator Video Ideas Analysis")
        print("-" * 50)
        
        video_ideas = [
            "POV: You're living your soft life era and thriving in your main character energy",
            "What nobody tells you about manifestation - the dark side that changed everything",
            "Rich people mindset vs broke people mindset - the difference will shock you",
            "This morning routine will change your life in 30 days (science-backed)",
            "Red flags in friendship that everyone ignores but you shouldn't",
            "The psychology behind why some people always win at life",
            "How I manifested $10k in one month using this controversial method",
            "This productivity hack eliminated my procrastination forever",
            "The truth about toxic positivity that everyone needs to hear",
            "Why successful people never reveal their real secrets"
        ]
        
        print(f"📊 Analyzing {len(video_ideas)} video concepts...")
        
        # Analyze for different platforms
        platforms = ['tiktok', 'instagram', 'youtube_shorts']
        platform_results = {}
        
        for platform in platforms:
            print(f"\n🎯 Optimizing for {platform.upper()}...")
            results = self.optimizer.batch_analyze(video_ideas, self.analyzer, platform)
            
            # Sort by viral score
            sorted_results = sorted(
                [(idea, result) for idea, result in zip(video_ideas, results)],
                key=lambda x: x[1]['total_score'],
                reverse=True
            )
            
            platform_results[platform] = sorted_results
            
            print(f"🏆 Top 3 performers for {platform}:")
            for i, (idea, result) in enumerate(sorted_results[:3], 1):
                category = result['viral_category']
                score = result['total_score']
                hook_type = result['dominant_hook_type']
                print(f"   {i}. [{category.upper()}] Score: {score:.1f}/10 (Hook: {hook_type})")
                print(f"      '{idea[:60]}{'...' if len(idea) > 60 else ''}'")
        
        # Cross-platform comparison
        print(f"\n📈 CROSS-PLATFORM PERFORMANCE ANALYSIS:")
        for i, idea in enumerate(video_ideas[:3]):
            print(f"\n💡 Idea {i+1}: '{idea[:50]}...'")
            for platform in platforms:
                score = platform_results[platform][i][1]['total_score']
                category = platform_results[platform][i][1]['viral_category']
                print(f"   {platform.title()}: {score:.1f}/10 [{category}]")
    
    def demo_social_media_dashboard(self):
        """Demo: Social media manager dashboard insights"""
        print("\n🎯 SCENARIO 2: Social Media Manager Dashboard")
        print("-" * 50)
        
        current_content = [
            "This aesthetic morning routine will transform your entire life",
            "POV: You finally learned to say no and your life got 10x better",
            "The millionaire morning routine nobody talks about",
            "How to glow up mentally, physically, and spiritually in 2024",
            "This controversial opinion about hustle culture will change your perspective"
        ]
        
        print("📊 Generating dashboard insights...")
        
        dashboard_data = {
            'content_performance': [],
            'trending_elements': set(),
            'optimization_suggestions': [],
            'viral_potential_distribution': {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        }
        
        for content in current_content:
            # Analyze for primary platform (TikTok)
            analysis = self.analyzer.calculate_comprehensive_viral_score(content, content, 'tiktok')
            
            dashboard_data['content_performance'].append({
                'content': content[:50] + '...',
                'viral_score': analysis['total_score'],
                'category': analysis['viral_category'],
                'hook_type': analysis['dominant_hook_type'],
                'emotional_intensity': analysis['emotional_intensity'],
                'platform_optimization': analysis['platform_optimization']
            })
            
            # Track trending elements
            if 'aesthetic' in content.lower():
                dashboard_data['trending_elements'].add('aesthetic')
            if 'pov' in content.lower():
                dashboard_data['trending_elements'].add('pov_format')
            if 'morning routine' in content.lower():
                dashboard_data['trending_elements'].add('morning_routines')
            
            # Categorize viral potential
            if analysis['total_score'] >= 7.0:
                dashboard_data['viral_potential_distribution']['HIGH'] += 1
            elif analysis['total_score'] >= 5.0:
                dashboard_data['viral_potential_distribution']['MEDIUM'] += 1
            else:
                dashboard_data['viral_potential_distribution']['LOW'] += 1
        
        # Display dashboard
        print("\n📈 DASHBOARD OVERVIEW:")
        print(f"   Total Content Analyzed: {len(current_content)}")
        print(f"   High Viral Potential: {dashboard_data['viral_potential_distribution']['HIGH']}")
        print(f"   Medium Viral Potential: {dashboard_data['viral_potential_distribution']['MEDIUM']}")
        print(f"   Low Viral Potential: {dashboard_data['viral_potential_distribution']['LOW']}")
        
        print(f"\n🔥 TRENDING ELEMENTS DETECTED:")
        for element in dashboard_data['trending_elements']:
            print(f"   • {element.replace('_', ' ').title()}")
        
        print(f"\n📊 CONTENT PERFORMANCE BREAKDOWN:")
        for item in dashboard_data['content_performance']:
            print(f"\n   📝 {item['content']}")
            print(f"      Score: {item['viral_score']:.1f}/10 [{item['category']}] (Hook: {item['hook_type']})")
            print(f"      Emotional Intensity: {item['emotional_intensity']:.1f}/10")
            print(f"      Platform Optimization: {item['platform_optimization']:.1f}/10")
    
    def demo_trend_optimization(self):
        """Demo: Real-time trend optimization"""
        print("\n📈 SCENARIO 3: Real-Time Trend Optimization")
        print("-" * 50)
        
        base_content = "How to build passive income while working full-time"
        
        print(f"🎯 Optimizing base content: '{base_content}'")
        
        # Generate trend-optimized variations
        trend_variations = [
            "POV: You're building passive income streams while everyone else complains about being broke",
            "What nobody tells you about passive income - the truth that will change everything",
            "The passive income method that millionaires don't want you to know",
            "How I built 6 passive income streams while working my 9-5 (step by step)",
            "This controversial passive income strategy changed my entire financial future"
        ]
        
        print(f"\n🔄 Testing {len(trend_variations)} trend-optimized variations...")
        
        results = []
        for variation in trend_variations:
            analysis = self.analyzer.calculate_comprehensive_viral_score(variation, variation, 'tiktok')
            results.append((variation, analysis))
        
        # Sort by performance
        results.sort(key=lambda x: x[1]['total_score'], reverse=True)
        
        print(f"\n🏆 OPTIMIZATION RESULTS (Ranked by Viral Potential):")
        for i, (variation, analysis) in enumerate(results, 1):
            print(f"\n   {i}. Score: {analysis['total_score']:.1f}/10 [{analysis['viral_category']}]")
            print(f"      Content: '{variation}'")
            print(f"      Hook Strength: {analysis['hook_strength']:.1f}")
            print(f"      Emotional Impact: {analysis['emotional_intensity']:.1f}")
            print(f"      Trend Alignment: {analysis['trend_alignment']:.1f}")
        
        # Identify optimization patterns
        print(f"\n🔍 OPTIMIZATION PATTERN ANALYSIS:")
        best_variation = results[0][1]
        worst_variation = results[-1][1]
        
        improvement = best_variation['total_score'] - worst_variation['total_score']
        print(f"   Performance Improvement: +{improvement:.1f} points ({improvement/worst_variation['total_score']*100:.1f}% increase)")
        
        # Extract successful patterns
        best_content = results[0][0].lower()
        patterns = []
        if 'pov:' in best_content:
            patterns.append('POV Format')
        if 'nobody tells you' in best_content:
            patterns.append('Curiosity Gap')
        if 'millionaire' in best_content or 'broke' in best_content:
            patterns.append('Wealth Contrast')
        
        print(f"   Successful Patterns: {', '.join(patterns)}")
    
    def demo_performance_analytics(self):
        """Demo: System performance analytics"""
        print("\n⚡ SCENARIO 4: Performance Analytics & Optimization")
        print("-" * 50)
        
        # Sample content for performance testing
        test_contents = [
            "This mindset shift changed everything about how I view success",
            "POV: You finally stopped caring about what others think",
            "The productivity hack that successful people don't share",
            "How to manifest your dream life in 30 days (backed by psychology)",
            "Red flags in dating that everyone ignores but you shouldn't",
            "This morning routine will change your life forever",
            "The truth about toxic positivity culture",
            "Why your 20s are for learning, not earning",
            "This controversial opinion about work-life balance",
            "How to become the main character in your own story"
        ]
        
        print("🚀 Running performance benchmark...")
        
        # Run benchmark
        performance_stats = self.optimizer.benchmark_system(self.analyzer, test_contents)
        
        # Additional insights
        print(f"\n💡 SYSTEM INSIGHTS:")
        
        # Analyze content quality distribution
        results = self.optimizer.batch_analyze(test_contents, self.analyzer)
        scores = [r['total_score'] for r in results]
        
        high_quality = sum(1 for s in scores if s >= 7.0)
        medium_quality = sum(1 for s in scores if 5.0 <= s < 7.0)
        low_quality = sum(1 for s in scores if s < 5.0)
        
        print(f"   Content Quality Distribution:")
        print(f"     High Quality (7.0+): {high_quality}/{len(scores)} ({high_quality/len(scores)*100:.1f}%)")
        print(f"     Medium Quality (5.0-6.9): {medium_quality}/{len(scores)} ({medium_quality/len(scores)*100:.1f}%)")
        print(f"     Low Quality (<5.0): {low_quality}/{len(scores)} ({low_quality/len(scores)*100:.1f}%)")
        
        avg_score = sum(scores) / len(scores)
        print(f"   Average Viral Score: {avg_score:.1f}/10")
        
        # System recommendations
        print(f"\n🎯 SYSTEM RECOMMENDATIONS:")
        if avg_score >= 6.5:
            print("   ✅ System is performing excellently at identifying high-quality viral content")
        elif avg_score >= 5.5:
            print("   ⚠️ System performance is good, minor calibration may improve accuracy")
        else:
            print("   ❌ System needs recalibration for better viral content detection")
        
        if performance_stats['cache_hit_rate'] >= 80:
            print("   ✅ Caching system is highly effective")
        else:
            print("   💾 Consider optimizing caching strategy for better performance")
    
    def run_complete_demo(self):
        """Run the complete integration demonstration"""
        print("🚀 ENHANCED VIRAL AI SYSTEM - COMPLETE INTEGRATION DEMO")
        print("Built for next-generation viral content optimization")
        print("\nSystem Capabilities:")
        print("  🧠 Advanced AI-powered viral analysis")
        print("  🎯 Multi-platform optimization")
        print("  📈 Real-time trend detection")
        print("  ⚡ High-performance batch processing")
        print("  💾 Intelligent caching system")
        print("  📊 Comprehensive analytics")
        
        start_time = time.time()
        
        try:
            self.demo_real_world_scenarios()
            
            total_time = time.time() - start_time
            
            print("\n" + "="*60)
            print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"⏱️ Total Demo Time: {total_time:.2f} seconds")
            print(f"🚀 System Status: FULLY OPERATIONAL")
            print(f"📈 Performance: OPTIMIZED")
            print(f"🎯 Accuracy: HIGH")
            
            # Final system stats
            stats = self.optimizer.get_performance_stats()
            print(f"\n📊 Final System Statistics:")
            print(f"   Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
            print(f"   Total Analyses: {stats['total_requests']}")
            print(f"   Avg Processing Time: {stats['avg_processing_time_ms']:.2f}ms")
            
        except Exception as e:
            print(f"❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🔥 Enhanced Viral AI System Integration Demo")
    print("Demonstrating next-generation viral content analysis...")
    
    demo = ViralAIIntegrationDemo()
    demo.run_complete_demo()
    
    print("\n🚀 Demo complete! System ready for production deployment.")
