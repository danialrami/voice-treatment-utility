# Voice Treatment Utility

[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) [![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/) [![FFmpeg](https://img.shields.io/badge/FFmpeg-required-orange.svg)](https://ffmpeg.org/) [![SoX](https://img.shields.io/badge/SoX-required-orange.svg)](http://sox.sourceforge.net/)

Copyright (c) 2024 Daniel Ramirez

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

Audio processing utility for enhancing OpenAI TTS outputs.
Developed as a complementary tool for audio post-processing workflows.

## Overview
This Python script provides batch processing capabilities for WAV audio files using FFmpeg and Matchering. It applies audio processing and converts outputs to both WAV (48kHz 24-bit) and MP3 formats. The script is specifically designed to process audio files from OpenAI's Text-to-Speech API (which outputs 24kHz 16-bit audio) to meet audio standards.

### Prerequisites
1. Install system requirements (MacOS):
```bash
brew install ffmpeg sox
```

2. Clone this repository:
```bash
git clone https://github.com/danialrami/voice-treatment-utility.git
cd voice-treatment-utility
```

3. Download RNNoise models:
```bash
# In a separate directory
git clone https://github.com/GregorR/rnnoise-models.git
# Create directories and copy the model
mkdir -p rnnoise-models/beguiling-drafter-2018-08-30
cp rnnoise-models/beguiling-drafter-2018-08-30/bd.rnnn ./rnnoise-models/beguiling-drafter-2018-08-30/
```

4. Install Python requirements:
```bash
pip install -r requirements.txt
```

5. Add your reference WAV file in the `references/`

### Required Directory Structure
```
voice-treatment-utility/
├── voice-treatment.py
├── requirements.txt
├── README.md
├── LICENSE.md
├── references/
│   └── christina-reference.wav    # Your reference file (not included)
└── rnnoise-models/
    └── beguiling-drafter-2018-08-30/
        └── bd.rnnn               # From rnnoise-models repository
```

## Features
- Batch processing of multiple WAV files
- Neural network-based noise reduction using RNNoise
- High-quality sample rate conversion (24kHz → 48kHz)
- Bit depth increase (16-bit → 24-bit)
- Audio filtering chain using FFmpeg
- Reference-based audio mastering using Matchering
- Organized dual format output (WAV and MP3)
- Progress tracking for batch operations

## Requirements
- Python 3.x
- FFmpeg with RNNoise and SoX resampler support
- RNNoise models (beguiling-drafter)
- Matchering library
- Reference WAV file for mastering
- Input WAV files (supports 24kHz 16-bit format)

## Installation
```bash
# Install system requirements (MacOS)
brew install ffmpeg sox

# Clone RNNoise models
git clone https://github.com/GregorR/rnnoise-models.git

# Install Python requirements
pip install -r requirements.txt
```

## Audio Processing Chain

### 1. Noise Reduction
- Uses RNNoise neural network model (beguiling-drafter)
- Optimized for studio-quality voice recordings
- Real-time processing with minimal artifacts

### 2. Equalization Filters
```
Input → RNNoise → Highpass → Bell EQ 1 → Bell EQ 2 → Lowpass → Resampling → Matchering → Dual Format Output
```

#### Filter Specifications
- **Highpass Filter**: 100 Hz, 12 dB/octave slope
- **First Bell EQ**: -4 dB at 880 Hz (Q=1)
- **Second Bell EQ**: +3 dB at 5 kHz (Q=1)
- **Lowpass Filter**: 17.5 kHz cutoff, 12 dB/octave slope

### 3. Sample Rate Conversion
Uses SoX Resampler (SOXR) with the following parameters:
- Async mode enabled
- Minimum hard compensation: 0.100001
- High-quality conversion algorithm

### 4. Reference Mastering
- Uses Matchering for professional-grade mastering
- Matches reference file characteristics
- Maintains consistent sound quality across all processed files

### 5. Dual Format Output
#### WAV Output
- Sample Rate: 48 kHz
- Bit Depth: 24-bit
- Format: WAV (PCM)
- Channels: Mono
- Location: wavs subdirectory

#### MP3 Output
- Sample Rate: 48 kHz
- Bitrate: 320 kbps
- Format: MP3
- Channels: Mono
- Location: main processed directory

## Usage
1. Ensure RNNoise models and reference file are in their respective directories
2. Run the script:
```bash
python3 voice-treatment.py
```
3. When prompted, enter the path to the directory containing your WAV files
4. The script will create a new directory with "_processed" suffix containing:
   - MP3 files with "_mobile" suffix in the main directory
   - WAV files with "_processed" suffix in a "wavs" subdirectory

### Output Structure Example
```
voice-treatment-utility/
├── input_directory/
│   ├── file1.wav
│   └── file2.wav
└── input_directory_processed/
    ├── file1_mobile.mp3
    ├── file2_mobile.mp3
    └── wavs/
        ├── file1_processed.wav
        └── file2_processed.wav
```

## Batch Processing Features
- Processes all WAV files in the specified directory
- Shows progress (X of Y files)
- Continues processing if individual files fail
- Maintains organized output structure
- Creates separate directories for WAV and MP3 outputs
- Preserves original files

## Error Handling
- Validates input directory existence
- Validates RNNoise model availability
- Validates reference file existence
- Provides detailed FFmpeg error messages
- Cleans up intermediate files automatically
- Maintains original files in case of processing errors
- Continues batch processing if individual files fail

## Notes
- Optimized for OpenAI TTS output processing
- Processing chain optimized for voice content
- RNNoise processing occurs before EQ to minimize artifacts
- SoX resampling used for highest quality conversion
- Optional mobile volume adjustment available (-25dB)
- Intermediate files automatically cleaned up
- Batch processing maintains consistent quality across files
- Progress tracking for large batch operations

## Limitations
- Input files must be WAV format
- Processing is done in real-time (no parallel processing)
- Output directory is created next to input directory
- Requires specific FFmpeg compilation with RNNoise support
- Reference file must be 48kHz WAV
- All files in batch use the same reference file for mastering

## Attribution and Licenses
This project uses the following open-source components:
- [Matchering](https://github.com/sergree/matchering) - Audio matching and mastering
- [RNNoise](https://github.com/xiph/rnnoise) - Neural network-based noise reduction
- [FFmpeg](https://ffmpeg.org/) - Audio processing framework
- [SoX](http://sox.sourceforge.net/) - Sound processing library

## Contributing
Contributions are welcome -- Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the GNU General Public License v2.0. For more details, see:
- The [LICENSE](LICENSE.md) file in this repository
- The official [GPL v2 license text](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

This choice of license ensures that any modifications or redistributions of this code must also remain open source, protecting the community's ability to use, study, share, and improve the software.

## Author
Daniel Ramirez
- GitHub: [@danialrami](https://github.com/danialrami)

## Acknowledgments
- [Sergree](https://github.com/sergree) for the Matchering library
- [Gregor Richards](https://github.com/GregorR) for the RNNoise models
- The FFmpeg and SoX teams for their tools
- OpenAI for their Text-to-Speech API