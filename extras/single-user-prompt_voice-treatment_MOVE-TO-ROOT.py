import subprocess
import os
import matchering as mg

def process_audio(input_file, output_wav, output_mp3):
    print("\nChecking if input file exists...")
    # Ensure the input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file {input_file} not found")
    print("File found successfully!")
    
    # Get path to RNNoise model and reference file relative to script location
    rnnoise_model = os.path.join(script_dir, "rnnoise-models", "beguiling-drafter-2018-08-30", "bd.rnnn")
    reference_file = os.path.join(script_dir, "christina-reference.wav")
    
    # Check if reference file exists
    if not os.path.exists(reference_file):
        raise FileNotFoundError(f"Reference file {reference_file} not found")
    
    # Create intermediate files
    intermediate_file = os.path.join(script_dir, "intermediate.wav")
    matched_file = os.path.join(script_dir, "matched_intermediate.wav")
    
    print("\nSetting up audio processing filters...")
    # Create the FFmpeg filter chain
    filters = [
        # Noise reduction using RNNoise
        f"arnndn=m='{rnnoise_model}'",  # Use RNNoise for denoising
        
        # EQ filters
        "highpass=f=150:p=2",  # 12 dB/oct lowcut at 150 Hz
        "equalizer=f=880:t=q:w=1:g=-4",  # -4 dB bell at 880 Hz
        "equalizer=f=5000:t=q:w=1:g=3",     # +4 dB bell at 5 kHz
        "lowpass=f=17500:p=2",              # 12 dB/oct lowpass at 17.5 kHz
        
        # Add SoX resampler
        "aresample=async=1:min_hard_comp=0.100001:first_pts=0:resampler=soxr",
    ]
    
    # Combine all filters
    filter_string = ','.join(filters)
    print("Filters configured successfully!")
    
    print("\nPreparing FFmpeg command with SoX resampling...")
    # Construct the FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', input_file,
        '-af', filter_string,
        '-ar', '48000',  # Target sample rate of 48kHz
        '-ac', '1',      # Force mono
        '-acodec', 'pcm_s24le',  # 24-bit WAV output
        intermediate_file,
        '-y'  # Overwrite output file if it exists
    ]
    
    try:
        print("\nProcessing audio file with SoX resampling and RNNoise...")
        # Execute FFmpeg command
        subprocess.run(cmd, check=True, capture_output=True)
        print("Initial processing complete. Starting matchering process...")
        
        # Apply matchering using reference file
        print("\nApplying reference matching...")
        mg.process(
            target=intermediate_file,
            reference=reference_file,
            results=[
                mg.pcm24(matched_file)
            ]
        )
        
        # Final processing to create WAV and MP3
        print("\nFinalizing audio formats...")
        
        # Create WAV output
        wav_cmd = [
            'ffmpeg',
            '-i', matched_file,
            '-ar', '48000',      # Force 48kHz
            '-ac', '1',          # Force mono
            '-acodec', 'pcm_s24le',
            output_wav,
            '-y'
        ]
        subprocess.run(wav_cmd, check=True, capture_output=True)
        
        # Create MP3 output
        mp3_cmd = [
            'ffmpeg',
            '-i', matched_file,
            '-ar', '48000',      # Force 48kHz
            '-ac', '1',          # Force mono
            '-codec:a', 'libmp3lame',
            '-b:a', '320k',      # High quality bitrate
            # Optional mobile optimization: uncomment the line below to reduce volume even further for mobile devices, currently normalized to match Resemble audio reference wav
            # '-af', 'volume=-25dB',  # Reduces volume by 25dB for futher device implementation
            output_mp3,
            '-y'
        ]
        subprocess.run(mp3_cmd, check=True, capture_output=True)
        
        # Clean up intermediate files
        os.remove(intermediate_file)
        os.remove(matched_file)
        
        print(f"\nSuccess! Processed files created:")
        print(f"WAV: {output_wav}")
        print(f"MP3: {output_mp3}")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError processing file: {e.stderr.decode()}")
        if os.path.exists(intermediate_file):
            os.remove(intermediate_file)
        if os.path.exists(matched_file):
            os.remove(matched_file)
        raise
    except Exception as e:
        print(f"\nError during processing: {str(e)}")
        if os.path.exists(intermediate_file):
            os.remove(intermediate_file)
        if os.path.exists(matched_file):
            os.remove(matched_file)
        raise

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Prompt user for input file path
    input_wav = input("\nPlease enter the path to your WAV file: ").strip("'\"")
    
    # Get just the filename from the input path
    input_filename = os.path.basename(input_wav)
    base_filename = os.path.splitext(input_filename)[0]
    
    # Create output paths in same directory as script
    output_wav = os.path.join(script_dir, f"{base_filename}_processed.wav")
    output_mp3 = os.path.join(script_dir, f"{base_filename}_mobile.mp3")
    
    process_audio(input_wav, output_wav, output_mp3)