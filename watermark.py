import os
from PIL import Image, ImageDraw, ImageFont

# 1. FIXED IMPORT FOR MOVIEPY V2.0+
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip

def create_watermark_layer(width, height, text):
    """Generates a transparent layer with the custom text."""
    txt_layer = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    # Make the font size responsive to the media size
    font_size = max(int(width / 35), 20) 
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # White text with 75% opacity
    text_color = (255, 255, 255, 190) 
    
    # Calculate position (Bottom Right Corner)
    bbox = draw.multiline_textbbox((0, 0), text, font=font, align="right")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = width - text_w - 30
    y = height - text_h - 30
    
    # Draw the multiline text
    draw.multiline_text((x, y), text, fill=text_color, font=font, align="right")
    return txt_layer

def process_media(input_folder, output_folder, watermark_text):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Grab all files in the raw folder
    files = os.listdir(input_folder)
    img_exts = ('.jpeg', '.jpg', '.png', '.webp')
    vid_exts = ('.mp4', '.mov')
    
    images = [f for f in files if f.lower().endswith(img_exts)]
    videos = [f for f in files if f.lower().endswith(vid_exts)]
    
    print(f"Found {len(images)} images and {len(videos)} videos. Beginning processing...\n")

    # PROCESS IMAGES
    for index, filename in enumerate(images, start=1):
        img_path = os.path.join(input_folder, filename)
        img = Image.open(img_path).convert("RGBA")
        
        txt_layer = create_watermark_layer(img.width, img.height, watermark_text)
        watermarked_img = Image.alpha_composite(img, txt_layer).convert("RGB")
        
        new_name = f"img-{index}.jpeg"
        watermarked_img.save(os.path.join(output_folder, new_name), "JPEG", quality=90)
        print(f"✅ Saved Image: {new_name}")

    # PROCESS VIDEOS
    for index, filename in enumerate(videos, start=1):
        vid_path = os.path.join(input_folder, filename)
        print(f"\n⏳ Processing Video {index}... (This may take a few minutes)")
        
        video = VideoFileClip(vid_path)
        
        temp_wm_path = f"temp_wm_{index}.png"
        
        # Using video.size[0] and [1] for v2 compatibility
        txt_layer = create_watermark_layer(video.size[0], video.size[1], watermark_text)
        txt_layer.save(temp_wm_path)
        
        # 2. FIXED DURATION COMMAND FOR MOVIEPY V2.0+ (with_duration instead of set_duration)
        wm_clip = ImageClip(temp_wm_path).with_duration(video.duration)
        final_video = CompositeVideoClip([video, wm_clip])
        
        new_name = f"vid-{index}.mp4"
        final_video.write_videofile(os.path.join(output_folder, new_name), codec="libx264", audio_codec="aac")
        
        video.close()
        if os.path.exists(temp_wm_path):
            os.remove(temp_wm_path)
        print(f"✅ Saved Video: {new_name}")

# --- WORKFLOW SETTINGS ---
INPUT_DIR = "raw_media" 
OUTPUT_DIR = "bridal"    

TEXT = "Zabi Flower Stall\n📞 +91 93434 58734 | +91 99458 22792"

process_media(INPUT_DIR, OUTPUT_DIR, TEXT)