#!/usr/bin/env python3
"""
Performance Optimization Module for Viral AI System
Includes caching, batch processing, and memory optimization
"""

import time
import hashlib
import pickle
import os
from functools import lru_cache
from typing import Dict, List, Tuple, Any
import threading
from concurrent.futures import ThreadPoolExecutor
import json

class PerformanceOptimizer:
    def __init__(self, cache_dir="./cache", max_cache_size=1000):
        self.cache_dir = cache_dir
        self.max_cache_size = max_cache_size
        self.memory_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.processing_times = []
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
    def get_cache_key(self, content: str, platform: str = "") -> str:
        """Generate unique cache key for content analysis"""
        combined = f"{content}_{platform}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def cache_result(self, key: str, result: Any) -> None:
        """Cache analysis result both in memory and disk"""
        # Memory cache
        if len(self.memory_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = {
            'result': result,
            'timestamp': time.time()
        }
        
        # Disk cache for persistence
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(result, f)
        except Exception as e:
            print(f"Warning: Could not cache to disk: {e}")
    
    def get_cached_result(self, key: str) -> Tuple[Any, bool]:
        """Retrieve cached result if available"""
        # Check memory cache first
        if key in self.memory_cache:
            self.cache_hits += 1
            return self.memory_cache[key]['result'], True
        
        # Check disk cache
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    result = pickle.load(f)
                    # Add back to memory cache
                    self.memory_cache[key] = {
                        'result': result,
                        'timestamp': time.time()
                    }
                    self.cache_hits += 1
                    return result, True
            except Exception as e:
                print(f"Warning: Could not load from disk cache: {e}")
        
        self.cache_misses += 1
        return None, False
    
    def batch_analyze(self, contents: List[str], analyzer, platform: str = 'tiktok') -> List[Dict]:
        """Analyze multiple contents in parallel with caching"""
        print(f"🚀 Starting batch analysis of {len(contents)} items...")
        
        start_time = time.time()
        results = []
        
        def analyze_single(content_data):
            content, index = content_data
            cache_key = self.get_cache_key(content, platform)
            
            # Check cache first
            cached_result, is_cached = self.get_cached_result(cache_key)
            if is_cached:
                return index, cached_result, True
            
            # Perform analysis
            analysis_start = time.time()
            result = analyzer.calculate_comprehensive_viral_score(content, content, platform)
            analysis_time = time.time() - analysis_start
            
            # Cache the result
            self.cache_result(cache_key, result)
            
            return index, result, False
        
        # Process in parallel
        content_data = [(content, i) for i, content in enumerate(contents)]
        futures = []
        
        for data in content_data:
            future = self.thread_pool.submit(analyze_single, data)
            futures.append(future)
        
        # Collect results
        cached_count = 0
        computed_count = 0
        
        for future in futures:
            index, result, was_cached = future.result()
            results.append((index, result))
            
            if was_cached:
                cached_count += 1
            else:
                computed_count += 1
        
        # Sort by original index
        results.sort(key=lambda x: x[0])
        final_results = [result for _, result in results]
        
        total_time = time.time() - start_time
        avg_time = total_time / len(contents) * 1000  # ms per item
        
        print(f"✅ Batch analysis completed in {total_time:.2f}s")
        print(f"📊 {cached_count} cached, {computed_count} computed")
        print(f"⚡ Average time per item: {avg_time:.2f}ms")
        print(f"🎯 Cache hit rate: {cached_count/len(contents)*100:.1f}%")
        
        return final_results
    
    def optimize_memory(self):
        """Clean up memory cache and old disk cache files"""
        # Clean memory cache of old entries
        current_time = time.time()
        expired_keys = []
        
        for key, data in self.memory_cache.items():
            # Remove entries older than 1 hour
            if current_time - data['timestamp'] > 3600:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        # Clean disk cache
        cache_files = os.listdir(self.cache_dir)
        for cache_file in cache_files:
            if cache_file.endswith('.pkl'):
                file_path = os.path.join(self.cache_dir, cache_file)
                file_age = current_time - os.path.getctime(file_path)
                
                # Remove files older than 24 hours
                if file_age > 86400:
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Warning: Could not remove old cache file: {e}")
        
        print(f"🧹 Memory optimization completed. Removed {len(expired_keys)} expired entries.")
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        avg_processing_time = sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        
        return {
            'cache_hit_rate': hit_rate,
            'total_requests': total_requests,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'memory_cache_size': len(self.memory_cache),
            'avg_processing_time_ms': avg_processing_time * 1000,
            'estimated_daily_capacity': int(86400 / avg_processing_time) if avg_processing_time > 0 else 0
        }
    
    def benchmark_system(self, analyzer, sample_contents: List[str] = None):
        """Run comprehensive performance benchmark"""
        if sample_contents is None:
            sample_contents = [
                "What if I told you this secret will change your life forever?",
                "POV: You just discovered the ultimate productivity hack that successful people use",
                "The way rich people think vs poor people - this will blow your mind",
                "Nobody talks about this but here's the truth about manifesting money",
                "Red flags in relationships that everyone ignores but you shouldn't",
                "This morning routine changed my entire life in just 30 days",
                "The psychology behind why some people always win at everything",
                "How to become the main character in your own life story",
                "This controversial opinion about success will make you rethink everything",
                "The one habit that separates millionaires from everyone else"
            ]
        
        print("🔥 Running Performance Benchmark...")
        print("=" * 50)
        
        # Test 1: Single analysis performance
        print("\n⚡ Testing single analysis performance...")
        start_time = time.time()
        result = analyzer.calculate_comprehensive_viral_score(
            sample_contents[0], sample_contents[0], 'tiktok'
        )
        single_time = time.time() - start_time
        print(f"   Single analysis: {single_time*1000:.2f}ms")
        
        # Test 2: Batch processing performance
        print("\n🚀 Testing batch processing performance...")
        batch_results = self.batch_analyze(sample_contents, analyzer, 'tiktok')
        
        # Test 3: Cache performance
        print("\n💾 Testing cache performance...")
        cache_start = time.time()
        cached_results = self.batch_analyze(sample_contents[:5], analyzer, 'tiktok')
        cache_time = time.time() - cache_start
        print(f"   Cached batch time: {cache_time:.2f}s")
        
        # Test 4: Memory usage optimization
        print("\n🧹 Testing memory optimization...")
        initial_cache_size = len(self.memory_cache)
        self.optimize_memory()
        final_cache_size = len(self.memory_cache)
        print(f"   Cache size before: {initial_cache_size}")
        print(f"   Cache size after: {final_cache_size}")
        
        # Generate performance report
        stats = self.get_performance_stats()
        
        print("\n📊 PERFORMANCE REPORT")
        print("=" * 50)
        print(f"🎯 Cache Hit Rate: {stats['cache_hit_rate']:.1f}%")
        print(f"⚡ Avg Processing Time: {stats['avg_processing_time_ms']:.2f}ms")
        print(f"🚀 Estimated Daily Capacity: {stats['estimated_daily_capacity']:,} analyses")
        print(f"💾 Memory Cache Size: {stats['memory_cache_size']} items")
        print(f"📈 Total Requests: {stats['total_requests']}")
        
        # Performance recommendations
        print("\n💡 OPTIMIZATION RECOMMENDATIONS:")
        if stats['cache_hit_rate'] > 80:
            print("   ✅ Excellent cache performance!")
        elif stats['cache_hit_rate'] > 60:
            print("   ⚠️ Good cache performance, consider increasing cache size")
        else:
            print("   ❌ Low cache hit rate, optimize caching strategy")
        
        if stats['avg_processing_time_ms'] < 50:
            print("   ✅ Excellent processing speed!")
        elif stats['avg_processing_time_ms'] < 100:
            print("   ⚠️ Good processing speed, minor optimization possible")
        else:
            print("   ❌ Slow processing, significant optimization needed")
        
        return stats

class AdvancedBatchProcessor:
    """Advanced batch processing with priority queues and load balancing"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.high_priority_queue = []
        self.normal_priority_queue = []
        self.processing_stats = {
            'total_processed': 0,
            'total_time': 0,
            'error_count': 0
        }
    
    def add_to_queue(self, content: str, priority: str = 'normal', metadata: Dict = None):
        """Add content to processing queue"""
        item = {
            'content': content,
            'metadata': metadata or {},
            'timestamp': time.time()
        }
        
        if priority == 'high':
            self.high_priority_queue.append(item)
        else:
            self.normal_priority_queue.append(item)
    
    def process_queue(self, analyzer, optimizer: PerformanceOptimizer):
        """Process all items in queue with priority handling"""
        all_items = self.high_priority_queue + self.normal_priority_queue
        
        if not all_items:
            print("📭 No items in queue to process")
            return []
        
        print(f"🔄 Processing {len(all_items)} items from queue...")
        print(f"   High priority: {len(self.high_priority_queue)}")
        print(f"   Normal priority: {len(self.normal_priority_queue)}")
        
        contents = [item['content'] for item in all_items]
        results = optimizer.batch_analyze(contents, analyzer)
        
        # Combine results with metadata
        processed_results = []
        for i, result in enumerate(results):
            processed_results.append({
                'analysis': result,
                'metadata': all_items[i]['metadata'],
                'processing_time': time.time() - all_items[i]['timestamp']
            })
        
        # Update stats
        self.processing_stats['total_processed'] += len(results)
        
        # Clear queues
        self.high_priority_queue.clear()
        self.normal_priority_queue.clear()
        
        print(f"✅ Queue processing completed!")
        return processed_results

# Example usage and testing
if __name__ == "__main__":
    print("🚀 Performance Optimization System Test")
    
    # This would normally import the analyzer
    print("📊 Performance optimizer ready for integration!")
    print("   - Intelligent caching system")
    print("   - Parallel batch processing") 
    print("   - Memory optimization")
    print("   - Performance benchmarking")
    print("   - Priority queue processing")
