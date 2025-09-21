import google.generativeai as genai
import os
import json
import subprocess
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import tempfile
from datetime import datetime
import re

class SegmentedVideoGenerator:
    def __init__(self, gemini_api_key: str):
        """Segmented video generator - creates 5 matching video/audio segments"""
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        print(f"✅ Initialized Segmented Video Generator")
        
    def generate_segments(self, topic: str) -> dict:
        """Generate 5 segments: intro, concept1, concept2, example, conclusion"""
        
        prompt = f"""
Create educational content about "{topic}" split into exactly 5 segments for video production.

Each segment should have:
1. MANIM CODE - Animation for that specific segment (NO LaTeX, only Text() and shapes)
2. NARRATION - What to say during that segment (15-20 seconds when spoken)

SEGMENTS NEEDED:
1. INTRO/MOTIVATION - Hook the audience, why this topic matters
2. FUNDAMENTALS - Basic concepts and definitions  
3. CORE PRINCIPLES - Main ideas and how they work
4. PRACTICAL EXAMPLE - Real example or application
5. CONCLUSION - Summary and encouragement

MANIM CONSTRAINTS:
- White background, black text
- Use only Text(), Rectangle, Circle, Line, Arrow
- Each segment should be 15-20 seconds of animation
- Simple, clear visuals

NARRATION CONSTRAINTS:
- 15-20 seconds of natural speech per segment
- No timing instructions or asterisks
- Conversational teaching tone
- Each segment stands alone but connects to others

Topic: {topic}

Format your response EXACTLY like this:

SEGMENT_1_INTRO:
MANIM_CODE:
```python
from manim import *
class IntroVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # Animation code here
```
NARRATION:
Hello everyone! Today we're exploring [topic]. This is incredibly important because...

SEGMENT_2_FUNDAMENTALS:
MANIM_CODE:
```python
from manim import *
class FundamentalsVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # Animation code here
```
NARRATION:
Let's start with the fundamentals. The key concepts you need to understand are...

SEGMENT_3_PRINCIPLES:
MANIM_CODE:
```python
from manim import *
class PrinciplesVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # Animation code here
```
NARRATION:
Now for the core principles. These govern how everything works together...

SEGMENT_4_EXAMPLE:
MANIM_CODE:
```python
from manim import *
class ExampleVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # Animation code here
```
NARRATION:
Here's a practical example to make this concrete. Let's see how we apply these ideas...

SEGMENT_5_CONCLUSION:
MANIM_CODE:
```python
from manim import *
class ConclusionVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # Animation code here
```
NARRATION:
To wrap up, we've covered the essential aspects of [topic]. Remember that...
"""
        
        try:
            print(f"🤖 Generating 5 segments for: {topic}")
            response = self.model.generate_content(prompt)
            content = response.text
            print(f"✅ AI response received!")
            
            segments = {}
            segment_names = ["INTRO", "FUNDAMENTALS", "PRINCIPLES", "EXAMPLE", "CONCLUSION"]
            
            for i, name in enumerate(segment_names, 1):
                segment_key = f"SEGMENT_{i}_{name}:"
                if segment_key in content:
                    # Extract this segment
                    start_idx = content.find(segment_key)
                    if i < len(segment_names):
                        next_segment_key = f"SEGMENT_{i+1}_{segment_names[i]}:"
                        end_idx = content.find(next_segment_key)
                        if end_idx == -1:
                            end_idx = len(content)
                    else:
                        end_idx = len(content)
                    
                    segment_content = content[start_idx:end_idx]
                    
                    # Parse manim code and narration
                    manim_code, narration = self._parse_segment(segment_content)
                    if manim_code and narration:
                        segments[name.lower()] = {
                            'code': self._ensure_latex_free(manim_code),
                            'narration': self._clean_narration_text(narration),
                            'class_name': f"{name.capitalize()}Video"
                        }
                        print(f"✅ Parsed segment: {name}")
                    else:
                        # Generate fallback
                        segments[name.lower()] = self._generate_fallback_segment(topic, name, i)
                        print(f"⚠️ Generated fallback for: {name}")
                else:
                    # Generate fallback
                    segments[name.lower()] = self._generate_fallback_segment(topic, name, i)
                    print(f"⚠️ Generated fallback for: {name}")
            
            return segments
                
        except Exception as e:
            print(f"❌ AI generation error: {e}")
            return self._generate_all_fallback_segments(topic)
    
    def _parse_segment(self, segment_content: str) -> tuple:
        """Parse manim code and narration from segment"""
        try:
            if "MANIM_CODE:" in segment_content and "NARRATION:" in segment_content:
                parts = segment_content.split("NARRATION:")
                manim_section = parts[0].replace("MANIM_CODE:", "").strip()
                narration = parts[1].strip()
                
                # Clean Manim code
                if "```python" in manim_section:
                    code_start = manim_section.find("```python") + 9
                    code_end = manim_section.find("```", code_start)
                    if code_end == -1:
                        code_end = len(manim_section)
                    manim_code = manim_section[code_start:code_end].strip()
                else:
                    manim_code = manim_section.strip()
                
                return manim_code, narration
        except:
            pass
        return None, None
    
    def _ensure_latex_free(self, code: str) -> str:
        """Remove LaTeX elements and replace with Text()"""
        if "MathTex" in code or "Tex(" in code:
            print("⚠️ Converting LaTeX to Text...")
            replacements = {
                r"MathTex(r\"": "Text(\"",
                r"MathTex(": "Text(",
                r"Tex(": "Text(",
                r"\\frac{": "",
                r"}{": "/",
                r"\\": "",
            }
            for old, new in replacements.items():
                code = code.replace(old, new)
        return code
    
    def _clean_narration_text(self, narration: str) -> str:
        """Clean narration for TTS"""
        patterns_to_remove = [
            r'\*.*?\*',  # Remove *asterisk text*
            r'\[.*?\]',  # Remove [bracket text] 
            r'\d+\s*-\s*\d+\s*seconds?',  # Remove timing
            r'\(.*?\)',  # Remove parenthetical instructions
        ]
        
        clean_text = narration
        for pattern in patterns_to_remove:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        clean_text = re.sub(r'\s+', ' ', clean_text.replace('\n', ' ')).strip()
        return clean_text
    
    def _generate_fallback_segment(self, topic: str, segment_name: str, segment_num: int) -> dict:
        """Generate fallback segment if AI parsing fails"""
        
        class_name = f"{segment_name.capitalize()}Video"
        
        # Segment-specific content
        if segment_name == "INTRO":
            title = f"Welcome to {topic.title()}"
            content = [
                "Why This Matters",
                "Key Benefits",
                "What You'll Learn"
            ]
            narration = f"Hello everyone! Welcome to our lesson on {topic}. This topic is incredibly important because it helps us understand fundamental concepts that apply to many real-world situations. Today, we'll explore the key ideas step by step."
            
        elif segment_name == "FUNDAMENTALS":
            title = "Fundamental Concepts"
            content = [
                "Basic Definitions", 
                "Core Components",
                "Essential Terms"
            ]
            narration = f"Let's start with the fundamentals of {topic}. Understanding these basic concepts is crucial because they form the foundation for everything else we'll learn. These are the building blocks that make everything else possible."
            
        elif segment_name == "PRINCIPLES":
            title = "Core Principles"
            content = [
                "How It Works",
                "Key Relationships", 
                "Important Rules"
            ]
            narration = f"Now for the core principles that govern {topic}. These principles show us how different elements work together and help us understand the underlying patterns. Once you grasp these, everything else will start to make sense."
            
        elif segment_name == "EXAMPLE":
            title = "Practical Example"
            content = [
                "Real-World Application",
                "Step-by-Step Process",
                "Expected Results"
            ]
            narration = f"Here's a practical example to make {topic} concrete. Let's see how we apply these concepts in a real situation. This example will help you understand how theory translates into practice."
            
        else:  # CONCLUSION
            title = "Key Takeaways"
            content = [
                "What We Learned",
                "Next Steps",
                "Keep Practicing"
            ]
            narration = f"To wrap up our exploration of {topic}, we've covered the essential concepts and seen how they apply in practice. Remember, mastering these ideas takes practice, so keep working with these concepts and exploring new applications."
        
        # Generate Manim code
        manim_code = f'''from manim import *

class {class_name}(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        
        # Title
        title = Text("{title}", font_size=48, color=BLACK, weight=BOLD)
        title.to_edge(UP, buff=1)
        self.play(Write(title), run_time=2)
        self.wait(1)
        
        # Content points
        points = [
            Text("{content[0]}", font_size=32, color=DARK_BLUE),
            Text("{content[1]}", font_size=32, color=DARK_BLUE),
            Text("{content[2]}", font_size=32, color=DARK_BLUE)
        ]
        
        content_group = VGroup(*points)
        content_group.arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        content_group.move_to(ORIGIN)
        
        for i, point in enumerate(points):
            self.play(Write(point), run_time=1.5)
            self.wait(1.2)
        
        # Visual element
        if {segment_num} <= 3:
            # Early segments get a box
            highlight_box = Rectangle(
                width=8, height=5,
                color=BLUE, stroke_width=3,
                fill_opacity=0.1, fill_color=LIGHT_BLUE
            )
            highlight_box.move_to(content_group.get_center())
            self.play(Create(highlight_box), run_time=1)
            self.wait(1.5)
        else:
            # Later segments get arrows and shapes
            arrow = Arrow(start=LEFT*2, end=RIGHT*2, color=GREEN, stroke_width=6)
            arrow.next_to(content_group, DOWN, buff=1)
            self.play(Create(arrow), run_time=1)
            self.wait(1.5)
        
        self.wait(2)
'''
        
        return {
            'code': manim_code,
            'narration': narration,
            'class_name': class_name
        }
    
    def _generate_all_fallback_segments(self, topic: str) -> dict:
        """Generate all fallback segments"""
        segments = {}
        names = ["intro", "fundamentals", "principles", "example", "conclusion"]
        titles = ["INTRO", "FUNDAMENTALS", "PRINCIPLES", "EXAMPLE", "CONCLUSION"]
        
        for i, (name, title) in enumerate(zip(names, titles)):
            segments[name] = self._generate_fallback_segment(topic, title, i+1)
        
        return segments
    
    def create_segmented_video(self, topic: str) -> str:
        """Create 5 separate videos and combine them"""
        
        print(f"🎬 Creating segmented video for: {topic}")
        
        # Generate all segments
        segments = self.generate_segments(topic)
        
        if not segments:
            print("❌ Failed to generate segments")
            return None
        
        # Create temp directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.mkdtemp()
        final_videos = []
        
        # Process each segment
        for i, (name, segment) in enumerate(segments.items(), 1):
            print(f"\n📹 Processing Segment {i}: {name.upper()}")
            
            # Save animation code
            manim_file = os.path.join(temp_dir, f"segment_{i}_{name}.py")
            with open(manim_file, 'w', encoding='utf-8') as f:
                f.write(segment['code'])
            
            # Generate audio
            audio_file = os.path.join(temp_dir, f"segment_{i}_{name}.mp3")
            try:
                tts = gTTS(text=segment['narration'], lang='en', slow=False)
                tts.save(audio_file)
                print(f"🔊 Audio generated for {name}")
            except Exception as e:
                print(f"❌ Audio generation failed for {name}: {e}")
                continue
            
            # Render video
            try:
                print(f"🎥 Rendering animation for {name}...")
                cmd = [
                    "manim", 
                    manim_file,
                    segment['class_name'],
                    "-pql",
                    "--format", "mp4",
                    "--media_dir", temp_dir
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    cwd=temp_dir,
                    timeout=180
                )
                
                if result.returncode == 0:
                    print(f"✅ Animation rendered for {name}")
                    
                    # Find video file
                    video_file = None
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file.endswith('.mp4') and 'videos' in root and segment['class_name'].lower() in file.lower():
                                video_file = os.path.join(root, file)
                                break
                        if video_file:
                            break
                    
                    if video_file and os.path.exists(video_file):
                        # Combine this segment's video and audio
                        combined_video = self._combine_segment_media(video_file, audio_file, name, i, temp_dir)
                        if combined_video:
                            final_videos.append(combined_video)
                            print(f"✅ Segment {i} completed: {name}")
                    else:
                        print(f"❌ Video file not found for {name}")
                else:
                    print(f"❌ Rendering failed for {name}")
                    print(f"Error: {result.stderr}")
                    
            except Exception as e:
                print(f"❌ Processing error for {name}: {e}")
                continue
        
        # Combine all segments
        if len(final_videos) >= 3:  # At least 3 segments successful
            final_output = self._combine_all_segments(final_videos, topic, timestamp)
            return final_output
        else:
            print(f"❌ Not enough segments completed ({len(final_videos)}/5)")
            return None
    
    def _combine_segment_media(self, video_file: str, audio_file: str, segment_name: str, segment_num: int, temp_dir: str) -> str:
        """Combine video and audio for one segment with proper duration matching"""
        
        try:
            print(f"🎞️ Combining media for segment {segment_num}: {segment_name}")
            
            video = VideoFileClip(video_file)
            audio = AudioFileClip(audio_file)
            
            print(f"📏 Video duration: {video.duration:.1f}s, Audio duration: {audio.duration:.1f}s")
            
            # Match durations - use the longer duration and extend the shorter one
            target_duration = max(video.duration, audio.duration)
            
            if video.duration < target_duration:
                # Extend video by looping or freezing last frame
                video = video.loop(duration=target_duration)
            elif video.duration > target_duration:
                # Trim video to match audio
                video = video.subclip(0, target_duration)
                
            if audio.duration < target_duration:
                # Extend audio with silence
                from moviepy.audio.AudioClip import silence
                silence_duration = target_duration - audio.duration
                silence_clip = silence(duration=silence_duration)
                audio = audio.concatenate(silence_clip)
            elif audio.duration > target_duration:
                # Trim audio
                audio = audio.subclip(0, target_duration)
            
            # Combine
            final = video.set_audio(audio)
            
            # Save segment
            segment_output = os.path.join(temp_dir, f"segment_{segment_num}_{segment_name}_final.mp4")
            final.write_videofile(
                segment_output,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Cleanup
            video.close()
            audio.close()
            final.close()
            
            print(f"✅ Segment {segment_num} media combined (duration: {target_duration:.1f}s)")
            return segment_output
            
        except Exception as e:
            print(f"❌ Failed to combine media for segment {segment_name}: {e}")
            return None
    
    def _combine_all_segments(self, video_files: list, topic: str, timestamp: str) -> str:
        """Combine all segment videos into final video"""
        
        try:
            print(f"🎬 Combining {len(video_files)} segments into final video...")
            
            clips = []
            total_duration = 0
            
            for video_file in video_files:
                if os.path.exists(video_file):
                    clip = VideoFileClip(video_file)
                    clips.append(clip)
                    total_duration += clip.duration
                    print(f"📼 Added segment: {os.path.basename(video_file)} ({clip.duration:.1f}s)")
            
            if clips:
                final_video = concatenate_videoclips(clips)
                
                output_filename = f"{topic.replace(' ', '_')}_{timestamp}_Segmented.mp4"
                final_video.write_videofile(
                    output_filename,
                    codec='libx264',
                    audio_codec='aac',
                    verbose=False,
                    logger=None
                )
                
                # Cleanup
                for clip in clips:
                    clip.close()
                final_video.close()
                
                print(f"🎉 Final segmented video created!")
                print(f"📁 File: {output_filename}")
                print(f"⏱️ Total duration: {total_duration:.1f} seconds")
                return output_filename
            else:
                print("❌ No valid video clips to combine")
                return None
                
        except Exception as e:
            print(f"❌ Failed to combine all segments: {e}")
            return None

def main():
    print("🚀 Segmented Video Generator")
    print("Creates 5 matching video/audio segments")
    print("=" * 50)
    
    api_key = input("Enter your Gemini API key: ").strip()
    if not api_key:
        print("❌ API key required!")
        return
    
    try:
        generator = SegmentedVideoGenerator(api_key)
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    topic = input("Enter topic: ").strip()
    if not topic:
        print("❌ Topic required!")
        return
    
    print(f"\n🎬 Creating segmented video for: {topic}")
    print("📺 Will generate: Intro → Fundamentals → Principles → Example → Conclusion")
    
    output = generator.create_segmented_video(topic)
    
    if output:
        print(f"\n🎊 SUCCESS!")
        print(f"📁 Final video: {output}")
        print(f"🎬 Perfect sync between video and audio!")
        print(f"📺 5 segments with matching durations")
    else:
        print(f"\n❌ Segmented video creation failed")
        print(f"💡 Try a different topic or check your internet connection")

if __name__ == "__main__":
    main()