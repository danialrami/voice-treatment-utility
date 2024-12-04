import subprocess
import os
import matchering as mg
from pathlib import Path

def process_audio(input_file, output_wav, output_mp3, rnnoise_model, reference_file):
    print(f"\nProcessing: {os.path.basename(input_file)}")
    
    # Create intermediate files with unique names based on input filename
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    intermediate_file = os.path.join(script_dir, f"intermediate_{base_name}.wav")
    matched_file = os.path.join(script_dir, f"matched_{base_name}.wav")
    
    print("Setting up audio processing filters...")
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
    
    try:
        # Initial processing
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-af', filter_string,
            '-ar', '48000',
            '-ac', '1',
            '-acodec', 'pcm_s24le',
            intermediate_file,
            '-y'
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Apply matchering
        mg.process(
            target=intermediate_file,
            reference=reference_file,
            results=[
                mg.pcm24(matched_file)
            ]
        )
        
        # Create WAV output
        wav_cmd = [
            'ffmpeg',
            '-i', matched_file,
            '-ar', '48000',
            '-ac', '1',
            '-acodec', 'pcm_s24le',
            output_wav,
            '-y'
        ]
        subprocess.run(wav_cmd, check=True, capture_output=True)
        
        # Create MP3 output
        mp3_cmd = [
            'ffmpeg',
            '-i', matched_file,
            '-ar', '48000',
            '-ac', '1',
            '-codec:a', 'libmp3lame',
            '-b:a', '320k',
            output_mp3,
            '-y'
        ]
        subprocess.run(mp3_cmd, check=True, capture_output=True)
        
        # Clean up intermediate files
        os.remove(intermediate_file)
        os.remove(matched_file)
        
        print(f"Successfully processed: {os.path.basename(input_file)}")
        
    except Exception as e:
        print(f"Error processing {os.path.basename(input_file)}: {str(e)}")
        if os.path.exists(intermediate_file):
            os.remove(intermediate_file)
        if os.path.exists(matched_file):
            os.remove(matched_file)
        raise

def process_directory(input_dir):
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rnnoise_model = os.path.join(script_dir, "rnnoise-models", "beguiling-drafter-2018-08-30", "bd.rnnn")
    reference_file = os.path.join(script_dir, "references", "christina-reference.wav") # replace with your reference file
    
    # Validate required files
    if not os.path.exists(rnnoise_model):
        raise FileNotFoundError(f"RNNoise model not found at {rnnoise_model}")
    if not os.path.exists(reference_file):
        raise FileNotFoundError(f"Reference file not found at {reference_file}")
    
    # Create output directories
    input_dir_name = os.path.basename(os.path.normpath(input_dir))
    output_dir = os.path.join(os.path.dirname(input_dir), f"{input_dir_name}_processed")
    wavs_dir = os.path.join(output_dir, "wavs")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(wavs_dir, exist_ok=True)
    
    # Process all WAV files
    wav_files = list(Path(input_dir).glob("*.wav"))
    total_files = len(wav_files)
    
    print(f"\nFound {total_files} WAV files to process")
    
    for i, wav_file in enumerate(wav_files, 1):
        print(f"\nProcessing file {i} of {total_files}")
        base_name = wav_file.stem
        
        output_wav = os.path.join(wavs_dir, f"{base_name}_processed.wav")
        output_mp3 = os.path.join(output_dir, f"{base_name}_mobile.mp3")
        
        try:
            process_audio(str(wav_file), output_wav, output_mp3, rnnoise_model, reference_file)
        except Exception as e:
            print(f"Failed to process {base_name}: {str(e)}")
            continue

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Prompt user for input directory path
    input_dir = input("\nPlease enter the path to the directory containing WAV files: ").strip("'\"")
    
    if not os.path.exists(input_dir):
        print("Error: Directory not found")
        exit(1)
    
    process_directory(input_dir)
    print("\nProcessing complete!")