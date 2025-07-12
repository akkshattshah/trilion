#!/bin/bash
FILTER=$(cat filter.txt)
ffmpeg -y -i media/clip_1751485379352_1.mp4 -vf "$FILTER" -c:a copy media/clip_1751485379352_1_SYNCED.mp4 