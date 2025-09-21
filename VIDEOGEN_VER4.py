import google.generativeai as genai
import os
import json
import subprocess
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import tempfile
from datetime import datetime
import re

class EducationalVideoGenerator:
    def __init__(self, gemini_api_key: str):
        """Educational video generator focused on math/ML/AI concepts"""
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Approved topics - only math/ML/AI/programming/stats/probability/simulation/transformers
        self.approved_keywords = [
            'calculus', 'derivative', 'integral', 'gradient', 'optimization',
            'machine learning', 'neural network', 'deep learning', 'backpropagation',
            'linear algebra', 'matrix', 'vector', 'eigenvalue', 'eigenvector',
            'statistics', 'probability', 'bayes', 'distribution', 'regression',
            'programming', 'algorithm', 'complexity', 'recursion', 'dynamic programming',
            'transformer', 'attention', 'embedding', 'convolution', 'lstm',
            'simulation', 'monte carlo', 'markov', 'random walk',
            'differential equation', 'fourier', 'laplace', 'optimization',
            'loss function', 'cost function', 'activation function',
            'clustering', 'classification', 'dimensionality reduction',
            'overfitting', 'regularization', 'cross validation'
        ]
        print("Educational Generator Initialized")
        
    def is_approved_topic(self, topic: str) -> bool:
        """Check if topic is educational and approved"""
        topic_lower = topic.lower()
        return any(keyword in topic_lower for keyword in self.approved_keywords)
        
    def generate_segments(self, topic: str) -> dict:
        """Generate educational segments with real mathematical content"""
        
        if not self.is_approved_topic(topic):
            print(f"Topic '{topic}' not approved. Focus on math/ML/AI/programming/stats/probability/simulation/transformers")
            return None
            
        prompt = f"""
Create educational content about "{topic}" using ONLY basic Manim elements.

You MUST create exactly 5 segments with these exact headers:

SEGMENT_1_INTRO:
SEGMENT_2_FUNDAMENTALS:
SEGMENT_3_PRINCIPLES:
SEGMENT_4_EXAMPLE:
SEGMENT_5_CONCLUSION:

RULES:
- NO LaTeX: Never use Tex(), MathTex(), MathText()
- NO images: Never use ImageMobject(), SVGMobject()
- ONLY use: Text(), Circle, Rectangle, Line, Dot, Arrow  
- ALL coordinates must be 3D: [x, y, 0] not [x, y]
- Use proper 3D format: Line(start=[-3, 0, 0], end=[3, 0, 0])
- ONLY use: Create, FadeIn, FadeOut, Write, Transform
- Background: "#0f1419"
- Colors: BLUE, RED, GREEN, YELLOW, WHITE, ORANGE

FORMAT EXACTLY LIKE THIS:

SEGMENT_1_INTRO:
MANIM_CODE:
```python
from manim import *

class IntroVideo(Scene):
    def construct(self):
        self.camera.background_color = "#0f1419"
        title = Text("Calculus for ML", font_size=48, color=BLUE)
        subtitle = Text("Why derivatives matter", font_size=32, color=WHITE)
        subtitle.next_to(title, DOWN)
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2)
```
NARRATION:
Calculus forms the foundation of machine learning. Derivatives help us optimize models by finding the steepest direction to minimize errors.

SEGMENT_2_FUNDAMENTALS:
MANIM_CODE:
```python
from manim import *

class FundamentalsVideo(Scene):
    def construct(self):
        self.camera.background_color = "#0f1419"
        equation = Text("f'(x) = df/dx", font_size=40, color=YELLOW)
        meaning = Text("Rate of change", font_size=30, color=WHITE)
        meaning.next_to(equation, DOWN)
        self.play(Write(equation))
        self.play(FadeIn(meaning))
        self.wait(2)
```
NARRATION:
The derivative f'(x) measures how fast a function changes. In machine learning, we use this to find the direction that reduces our loss function fastest.

SEGMENT_3_PRINCIPLES:
MANIM_CODE:
```python
from manim import *

class PrinciplesVideo(Scene):
    def construct(self):
        self.camera.background_color = "#0f1419"
        title = Text("Gradient Descent", font_size=40, color=GREEN)
        step1 = Text("1. Calculate gradient", font_size=30, color=WHITE)
        step2 = Text("2. Move opposite direction", font_size=30, color=WHITE)
        step1.next_to(title, DOWN)
        step2.next_to(step1, DOWN)
        self.play(Write(title))
        self.play(FadeIn(step1))
        self.play(FadeIn(step2))
        self.wait(2)
```
NARRATION:
Gradient descent uses derivatives to optimize machine learning models. We calculate the gradient and move in the opposite direction to minimize the loss function.

SEGMENT_4_EXAMPLE:
MANIM_CODE:
```python
from manim import *

class ExampleVideo(Scene):
    def construct(self):
        self.camera.background_color = "#0f1419"
        plane = NumberPlane(x_range=[-3, 3], y_range=[-2, 4])
        curve_points = []
        for x in range(-20, 21):
            x_val = x / 10
            y_val = x_val * x_val
            curve_points.append(plane.c2p(x_val, y_val))
        
        dots = VGroup()
        for point in curve_points[::4]:
            dot = Dot(point, color=RED, radius=0.05)
            dots.add(dot)
        
        self.play(FadeIn(plane))
        self.play(Create(dots))
        self.wait(2)
```
NARRATION:
Here we see a parabola representing a loss function. The derivative at each point shows the slope, helping us find the minimum where the error is smallest.

SEGMENT_5_CONCLUSION:
MANIM_CODE:
```python
from manim import *

class ConclusionVideo(Scene):
    def construct(self):
        self.camera.background_color = "#0f1419"
        title = Text("Key Takeaway", font_size=40, color=ORANGE)
        point = Text("Calculus optimizes ML models", font_size=32, color=WHITE)
        point.next_to(title, DOWN)
        self.play(Write(title))
        self.play(FadeIn(point))
        self.wait(2)
```
NARRATION:
Calculus is essential for machine learning because it gives us the mathematical tools to optimize our models and minimize prediction errors efficiently.

Now create similar content for "{topic}" following this exact format.
"""
        
        try:
            print(f"Generating educational content for: {topic}")
            response = self.model.generate_content(prompt)
            content = response.text
            print(f"AI response received, length: {len(content)} characters")
            
            segments = {}
            segment_names = ["INTRO", "FUNDAMENTALS", "PRINCIPLES", "EXAMPLE", "CONCLUSION"]
            
            # Debug: show what content we got
            print("Searching for segments in AI response...")
            for i, name in enumerate(segment_names, 1):
                segment_key = f"SEGMENT_{i}_{name}:"
                if segment_key in content:
                    print(f"Found segment: {name}")
                else:
                    print(f"Missing segment: {name}")
            
            for i, name in enumerate(segment_names, 1):
                segment_key = f"SEGMENT_{i}_{name}:"
                if segment_key in content:
                    start_idx = content.find(segment_key)
                    if i < len(segment_names):
                        next_segment_key = f"SEGMENT_{i+1}_{segment_names[i]}:"
                        end_idx = content.find(next_segment_key)
                        if end_idx == -1:
                            end_idx = len(content)
                    else:
                        end_idx = len(content)
                    
                    segment_content = content[start_idx:end_idx]
                    manim_code, narration = self._parse_segment(segment_content)
                    
                    if manim_code and narration:
                        clean_code = self._clean_code(manim_code)
                        if clean_code:
                            class_match = re.search(r'class (\w+)\(Scene\):', clean_code)
                            actual_class_name = class_match.group(1) if class_match else f"{name.capitalize()}Video"
                            segments[name.lower()] = {
                                'code': clean_code,
                                'narration': self._clean_narration(narration),
                                'class_name': actual_class_name  # Use the actual class name from code
                            }
                            print(f"Generated segment: {name}")
                        else:
                            print(f"Invalid code for segment: {name}")
                            return None
                    else:
                        print(f"Failed to parse segment: {name}")
                        return None
            
            return segments if len(segments) == 5 else None
                
        except Exception as e:
            print(f"Generation failed: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_segment(self, segment_content: str) -> tuple:
        """Parse manim code and narration"""
        try:
            if "MANIM_CODE:" in segment_content and "NARRATION:" in segment_content:
                parts = segment_content.split("NARRATION:")
                manim_section = parts[0].replace("MANIM_CODE:", "").strip()
                narration = parts[1].strip()
                
                if "```python" in manim_section:
                    code_start = manim_section.find("```python") + 9
                    code_end = manim_section.find("```", code_start)
                    if code_end == -1:
                        code_end = len(manim_section)
                    manim_code = manim_section[code_start:code_end].strip()
                else:
                    manim_code = manim_section.strip()
                
                return manim_code, narration
        except Exception as e:
            print(f"Parse error: {e}")
        return None, None
    
    def _clean_code(self, code: str) -> str:
        """Aggressively remove all LaTeX and problematic features"""
        
        # Check for ANY LaTeX-related content
        latex_indicators = [
            'Tex(', 'MathTex(', 'MathText(', '\\\\', '\\frac', '\\sum', '\\int',
            '\\alpha', '\\beta', '\\gamma', '\\delta', '\\theta', '\\pi', '\\sigma',
            '\\partial', '\\nabla', '\\infty', '\\rightarrow', '\\leftarrow',
            'TexTemplate', 'tex_template', '$', '$$', '\\begin{', '\\end{',
            '\\mathbf', '\\mathrm', '\\text{', '\\left(', '\\right)', 
            'ImageMobject', 'SVGMobject', '.png', '.jpg', '.svg',
            'ParametricFunction', 'ValueTracker', 'always_redraw',
            'LaggedStart', 'AnimationGroup', 'Succession', 'add_coordinate_labels',
            'add_coordinate_labels', 'Line(*',
            'NumberPlane', 'get_x_axis_label', 'get_y_axis_label', 'axes.plot',
            'axis_config', '.plot(', 'coords_to_point'
        ]
        
        # If ANY LaTeX indicator is found, reject completely
        for indicator in latex_indicators:
            if indicator in code:
                print(f"LaTeX/problematic content detected: '{indicator}'")
                return None
        
        # Additional safety replacements
        safe_replacements = [
            ('font="CMU Serif"', ''),
            ('weight=BOLD', ''),
            ('rate_func=smooth', ''),
            ('self.camera.frame', '# camera disabled'),
        ]
        
        clean_code = code
        for old, new in safe_replacements:
            clean_code = clean_code.replace(old, new)
        
        print("Code passed LaTeX safety check")
        return clean_code
    
    def _clean_narration(self, narration: str) -> str:
        """Clean narration text"""
        # Remove annotations and cleanup
        patterns = [
            r'\*.*?\*',
            r'\[.*?\]',
            r'\(.*?\)',
        ]
        
        clean_text = narration
        for pattern in patterns:
            clean_text = re.sub(pattern, '', clean_text)
        
        clean_text = re.sub(r'\s+', ' ', clean_text.replace('\n', ' ')).strip()
        return clean_text
    
    def create_video(self, topic: str) -> str:
        """Create educational video"""
        
        if not self.is_approved_topic(topic):
            print(f"Topic '{topic}' not approved")
            print("Approved topics: math, ML, AI, programming, statistics, probability, simulation, transformers")
            return None
        
        print(f"Creating educational video: {topic}")
        
        segments = self.generate_segments(topic)
        if not segments:
            print("Failed to generate educational content")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.mkdtemp()
        final_videos = []
        
        for i, (name, segment) in enumerate(segments.items(), 1):
            print(f"\nProcessing Segment {i}: {name.upper()}")
            
            # Save code
            manim_file = os.path.join(temp_dir, f"segment_{i}.py")
            with open(manim_file, 'w', encoding='utf-8') as f:
                f.write(segment['code'])
                print(f"Segment {i} code preview: {segment['code'][:100]}...")
            
            # Generate audio
            audio_file = os.path.join(temp_dir, f"segment_{i}.mp3")
            try:
                tts = gTTS(text=segment['narration'], lang='en', slow=False)
                tts.save(audio_file)
                print("Audio generated")
            except Exception as e:
                print(f"Audio failed: {e}")
                return None
            
            # Render video
            try:
                print("Rendering animation...")
                cmd = [
                    "manim", 
                    manim_file,
                    segment['class_name'],
                    "-pql",  # Low quality for faster rendering  
                    "--format", "mp4",
                    "--media_dir", temp_dir,
                    "--verbosity", "DEBUG"  # More verbose output
                ]
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    cwd=temp_dir,
                    timeout=180
                )
                
                if result.returncode != 0:
                    print(f"Rendering failed: {result.stderr}")
                    return None
                
                # Find video file - check all possible locations
                # Find video file - check all possible locations
                video_file = None
                print(f"Looking for video file in: {temp_dir}")

                # FIRST look for the specific segment's Manim output
                manim_paths = [
                    os.path.join(temp_dir, "videos", f"segment_{i}", "480p15", f"{segment['class_name']}.mp4"),
                    os.path.join(temp_dir, "media", "videos", f"segment_{i}", "480p15", f"{segment['class_name']}.mp4"),
                ]

                for path in manim_paths:
                    if os.path.exists(path):
                        video_file = path
                        print(f"Found Manim video: {path}")
                        break

                # ONLY if Manim video not found, then search generally
                if not video_file:
                    for root, dirs, files in os.walk(temp_dir):
                        # Skip already processed final videos
                        if "final.mp4" in root:
                            continue
                        for file in files:
                            if file.endswith('.mp4') and segment['class_name'] in file:
                                video_file = os.path.join(root, file)
                                break
                
                if not video_file:
                    print(f"No MP4 file found in {temp_dir}")
                    print("Checking if manim created any output...")
                    # Try common manim output paths
                    possible_paths = [
                        os.path.join(temp_dir, "media", "videos", f"segment_{i}", "480p15", f"{segment['class_name']}.mp4"),
                        os.path.join(temp_dir, "media", "videos", "480p15", f"{segment['class_name']}.mp4"),
                        os.path.join(temp_dir, f"{segment['class_name']}.mp4"),
                    ]
                    
                    for path in possible_paths:
                        if os.path.exists(path):
                            video_file = path
                            print(f"Found video at: {path}")
                            break
                    
                    if not video_file:
                        print("Video file not found anywhere")
                        print(f"Manim stderr: {result.stderr}")
                        print(f"Manim stdout: {result.stdout}")
                        return None
                
                # Combine video and audio
                combined = self._combine_media(video_file, audio_file, i, temp_dir)
                if not combined:
                    print("Media combination failed")
                    return None
                    
                final_videos.append(combined)
                print(f"Segment {i} completed")
                
            except Exception as e:
                print(f"Processing failed: {e}")
                return None
        
        # Combine all segments
        if len(final_videos) == 5:
            return self._combine_all(final_videos, topic, timestamp)
        else:
            print(f"Incomplete video ({len(final_videos)}/5 segments)")
            return None
    
    def _combine_media(self, video_file: str, audio_file: str, segment_num: int, temp_dir: str) -> str:
        """Combine video and audio"""
        try:
            video = VideoFileClip(video_file)
            audio = AudioFileClip(audio_file)
            
            print(f"Video: {video.duration:.1f}s, Audio: {audio.duration:.1f}s")
            
            # Match durations - use the longer one
            max_duration = max(video.duration, audio.duration)
            
            if video.duration < max_duration:
                # Loop video to match audio duration
                #video = video.loop(duration=max_duration)
                last_frame = video.to_ImageClip(duration=max_duration - video.duration)
                video = concatenate_videoclips([video, last_frame])
                print(f"Extended video to {max_duration:.1f}s")
            elif video.duration > max_duration:
                # Trim video to match audio
                video = video.subclip(0, max_duration)
                print(f"Trimmed video to {max_duration:.1f}s")
            
            if audio.duration < max_duration:
                # Extend audio with silence
                import numpy as np
                from moviepy.audio.AudioClip import AudioArrayClip
                from moviepy.audio.AudioClip import CompositeAudioClip  # Correct import
                
                silence_duration = max_duration - audio.duration
                silence_array = np.zeros((int(silence_duration * audio.fps), audio.nchannels))
                silence_clip = AudioArrayClip(silence_array, fps=audio.fps)
                audio = CompositeAudioClip([audio, silence_clip.set_start(audio.duration)])
                print(f"Extended audio with {silence_duration:.1f}s silence")
            elif audio.duration > max_duration:
                # Trim audio to match
                audio = audio.subclip(0, max_duration)
                print(f"Trimmed audio to {max_duration:.1f}s")
            
            # Combine video and audio
            final = video.set_audio(audio)
            output = os.path.join(temp_dir, f"segment_{segment_num}_final.mp4")
            
            print("Writing final video...")
            final.write_videofile(
                output, 
                codec='libx264',
                audio_codec='aac',
                verbose=False, 
                logger=None
            )
            
            # Cleanup
            video.close()
            audio.close() 
            final.close()
            
            print(f"Segment {segment_num} combined successfully")
            return output
            
        except Exception as e:
            print(f"Media combination error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _combine_all(self, video_files: list, topic: str, timestamp: str) -> str:
        """Combine all segments"""
        try:
            clips = [VideoFileClip(f) for f in video_files if os.path.exists(f)]
            if not clips:
                return None
                
            final_video = concatenate_videoclips(clips)
            output_filename = f"{topic.replace(' ', '_')}_{timestamp}.mp4"
            final_video.write_videofile(output_filename, verbose=False, logger=None)
            
            for clip in clips:
                clip.close()
            final_video.close()
            
            total_duration = sum(clip.duration for clip in clips)
            print(f"\nEducational video created!")
            print(f"File: {output_filename}")
            print(f"Duration: {total_duration:.1f}s")
            return output_filename
            
        except Exception as e:
            print(f"Final combination failed: {e}")
            return None

def main():
    print("Educational Video Generator")
    print("Focus: Math, ML, AI, Programming, Statistics, Probability, Simulation, Transformers")
    print("=" * 60)
    
    api_key = input("Gemini API key: ").strip()
    if not api_key:
        print("API key required")
        return
    
    generator = EducationalVideoGenerator(api_key)
    
    topic = input("Enter topic: ").strip()
    if not topic:
        print("Topic required")
        return
    
    result = generator.create_video(topic)
    if result:
        print(f"\nSuccess: {result}")
    else:
        print("\nFailed to create video")

if __name__ == "__main__":
    main()