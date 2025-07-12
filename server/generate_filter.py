#!/usr/bin/env python3
import sys
import subprocess

if __name__ == "__main__":
    transcript = sys.argv[1]
    filter_txt = sys.argv[2]
    result = subprocess.run([
        'python3', 'simple_subtitle_generator.py', transcript
    ], capture_output=True, text=True)
    with open(filter_txt, 'w') as f:
        f.write(result.stdout.strip()) 