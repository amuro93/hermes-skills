#!/usr/bin/env python3
"""Generate exact LTX 2.3 i2v workflow JSON (46 nodes, 2-stage, 241 frames)."""
import json, sys

def build(ref_image="qiyan_ref.jpg", prompt="", seed1=23, seed2=42):
    wf = {}

    wf["269"] = {"class_type": "LoadImage", "inputs": {"image": ref_image}}
    wf["273"] = {"class_type": "SaveVideo", "inputs": {"filename_prefix": "video/LTX_2.3_i2v", "format": "auto", "codec": "auto", "video": ["312", 0]}}
    wf["274"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": seed2}}
    wf["275"] = {"class_type": "RandomNoise", "inputs": {"noise_seed": seed1}}
    wf["277"] = {"class_type": "LTXVAudioVAELoader", "inputs": {"ckpt_name": "ltx-2.3-22b-dev-fp8.safetensors"}}
    wf["279"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler_cfg_pp"}}
    wf["280"] = {"class_type": "ManualSigmas", "inputs": {"sigmas": "0.85, 0.7250, 0.4219, 0.0"}}
    wf["281"] = {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "ltx-2.3-22b-dev-fp8.safetensors"}}
    wf["282"] = {"class_type": "CFGGuider", "inputs": {"cfg": 1, "model": ["320", 0], "positive": ["284", 0], "negative": ["284", 1]}}
    wf["283"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["275", 0], "guider": ["316", 0], "sampler": ["291", 0], "sigmas": ["308", 0], "latent_image": ["306", 0]}}
    wf["284"] = {"class_type": "LTXVCropGuides", "inputs": {"positive": ["305", 0], "negative": ["305", 1], "latent": ["309", 0]}}
    wf["285"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "LTX2\\ltx-2.3-22b-distilled-lora-dynamic_fro09_avg_rank_105_bf16.safetensors", "strength_model": 0.5, "model": ["281", 0]}}
    wf["286"] = {"class_type": "ResizeImagesByLongerEdge", "inputs": {"longer_edge": 1536, "images": ["290", 0]}}
    wf["287"] = {"class_type": "LTXVLatentUpsampler", "inputs": {"samples": ["309", 0], "upscale_model": ["313", 0], "vae": ["281", 2]}}
    wf["288"] = {"class_type": "LTXVImgToVideoInplace", "inputs": {"strength": 1, "bypass": ["302", 0], "vae": ["281", 2], "image": ["289", 0], "latent": ["287", 0]}}
    wf["289"] = {"class_type": "LTXVPreprocess", "inputs": {"img_compression": 18, "image": ["286", 0]}}
    wf["290"] = {"class_type": "ResizeImageMaskNode", "inputs": {"input": ["269", 0], "resize_type": "scale dimensions", "scale_method": "lanczos", "resize_type.crop": "center", "resize_type.width": ["314", 0], "resize_type.height": ["299", 0]}}
    wf["291"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler_ancestral_cfg_pp"}}
    wf["292"] = {"class_type": "ComfyMathExpression", "inputs": {"expression": "a/2", "values.a": ["314", 0]}}
    wf["294"] = {"class_type": "ComfyMathExpression", "inputs": {"expression": "a/2", "values.a": ["299", 0]}}
    wf["295"] = {"class_type": "EmptyLTXVLatentVideo", "inputs": {"batch_size": 1, "width": ["292", 1], "height": ["294", 1], "length": ["301", 0]}}
    wf["296"] = {"class_type": "LTXVImgToVideoInplace", "inputs": {"strength": 0.7, "bypass": ["302", 0], "vae": ["281", 2], "image": ["289", 0], "latent": ["295", 0]}}
    wf["298"] = {"class_type": "ComfyMathExpression", "inputs": {"expression": "a", "values.a": ["300", 0]}}
    wf["299"] = {"class_type": "PrimitiveInt", "inputs": {"value": 1280}}
    wf["300"] = {"class_type": "PrimitiveInt", "inputs": {"value": 24}}
    wf["301"] = {"class_type": "PrimitiveInt", "inputs": {"value": 241}}
    wf["302"] = {"class_type": "PrimitiveBoolean", "inputs": {"value": False}}
    wf["303"] = {"class_type": "PrimitiveStringMultiline", "inputs": {"value": prompt}}

    # CLIPTextEncode needs the string from 303 or direct text
    if prompt:
        wf["304"] = {"class_type": "CLIPTextEncode", "inputs": {"text": ["303", 0], "clip": ["318", 0]}}
    else:
        wf["304"] = {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["318", 0]}}

    wf["305"] = {"class_type": "LTXVConditioning", "inputs": {"frame_rate": ["298", 0], "positive": ["304", 0], "negative": ["315", 0]}}
    wf["306"] = {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": ["296", 0], "audio_latent": ["307", 0]}}
    wf["307"] = {"class_type": "LTXVEmptyLatentAudio", "inputs": {"batch_size": 1, "frames_number": ["301", 0], "frame_rate": ["298", 1], "audio_vae": ["277", 0]}}
    wf["308"] = {"class_type": "ManualSigmas", "inputs": {"sigmas": "1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"}}
    wf["309"] = {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["283", 0]}}
    wf["310"] = {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["274", 0], "guider": ["282", 0], "sampler": ["279", 0], "sigmas": ["280", 0], "latent_image": ["276", 0]}}
    wf["276"] = {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": ["288", 0], "audio_latent": ["309", 1]}}
    wf["311"] = {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["310", 0]}}
    wf["312"] = {"class_type": "CreateVideo", "inputs": {"bit_depth": 8, "fps": ["298", 0], "images": ["317", 0], "audio": ["297", 0]}}
    wf["313"] = {"class_type": "LatentUpscaleModelLoader", "inputs": {"model_name": "ltx-2.3-spatial-upscaler-x2-1.0.safetensors"}}
    wf["314"] = {"class_type": "PrimitiveInt", "inputs": {"value": 960}}
    wf["315"] = {"class_type": "CLIPTextEncode", "inputs": {"text": "blurry, low quality, still frame, watermark, overlay, deformed, bad anatomy, ugly, cartoon", "clip": ["318", 0]}}
    wf["316"] = {"class_type": "CFGGuider", "inputs": {"cfg": 1, "model": ["320", 0], "positive": ["305", 0], "negative": ["305", 1]}}
    wf["317"] = {"class_type": "VAEDecodeTiled", "inputs": {"tile_size": 768, "overlap": 64, "temporal_size": 4096, "temporal_overlap": 4, "samples": ["311", 0], "vae": ["281", 2]}}
    wf["318"] = {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "gemma_3_12B_it_fp8_scaled.safetensors", "clip_name2": "ltx-2.3_text_projection_bf16.safetensors", "type": "ltxv", "device": "default"}}
    wf["320"] = {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "LTX2\\LTX2.3-MysticXXX.safetensors", "strength_model": 1, "model": ["285", 0]}}
    wf["297"] = {"class_type": "LTXVAudioVAEDecode", "inputs": {"samples": ["311", 1], "audio_vae": ["277", 0]}}

    return {"prompt": wf}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate exact LTX 2.3 i2v workflow")
    parser.add_argument("--image", default="qiyan_ref.jpg", help="Reference image filename")
    parser.add_argument("--prompt", default="", help="Positive prompt text")
    parser.add_argument("--seed1", type=int, default=23, help="Stage 1 noise seed")
    parser.add_argument("--seed2", type=int, default=42, help="Stage 2 noise seed")
    parser.add_argument("-o", "--output", default="/tmp/ltx_submit.json", help="Output path")
    args = parser.parse_args()

    wf = build(args.image, args.prompt, args.seed1, args.seed2)
    with open(args.output, "w") as f:
        json.dump(wf, f, ensure_ascii=False, indent=2)
    print(f"Written to {args.output}")
