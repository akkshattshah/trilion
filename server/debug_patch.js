// Debug enhanced version - replace the raw extraction section

        console.log(`🎬 Creating viral clip ${i + 1}/${clipData.length}...`);
        console.log(`�� Clip timing: startSeconds=${startSeconds}, duration=${duration}, endSeconds=${startSeconds + duration}`);
        console.log(`📁 File paths: raw=${rawFilename}, cropped=${croppedFilename}, final=${clipFilename}`);
        
        // STEP 1: Extract raw clip segment with debug info and proper encoding
        console.log('🎞️  STEP 1: Extracting raw clip with re-encoding to fix sync...');
        console.log(`📋 Raw extraction command will be: ffmpeg -i ${videoPath} -ss ${startSeconds} -t ${duration} -c:v libx264 -c:a aac -y ${rawPath}`);
        
        const rawCmd = [
          'ffmpeg', '-i', videoPath,
          '-ss', startSeconds.toString(),
          '-t', duration.toString(),
          '-c:v', 'libx264', '-c:a', 'aac', '-y', rawPath
        ];
        
        const rawStartTime = Date.now();
        const rawResult = spawnSync(rawCmd[0], rawCmd.slice(1), { stdio: 'inherit' });
        const rawEndTime = Date.now();
        
        console.log(`⏱️  Raw extraction took ${rawEndTime - rawStartTime}ms`);
        
        if (rawResult.status !== 0) {
          console.error(`❌ Raw clip extraction failed for clip ${i + 1} with exit code ${rawResult.status}`);
          continue;
        }
        
        // Check raw file properties
        try {
          const rawStats = fs.statSync(rawPath);
          console.log(`📊 Raw clip created: ${rawStats.size} bytes`);
          
          // Probe raw video metadata
          const { execSync } = require('child_process');
          const probeCmd = `ffprobe -v quiet -select_streams v:0 -show_entries stream=duration,start_time,codec_name,width,height -of csv=p=0 "${rawPath}"`;
          const rawMetadata = execSync(probeCmd, { encoding: 'utf8' }).trim();
          console.log(`🔍 Raw clip metadata: ${rawMetadata}`);
        } catch (probeError) {
          console.warn(`⚠️  Could not probe raw clip metadata: ${probeError.message}`);
        }

        let sourceForScaling = rawPath;

        // DEBUG LOGS for mode
        const normalizedProcessingMode = (processingMode || '').toLowerCase().trim();
        console.log(`🎯 DEBUG: processingMode=${processingMode} | normalizedProcessingMode=${normalizedProcessingMode} | globalProcessingMethod=${globalProcessingMethod}`);
