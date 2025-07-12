#!/usr/bin/env python3
"""
Comprehensive Testing Suite for Enhanced Viral AI System
Tests all components and provides performance benchmarks
"""

import time
import json
import sys
from intelligent_clip_analyzer import AdvancedViralContentAnalyzer

class ViralAITestSuite:
    def __init__(self):
        self.analyzer = AdvancedViralContentAnalyzer()
        self.test_results = []
        
    def run_comprehensive_tests(self):
        """Run all tests and generate report"""
        print("🧪 Starting Comprehensive Viral AI Test Suite...")
        print("=" * 60)
        
        # Test 1: Hook Pattern Recognition
        self.test_hook_patterns()
        
        # Test 2: Platform Optimization
        self.test_platform_optimization()
        
        # Test 3: Emotional Intensity Detection
        self.test_emotional_detection()
        
        # Test 4: Trend Alignment
        self.test_trend_alignment()
        
        # Test 5: Performance Benchmarks
        self.test_performance()
        
        # Test 6: Real-world Content Samples
        self.test_real_content()
        
        # Generate final report
        self.generate_test_report()
        
    def test_hook_patterns(self):
        """Test viral hook pattern recognition"""
        print("\n🪝 Testing Hook Pattern Recognition...")
        
        test_cases = [
            {
                'text': 'What if I told you that billionaires use this secret method?',
                'expected_hook': 'curiosity_gaps',
                'expected_score': 8.0
            },
            {
                'text': 'POV: You just discovered the ultimate life hack',
                'expected_hook': 'general',
                'expected_score': 6.0
            },
            {
                'text': 'Story time about the craziest thing that happened to me',
                'expected_hook': 'story_hooks',
                'expected_score': 7.0
            },
            {
                'text': 'Did you know that 90% of people make this mistake?',
                'expected_hook': 'question_hooks',
                'expected_score': 9.0
            },
            {
                'text': 'Rich vs Poor mindset - the difference will shock you',
                'expected_hook': 'comparison_hooks',
                'expected_score': 6.0
            }
        ]
        
        passed = 0
        for i, case in enumerate(test_cases, 1):
            hook_score, hook_type = self.analyzer.analyze_hook_strength(case['text'].lower())
            
            # Check hook type detection
            hook_correct = hook_type == case['expected_hook'] or hook_score >= case['expected_score']
            
            if hook_correct:
                print(f"   ✅ Test {i}: PASSED - Hook: {hook_type}, Score: {hook_score:.1f}")
                passed += 1
            else:
                print(f"   ❌ Test {i}: FAILED - Expected: {case['expected_hook']}, Got: {hook_type}")
        
        self.test_results.append({
            'test': 'Hook Pattern Recognition',
            'passed': passed,
            'total': len(test_cases),
            'score': passed / len(test_cases) * 100
        })
        
    def test_platform_optimization(self):
        """Test platform-specific optimization"""
        print("\n🎯 Testing Platform Optimization...")
        
        test_content = "POV: You're living your best life with this aesthetic morning routine"
        
        platforms = ['tiktok', 'instagram', 'youtube_shorts']
        results = {}
        
        for platform in platforms:
            score = self.analyzer.analyze_platform_optimization(test_content.lower(), platform)
            results[platform] = score
            print(f"   📱 {platform.title()}: {score:.1f}/10")
        
        # Instagram should score highest for this aesthetic content
        best_platform = max(results, key=results.get)
        expected = 'instagram'
        
        passed = 1 if best_platform == expected else 0
        
        self.test_results.append({
            'test': 'Platform Optimization',
            'passed': passed,
            'total': 1,
            'score': passed * 100,
            'details': results
        })
        
    def test_emotional_detection(self):
        """Test emotional intensity detection"""
        print("\n💥 Testing Emotional Intensity Detection...")
        
        test_cases = [
            {
                'text': 'This is INSANE! You won\'t believe this mind-blowing discovery!',
                'expected_min': 8.0
            },
            {
                'text': 'This controversial opinion will shock everyone',
                'expected_min': 6.0
            },
            {
                'text': 'Here is some basic information about the topic',
                'expected_min': 0.0,
                'expected_max': 3.0
            }
        ]
        
        passed = 0
        for i, case in enumerate(test_cases, 1):
            intensity = self.analyzer.analyze_emotional_intensity(case['text'].lower())
            
            min_expected = case['expected_min']
            max_expected = case.get('expected_max', 10.0)
            
            if min_expected <= intensity <= max_expected:
                print(f"   ✅ Test {i}: PASSED - Intensity: {intensity:.1f}")
                passed += 1
            else:
                print(f"   ❌ Test {i}: FAILED - Expected: {min_expected}-{max_expected}, Got: {intensity:.1f}")
        
        self.test_results.append({
            'test': 'Emotional Intensity Detection',
            'passed': passed,
            'total': len(test_cases),
            'score': passed / len(test_cases) * 100
        })
        
    def test_trend_alignment(self):
        """Test trend alignment detection"""
        print("\n📈 Testing Trend Alignment...")
        
        test_cases = [
            {
                'text': 'soft life main character energy morning routine',
                'expected_min': 4.0
            },
            {
                'text': 'passive income side hustle digital nomad lifestyle',
                'expected_min': 3.0
            },
            {
                'text': 'random content with no trending topics',
                'expected_max': 2.0
            }
        ]
        
        passed = 0
        for i, case in enumerate(test_cases, 1):
            trend_score = self.analyzer.analyze_trend_alignment(case['text'].lower())
            
            min_expected = case.get('expected_min', 0.0)
            max_expected = case.get('expected_max', 10.0)
            
            if min_expected <= trend_score <= max_expected:
                print(f"   ✅ Test {i}: PASSED - Trend Score: {trend_score:.1f}")
                passed += 1
            else:
                print(f"   ❌ Test {i}: FAILED - Expected: {min_expected}-{max_expected}, Got: {trend_score:.1f}")
        
        self.test_results.append({
            'test': 'Trend Alignment',
            'passed': passed,
            'total': len(test_cases),
            'score': passed / len(test_cases) * 100
        })
        
    def test_performance(self):
        """Test performance benchmarks"""
        print("\n⚡ Testing Performance Benchmarks...")
        
        test_text = "What if I told you that this viral content strategy will change your entire approach to social media marketing forever?"
        
        # Test comprehensive scoring speed
        start_time = time.time()
        for _ in range(100):
            scores = self.analyzer.calculate_comprehensive_viral_score(test_text, test_text, 'tiktok')
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100 * 1000  # ms per analysis
        
        print(f"   ⏱️ Average analysis time: {avg_time:.2f}ms")
        print(f"   🎯 Throughput: {1000/avg_time:.0f} analyses per second")
        
        # Performance should be under 50ms per analysis
        performance_passed = avg_time < 50.0
        
        self.test_results.append({
            'test': 'Performance Benchmark',
            'passed': 1 if performance_passed else 0,
            'total': 1,
            'score': 100 if performance_passed else 0,
            'avg_time_ms': avg_time
        })
        
    def test_real_content(self):
        """Test with real-world content samples"""
        print("\n🌍 Testing Real-World Content Samples...")
        
        real_samples = [
            "Nobody talks about this but here's the truth about starting a business that will save you years of mistakes",
            "The way I manifested my dream life in 30 days using this simple technique that anyone can do",
            "POV: You're the main character in your own life and you finally stopped caring what others think",
            "This productivity hack changed everything - from chaos to organized in just 5 minutes",
            "Red flags in friendships that everyone ignores but you shouldn't"
        ]
        
        total_score = 0
        high_quality_clips = 0
        
        for i, sample in enumerate(real_samples, 1):
            scores = self.analyzer.calculate_comprehensive_viral_score(sample, sample, 'tiktok')
            total_score += scores['total_score']
            
            if scores['total_score'] >= 15.0:  # High quality threshold
                high_quality_clips += 1
                
            print(f"   📊 Sample {i}: {scores['total_score']:.1f}/10 - {scores['viral_category']}")
        
        avg_score = total_score / len(real_samples)
        quality_rate = high_quality_clips / len(real_samples) * 100
        
        self.test_results.append({
            'test': 'Real-World Content',
            'passed': high_quality_clips,
            'total': len(real_samples),
            'score': quality_rate,
            'avg_score': avg_score
        })
        
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_passed = sum(result['passed'] for result in self.test_results)
        total_tests = sum(result['total'] for result in self.test_results)
        overall_score = total_passed / total_tests * 100
        
        print(f"\n🎯 OVERALL PERFORMANCE: {overall_score:.1f}%")
        print(f"📈 Total Tests: {total_tests}")
        print(f"✅ Passed: {total_passed}")
        print(f"❌ Failed: {total_tests - total_passed}")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASSED" if result['score'] >= 80 else "⚠️ NEEDS IMPROVEMENT" if result['score'] >= 60 else "❌ FAILED"
            print(f"   {result['test']}: {result['score']:.1f}% {status}")
        
        # Performance insights
        perf_result = next(r for r in self.test_results if r['test'] == 'Performance Benchmark')
        print(f"\n⚡ PERFORMANCE INSIGHTS:")
        print(f"   Average Analysis Time: {perf_result['avg_time_ms']:.2f}ms")
        print(f"   Estimated Daily Capacity: {86400000 / perf_result['avg_time_ms']:.0f} analyses")
        
        # Quality insights
        real_result = next(r for r in self.test_results if r['test'] == 'Real-World Content')
        print(f"\n🌍 CONTENT QUALITY INSIGHTS:")
        print(f"   High-Quality Detection Rate: {real_result['score']:.1f}%")
        print(f"   Average Viral Score: {real_result['avg_score']:.1f}/10")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if overall_score >= 90:
            print("   🔥 System is performing exceptionally well!")
            print("   🚀 Ready for production deployment")
        elif overall_score >= 80:
            print("   ✨ System is performing well with minor optimization opportunities")
            print("   🎯 Consider fine-tuning low-scoring components")
        else:
            print("   ⚠️ System needs significant improvements before production")
            print("   🔧 Focus on failed test categories first")
        
        return {
            'overall_score': overall_score,
            'total_tests': total_tests,
            'passed': total_passed,
            'results': self.test_results
        }

if __name__ == "__main__":
    print("🧪 Enhanced Viral AI Testing Suite")
    print("Testing next-generation viral content analysis system...")
    
    suite = ViralAITestSuite()
    report = suite.run_comprehensive_tests()
    
    # Save detailed report
    with open('viral_ai_test_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: viral_ai_test_report.json")
    
    # Exit with appropriate code
    sys.exit(0 if report['overall_score'] >= 80 else 1)
