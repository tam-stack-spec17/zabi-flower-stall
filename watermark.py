import os
import shutil
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip

def create_watermark_layer(width, height, text):
    txt_layer = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    font_size = max(int(width / 30), 20) 
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # DARK BLACK text with semi-transparency (0, 0, 0 is black, 200 is opacity)
    text_color = (0, 0, 0, 200) 
    
    bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (width - text_w) // 2
    y = (height - text_h) // 2
    
    draw.multiline_text((x, y), text, fill=text_color, font=font, align="center")
    return txt_layer

def process_collection_in_place(folder, watermark_text):
    if not os.path.exists(folder):
        return
        
    files = os.listdir(folder)
    img_exts = ('.jpeg', '.jpg', '.png', '.webp')
    vid_exts = ('.mp4', '.mov')
    
    images = [f for f in files if f.lower().endswith(img_exts)]
    videos = [f for f in files if f.lower().endswith(vid_exts)]
    
    if not images and not videos:
        return
        
    print(f"\n============================================")
    print(f"  PROCESSING: {folder.upper()} COLLECTION")
    print(f"============================================")
    
    temp_dir = f"temp_workspace_{folder}"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    for index, filename in enumerate(images, start=1):
        img_path = os.path.join(folder, filename)
        try:
            img = Image.open(img_path).convert("RGBA")
            txt_layer = create_watermark_layer(img.width, img.height, watermark_text)
            watermarked_img = Image.alpha_composite(img, txt_layer).convert("RGB")
            
            new_name = f"img-{index}.jpeg"
            watermarked_img.save(os.path.join(temp_dir, new_name), "JPEG", quality=90)
            print(f"✅ Image ready: {new_name}")
        except Exception as e:
            print(f"❌ Could not process image {filename}: {e}")

    for index, filename in enumerate(videos, start=1):
        vid_path = os.path.join(folder, filename)
        print(f"⏳ Processing Video {index} in {folder.upper()}...")
        try:
            video = VideoFileClip(vid_path)
            temp_wm_path = f"temp_wm_{folder}_{index}.png"
            
            txt_layer = create_watermark_layer(video.size[0], video.size[1], watermark_text)
            txt_layer.save(temp_wm_path)
            
            wm_clip = ImageClip(temp_wm_path).with_duration(video.duration)
            final_video = CompositeVideoClip([video, wm_clip])
            
            new_name = f"vid-{index}.mp4"
            final_video.write_videofile(os.path.join(temp_dir, new_name), codec="libx264", audio_codec="aac")
            
            # 🔥 FIX: Force close all clips to unlock files on Windows
            final_video.close()
            wm_clip.close()
            video.close()
            
            if os.path.exists(temp_wm_path):
                os.remove(temp_wm_path)
            print(f"✅ Video ready: {new_name}")
        except Exception as e:
            print(f"❌ Could not process video {filename}: {e}")

    print(f"🧹 Cleaning up old unwatermarked files in {folder}...")
    for f in files:
        file_to_delete = os.path.join(folder, f)
        if os.path.isfile(file_to_delete):
            os.remove(file_to_delete)
        
    print(f"📦 Moving perfectly named watermarked files into {folder}...")
    temp_files = os.listdir(temp_dir)
    for f in temp_files:
        shutil.move(os.path.join(temp_dir, f), os.path.join(folder, f))
        
    # 🔥 FIX: Force delete the temp folder, ignoring Windows locks
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"✨ {folder.upper()} collection is fully updated!")

# --- THE MASTER SETTINGS ---
# Bridal is removed so we pick up right where it left off!
COLLECTIONS = ["groom", "bed", "car", "kids"]

TEXT = "Zabi Flower Stall\n📞 +91 93434 58734 | +91 99458 22792"

for category in COLLECTIONS:
    process_collection_in_place(category, TEXT)
    
print("\n🎉 ALL COLLECTIONS PROCESSED SUCCESSFULLY! Ready to push to GitHub.")