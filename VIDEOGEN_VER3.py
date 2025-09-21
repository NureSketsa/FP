import google.generativeai as genai
import os
import json
import subprocess
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import tempfile
from datetime import datetime
import re

class ThreeBlueBrownStyleGenerator:
    def __init__(self, gemini_api_key: str):
        """3Blue1Brown style video generator with beautiful animations"""
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Initialized 3Blue1Brown Style Generator")
        
    def generate_segments(self, topic: str) -> dict:
        """Generate 5 segments with 3Blue1Brown style animations"""
        
        prompt = f"""
Create educational content about "{topic}" in 3Blue1Brown style with elegant mathematical animations.

Each segment should have:
1. MANIM CODE - Beautiful, smooth animations with 3Blue1Brown aesthetics
2. NARRATION - Engaging explanation (15-20 seconds when spoken)

3BLUE1BROWN STYLE REQUIREMENTS:
- Dark blue/navy background (#0f1419 or similar)
- Elegant colors: BLUE, YELLOW, GREEN, RED, WHITE, ORANGE
- Smooth transforms and morphing
- Mathematical elegance even for non-math topics
- Use VGroup for complex animations
- Emphasis on visual storytelling
- Beautiful typography and spacing
- Zoom effects and camera movements
- Gradient fills and glowing effects

SEGMENTS:
1. INTRO - Hook with beautiful title sequence and motivation
2. FUNDAMENTALS - Core concepts with elegant visual metaphors  
3. PRINCIPLES - Deep dive with smooth transformations
4. EXAMPLE - Concrete application with step-by-step visual flow
5. CONCLUSION - Satisfying wrap-up with all elements coming together

ANIMATION STYLE:
- Use Transform, ReplacementTransform, FadeIn, FadeOut, Write
- Smooth camera movements with self.camera.frame
- Beautiful color transitions
- Mathematical precision in positioning
- Elegant grouping and arrangement of elements
- Visual metaphors and analogies

Topic: {topic}

Format your response EXACTLY like this:

SEGMENT_1_INTRO:
MANIM_CODE:
```python
from manim import *
class IntroVideo(Scene):
    def construct(self):
        self.camera.background_color = "#0f1419"  # 3B1B dark blue
        # Beautiful intro animation
```
NARRATION:
Welcome to an exploration of [topic]. What makes this fascinating is...

SEGMENT_2_FUNDAMENTALS:
MANIM_CODE:
```python
from manim import *
class FundamentalsVideo(Scene):
    def construct(self):
        self.camera.background_color = "#0f1419"
        # Elegant fundamentals visualization
```
NARRATION:
The foundation of [topic] rests on these key ideas...

[Continue for all 5 segments...]
"""
        
        try:
            print(f"🎨 Generating 3Blue1Brown style content for: {topic}")
            response = self.model.generate_content(prompt)
            content = response.text
            print("✅ AI response received!")
            
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
                        enhanced_code = self._enhance_3b1b_style(manim_code, name)
                        if enhanced_code is not None:  # Code passed safety checks
                            segments[name.lower()] = {
                                'code': enhanced_code,
                                'narration': self._clean_narration_text(narration),
                                'class_name': f"{name.capitalize()}Video"
                            }
                            print(f"🎨 Parsed 3B1B segment: {name}")
                        else:  # Code failed safety checks, use fallback
                            segments[name.lower()] = self._generate_3b1b_fallback(topic, name, i)
                            print(f"🎨 Generated 3B1B fallback for: {name} (unsafe AI code)")
                    else:
                        # Generate 3B1B fallback
                        segments[name.lower()] = self._generate_3b1b_fallback(topic, name, i)
                        print(f"🎨 Generated 3B1B fallback for: {name}")
                else:
                    # Generate 3B1B fallback
                    segments[name.lower()] = self._generate_3b1b_fallback(topic, name, i)
                    print(f"🎨 Generated 3B1B fallback for: {name}")
            
            return segments
                
        except Exception as e:
            print(f"❌ AI generation error: {e}")
            return self._generate_all_3b1b_fallbacks(topic)
    
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
        except Exception:
            pass
        return None, None
    
    def _enhance_3b1b_style(self, code: str, segment_name: str) -> str:
        """Remove all problematic Manim features and force use of simple fallback"""
        
        # If AI-generated code contains any problematic patterns, 
        # completely discard it and use our reliable fallback
        problematic_patterns = [
            'Tex(', 'MathTex(', 'MathText(',
            'self.camera.frame', 'add_coordinate_labels',
            'Axes(', 'Surface(', 'NumberLine(',
            'DecimalNumber(', 'always_redraw(',
            'LaggedStart(', 'RoundedRectangle('
        ]
        
        # Check if code contains any problematic patterns
        for pattern in problematic_patterns:
            if pattern in code:
                print(f"🚫 Detected problematic pattern '{pattern}' - using safe fallback")
                # Return None to force fallback usage
                return None
        
        # If code passes the check, apply basic cleaning
        latex_replacements = [
            ('Tex(', 'Text('),
            ('MathTex(', 'Text('),
            ('MathText(', 'Text('),
            ('font="CMU Serif"', ''),
            ('weight=BOLD', ''),
            (', weight=BOLD', ''),
            ('font="CMU Serif", ', ''),
            ('rate_func=smooth', ''),
            (', rate_func=smooth', ''),
        ]
        
        enhanced_code = code
        for old, new in latex_replacements:
            enhanced_code = enhanced_code.replace(old, new)
        
        return enhanced_code
    
    def _clean_narration_text(self, narration: str) -> str:
        """Clean narration for TTS"""
        patterns_to_remove = [
            r'\*.*?\*',
            r'\[.*?\]',
            r'\d+\s*-\s*\d+\s*seconds?',
            r'\(.*?\)',
        ]
        
        clean_text = narration
        for pattern in patterns_to_remove:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        clean_text = re.sub(r'\s+', ' ', clean_text.replace('\n', ' ')).strip()
        return clean_text
    
    def _generate_3b1b_fallback(self, topic: str, segment_name: str, segment_num: int) -> dict:
        """Generate simple, reliable 3Blue1Brown style fallback segment"""
        
        class_name = f"{segment_name.capitalize()}Video"
        
        # 3B1B Color palette
        colors = {
            "bg": "#0f1419",
            "primary": "#58C4DD",
            "accent": "#FFFF00", 
            "success": "#C9E4CA",
            "danger": "#FC6255",
            "warning": "#FF8C42",
            "info": "#BC7FCD"
        }
        
        if segment_name == "INTRO":
            title_text = f"{topic.title()}"
            subtitle = "A Beautiful Mathematical Journey"
            narration = f"Welcome to an elegant exploration of {topic}. What makes this topic truly fascinating is how it reveals the hidden mathematical beauty in everyday concepts. Let's dive into this journey of discovery together."
            
            main_color = colors["primary"]
            accent_color = colors["accent"]
            
        elif segment_name == "FUNDAMENTALS":
            title_text = "The Foundation"
            subtitle = "Building Blocks of Understanding"
            narration = f"The foundation of {topic} rests on these fundamental principles. Like building an elegant mathematical structure, we need to understand each component and how they interconnect to form something beautiful and meaningful."
            
            main_color = colors["success"]
            accent_color = colors["primary"]
            
        elif segment_name == "PRINCIPLES":
            title_text = "Core Principles"
            subtitle = "The Heart of the Matter"
            narration = f"Now we reach the heart of {topic}, where the core principles reveal themselves. These aren't just abstract rules, but elegant patterns that govern how everything works together in perfect harmony."
            
            main_color = colors["warning"]
            accent_color = colors["info"]
            
        elif segment_name == "EXAMPLE":
            title_text = "Seeing It In Action"
            subtitle = "From Theory to Reality"
            narration = f"Here's where {topic} comes alive through a concrete example. Watch how the abstract principles we've learned transform into something tangible and practical, like magic unfolding before our eyes."
            
            main_color = colors["info"]
            accent_color = colors["danger"]
            
        else:  # CONCLUSION
            title_text = "The Beautiful Truth"
            subtitle = "Bringing It All Together"
            narration = f"As we conclude our exploration of {topic}, notice how all the pieces fit together like a perfect puzzle. This is the beauty of mathematics and logical thinking - everything has its place and purpose."
            
            main_color = colors["danger"]
            accent_color = colors["success"]
        
        # Generate simple, reliable 3B1B style Manim code (no LaTeX, no advanced features)
        manim_code = f'''from manim import *
import numpy as np

class {class_name}(Scene):
    def construct(self):
        # 3Blue1Brown signature dark background
        self.camera.background_color = "{colors['bg']}"
        
        # Beautiful title sequence
        title = Text(
            "{title_text}",
            font_size=56,
            color="{main_color}"
        )
        
        subtitle = Text(
            "{subtitle}",
            font_size=32,
            color="{accent_color}"
        ).next_to(title, DOWN, buff=0.5)
        
        # Elegant entrance animation
        self.play(
            Write(title, run_time=2),
            FadeIn(subtitle, run_time=1.5)
        )
        self.wait(1)
        
        # Create visual elements with 3B1B style
        if {segment_num} == 1:  # INTRO
            # Animated dots forming a pattern
            dots = VGroup()
            for i in range(12):
                dot = Dot(
                    color="{main_color}",
                    radius=0.08
                ).move_to(
                    2 * np.cos(i * TAU / 12) * RIGHT + 1.5 * np.sin(i * TAU / 12) * UP
                )
                dots.add(dot)
            
            # Animate dots appearing in sequence
            for dot in dots:
                self.play(GrowFromCenter(dot), run_time=0.1)
            
            # Create connecting lines
            lines = VGroup()
            for i in range(12):
                line = Line(
                    dots[i].get_center(), 
                    dots[(i + 1) % 12].get_center(),
                    color="{accent_color}",
                    stroke_width=2
                )
                lines.add(line)
            
            for line in lines:
                self.play(Create(line), run_time=0.05)
            
            self.wait(2)
            
        elif {segment_num} == 2:  # FUNDAMENTALS
            # Building blocks animation
            self.play(FadeOut(VGroup(title, subtitle), run_time=1))
            
            blocks = VGroup()
            colors_cycle = ["{main_color}", "{accent_color}", "{colors['success']}"]
            
            for i in range(3):
                for j in range(3):
                    block = Rectangle(
                        width=0.8, height=0.8,
                        color=colors_cycle[(i+j) % 3],
                        fill_opacity=0.7,
                        stroke_width=2
                    ).move_to((i-1) * RIGHT + (j-1) * UP)
                    
                    # Add simple number to each block
                    block_num = Text(
                        str(i*3+j+1),
                        font_size=24,
                        color=WHITE
                    ).move_to(block.get_center())
                    
                    block_group = VGroup(block, block_num)
                    blocks.add(block_group)
            
            # Animate blocks building up
            for block in blocks:
                self.play(FadeIn(block, shift=DOWN*0.5), run_time=0.2)
            
            self.wait(2)
            
        elif {segment_num} == 3:  # PRINCIPLES  
            # Flow diagram with arrows
            self.play(FadeOut(VGroup(title, subtitle), run_time=1))
            
            # Create principle boxes
            principles = VGroup()
            principle_texts = ["Input", "Process", "Output"]
            positions = [LEFT*3, ORIGIN, RIGHT*3]
            
            for text, pos in zip(principle_texts, positions):
                box = Rectangle(
                    width=2, height=1,
                    color="{main_color}",
                    fill_opacity=0.3,
                    stroke_width=3
                ).move_to(pos)
                
                label = Text(text, font_size=28, color=WHITE).move_to(box.get_center())
                principle = VGroup(box, label)
                principles.add(principle)
            
            # Create simple arrows
            arrow1 = Arrow(
                principles[0].get_right() + RIGHT*0.1,
                principles[1].get_left() + LEFT*0.1,
                color="{accent_color}",
                stroke_width=6
            )
            
            arrow2 = Arrow(
                principles[1].get_right() + RIGHT*0.1,
                principles[2].get_left() + LEFT*0.1,
                color="{accent_color}",
                stroke_width=6
            )
            
            # Animate the flow
            self.play(FadeIn(principles[0]))
            self.wait(0.5)
            self.play(Create(arrow1))
            self.play(FadeIn(principles[1]))
            self.wait(0.5)
            self.play(Create(arrow2))
            self.play(FadeIn(principles[2]))
            self.wait(2)
            
        elif {segment_num} == 4:  # EXAMPLE
            # Step-by-step transformation
            self.play(FadeOut(VGroup(title, subtitle), run_time=1))
            
            # Create morphing shapes
            initial_shape = Circle(radius=1, color="{main_color}", fill_opacity=0.5)
            intermediate_shape = Square(side_length=2, color="{accent_color}", fill_opacity=0.5)
            final_shape = Triangle(color="{colors['success']}", fill_opacity=0.5).scale(1.5)
            
            # Step labels
            step1 = Text("Step 1: Start", font_size=24, color=WHITE).to_edge(UP)
            step2 = Text("Step 2: Transform", font_size=24, color=WHITE).to_edge(UP)  
            step3 = Text("Step 3: Result", font_size=24, color=WHITE).to_edge(UP)
            
            # Animate the transformation
            self.play(Write(step1), FadeIn(initial_shape, scale=0.5))
            self.wait(1)
            
            self.play(
                Transform(step1, step2),
                Transform(initial_shape, intermediate_shape),
                run_time=2
            )
            self.wait(1)
            
            self.play(
                Transform(step1, step3),
                Transform(initial_shape, final_shape),
                run_time=2
            )
            self.wait(2)
            
        else:  # CONCLUSION
            # Satisfying finale with all elements
            self.play(FadeOut(VGroup(title, subtitle), run_time=1))
            
            # Create final visual summary
            center_circle = Circle(
                radius=1.5,
                color="{main_color}",
                stroke_width=4,
                fill_opacity=0.2
            )
            
            # Surrounding elements
            satellites = VGroup()
            for i in range(8):
                angle = i * TAU / 8
                satellite = Dot(
                    color="{accent_color}",
                    radius=0.15
                ).move_to(2.5 * np.cos(angle) * RIGHT + 2.5 * np.sin(angle) * UP)
                satellites.add(satellite)
            
            # Connecting lines
            connections = VGroup()
            for satellite in satellites:
                line = Line(
                    center_circle.get_center(),
                    satellite.get_center(),
                    color=WHITE,
                    stroke_width=2,
                    stroke_opacity=0.6
                )
                connections.add(line)
            
            # Final text
            conclusion_text = Text(
                "Beautiful!",
                font_size=48,
                color="{main_color}"
            ).move_to(center_circle.get_center())
            
            # Animate finale
            self.play(FadeIn(center_circle, scale=0.3))
            self.wait(0.5)
            
            for sat in satellites:
                self.play(GrowFromCenter(sat), run_time=0.1)
            
            for conn in connections:
                self.play(Create(conn), run_time=0.05)
            
            self.play(Write(conclusion_text, run_time=2))
            self.wait(2)
        
        # Gentle fade out
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=2)
        self.wait(0.5)
'''
        
        return {
            'code': manim_code,
            'narration': narration,
            'class_name': class_name
        }
    
    def _generate_all_3b1b_fallbacks(self, topic: str) -> dict:
        """Generate all 3B1B fallback segments"""
        segments = {}
        names = ["intro", "fundamentals", "principles", "example", "conclusion"]
        titles = ["INTRO", "FUNDAMENTALS", "PRINCIPLES", "EXAMPLE", "CONCLUSION"]
        
        for i, (name, title) in enumerate(zip(names, titles)):
            segments[name] = self._generate_3b1b_fallback(topic, title, i+1)
        
        return segments
    
    def create_segmented_video(self, topic: str) -> str:
        """Create 5 beautiful 3B1B style segments"""
        
        print(f"🎨 Creating 3Blue1Brown style video for: {topic}")
        
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
            print(f"\n🎨 Processing 3B1B Segment {i}: {name.upper()}")
            
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
            
            # Render video with higher quality for 3B1B style
            try:
                print(f"🎨 Rendering beautiful animation for {name}...")
                cmd = [
                    "manim", 
                    manim_file,
                    segment['class_name'],
                    "-pqm",  # Medium quality for better visuals
                    "--format", "mp4",
                    "--media_dir", temp_dir,
                    "--fps", "30"  # Smooth 30fps
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    cwd=temp_dir,
                    timeout=300  # Longer timeout for quality rendering
                )
                
                if result.returncode == 0:
                    print(f"✨ Beautiful animation rendered for {name}")
                    
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
                            print(f"✨ 3B1B Segment {i} completed: {name}")
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
        """Combine video and audio for one segment with perfect duration matching"""
        
        try:
            print(f"🎞️ Syncing media for segment {segment_num}: {segment_name}")
            
            video = VideoFileClip(video_file)
            audio = AudioFileClip(audio_file)
            
            print(f"📏 Video: {video.duration:.1f}s, Audio: {audio.duration:.1f}s")
            
            # Match durations - use the longer duration
            target_duration = max(video.duration, audio.duration)
            
            if video.duration < target_duration:
                # Extend video by holding last frame
                video = video.loop(duration=target_duration)
            elif video.duration > target_duration:
                # Trim video to match audio
                video = video.subclip(0, target_duration)
                
            if audio.duration < target_duration:
                # Extend audio with silence - create a simple silence using numpy
                import numpy as np
                silence_duration = target_duration - audio.duration
                # Create silence array
                silence_array = np.zeros((int(silence_duration * audio.fps), audio.nchannels))
                # Create AudioArrayClip for the silence
                from moviepy.audio.AudioClip import AudioArrayClip
                silence_clip = AudioArrayClip(silence_array, fps=audio.fps)
                # Concatenate audio with silence
                from moviepy.audio.io.AudioFileClip import CompositeAudioClip
                audio = CompositeAudioClip([audio, silence_clip.set_start(audio.duration)])
            elif audio.duration > target_duration:
                # Trim audio
                audio = audio.subclip(0, target_duration)
            
            # Combine with perfect sync
            final = video.set_audio(audio)
            
            # Save segment
            segment_output = os.path.join(temp_dir, f"segment_{segment_num}_{segment_name}_3b1b.mp4")
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
            
            print(f"✨ Perfect sync achieved for segment {segment_num} ({target_duration:.1f}s)")
            return segment_output
            
        except Exception as e:
            print(f"❌ Failed to sync media for segment {segment_name}: {e}")
            return None
    
    def _combine_all_segments(self, video_files: list, topic: str, timestamp: str) -> str:
        """Combine all segments into stunning final video"""
        
        try:
            print("🎬 Creating final 3Blue1Brown masterpiece...")
            
            clips = []
            total_duration = 0
            
            for video_file in video_files:
                if os.path.exists(video_file):
                    clip = VideoFileClip(video_file)
                    clips.append(clip)
                    total_duration += clip.duration
                    print(f"✨ Added segment: {os.path.basename(video_file)} ({clip.duration:.1f}s)")
            
            if clips:
                final_video = concatenate_videoclips(clips)
                
                output_filename = f"{topic.replace(' ', '_')}_{timestamp}_3Blue1Brown.mp4"
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
                
                print("🎉 3Blue1Brown style masterpiece created!")
                print(f"📁 File: {output_filename}")
                print(f"⏱️ Total duration: {total_duration:.1f} seconds")
                print("🎨 Style: Elegant mathematical beauty")
                return output_filename
            else:
                print("❌ No valid video clips to combine")
                return None
                
        except Exception as e:
            print(f"❌ Failed to create final masterpiece: {e}")
            return None

def main():
    print("🎨 3Blue1Brown Style Video Generator")
    print("Creating elegant mathematical visualizations")
    print("✨ Beautiful • Smooth • Educational")
    print("=" * 50)
    
    api_key = input("Enter your Gemini API key: ").strip()
    if not api_key:
        print("❌ API key required!")
        return
    
    try:
        generator = ThreeBlueBrownStyleGenerator(api_key)
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    topic = input("Enter topic: ").strip()
    if not topic:
        print("❌ Topic required!")
        return
    
    print(f"\n🎨 Creating 3Blue1Brown style video for: {topic}")
    print("📺 Segments: Intro → Fundamentals → Principles → Example → Conclusion")
    print("✨ Style: Dark background, elegant colors, smooth animations")
    
    output = generator.create_segmented_video(topic)
    
    if output:
        print("\n🎊 MASTERPIECE CREATED!")
        print(f"📁 Video: {output}")
        print("🎨 Style: 3Blue1Brown elegance")
        print("✨ Features: Perfect sync, beautiful animations, mathematical elegance")
        print("🔥 Ready to blow minds!")
    else:
        print("\n❌ 3B1B video creation failed")
        print("💡 Try a simpler topic or check dependencies")

if __name__ == "__main__":
    main()