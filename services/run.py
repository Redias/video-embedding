#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
startup script for the function.
"""

import argparse
import json
import subprocess
from pathlib import Path

import ffmpeg
import numpy as np
import torch
import whisper
from transformers import CLIPProcessor, CLIPModel

from db.db_ops import VideoEmbeddingDB
from utils import Logger


logger = Logger()


def parse_args():
    parser = argparse.ArgumentParser(description="Video embedding processor")
    parser.add_argument(
        "--input", "-i", type=str, required=True, help="Input video file path"
    )
    parser.add_argument(
        "--output", "-o", type=str, required=True, help="Output video file path"
    )
    parser.add_argument(
        "--segment-duration",
        "-d",
        type=float,
        default=1.0,
        help="Duration of each video segment in seconds",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to run models on (cuda/cpu)",
    )
    return parser.parse_args()


def extract_video_segments(input_path, segment_duration):
    """Extract video segments using ffmpeg"""
    segments = []
    probe = ffmpeg.probe(input_path)
    duration = float(probe["format"]["duration"])

    for start_time in np.arange(0, duration, segment_duration):
        end_time = min(start_time + segment_duration, duration)

        # Extract video frame
        frame_data = (
            ffmpeg.input(input_path, ss=start_time, t=segment_duration)
            .output("pipe:", format="rawvideo", pix_fmt="rgb24", vframes=1)
            .run(capture_stdout=True, quiet=True)
        )[0]

        # Extract audio segment
        audio_data = (
            ffmpeg.input(input_path, ss=start_time, t=segment_duration)
            .output("pipe:", format="wav", acodec="pcm_s16le", ac=1, ar=16000)
            .run(capture_stdout=True, quiet=True)
        )[0]

        segments.append(
            {
                "start_time": start_time,
                "end_time": end_time,
                "frame_data": frame_data,
                "audio_data": audio_data,
            }
        )

    return segments


def process_segments(segments, device):
    """Process video segments with CLIP and Whisper"""
    # Initialize models
    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    whisper_model = whisper.load_model("base").to(device)

    results = []
    for segment in segments:
        # Process video frame with CLIP
        frame_tensor = clip_processor(
            images=segment["frame_data"], return_tensors="pt"
        ).to(device)
        frame_features = clip_model.get_image_features(**frame_tensor)

        # Process audio with Whisper
        audio_features = whisper_model.transcribe(segment["audio_data"])

        results.append(
            {
                "start_time": segment["start_time"],
                "end_time": segment["end_time"],
                "frame_embedding": frame_features.cpu().numpy(),
                "text_transcription": audio_features["text"],
            }
        )

    return results


def encode_video_with_metadata(input_path, output_path, metadata):
    """Encode video with embedded metadata"""
    metadata_str = json.dumps(metadata)

    # Create ffmpeg command
    stream = (
        ffmpeg.input(input_path)
        .output(output_path, metadata=f"embedding_data={metadata_str}")
        .overwrite_output()
    )

    # Run ffmpeg command
    stream.run()


def main():
    args = parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {args.input}")
        raise FileNotFoundError(f"Input file not found: {args.input}")
    
    logger.info(f"Processing video: {args.input}")
    
    # Extract video segments
    segments = extract_video_segments(args.input, args.segment_duration)
    logger.info(f"Extracted {len(segments)} segments")
    
    # Process segments with CLIP and Whisper
    results = process_segments(segments, args.device)
    logger.info("Processed all segments with CLIP and Whisper")
    
    # Store results in database
    with VideoEmbeddingDB() as db:
        probe = ffmpeg.probe(args.input)
        duration = float(probe["format"]["duration"])
        video_id = db.add_video(args.input, duration)
        
        for result in results:
            db.add_frame_embedding(video_id, result)
    
    # Encode video with metadata
    encode_video_with_metadata(args.input, args.output, results)
    logger.info(f"Video processing complete. Output saved to: {args.output}")


if __name__ == "__main__":
    main()
