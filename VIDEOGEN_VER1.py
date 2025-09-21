import google.generativeai as genai
import os
import json
import subprocess
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
import tempfile
from datetime import datetime

class LaTeXFreeVideoGenerator:
    def __init__(self, gemini_api_key: str):
        """LaTeX-free video generator for Windows"""
        self.gemini_api_key = gemini_api_key
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        print(f"✅ Initialized with gemini-2.0-flash (LaTeX-free mode)")
        
    def generate_manim_code(self, topic: str) -> tuple:
        """Generate LaTeX-free Manim code"""
        
        prompt = f"""
Create educational content about "{topic}" for a whiteboard-style video.

I need TWO separate things:

1. MANIM CODE - Python animation code (NO LaTeX, only Text() and basic shapes)
2. NARRATION SCRIPT - What the narrator should actually SAY (not timing instructions)

MANIM CONSTRAINTS:
- Use only Text() for text (NO MathTex or Tex)
- White background, black text
- Basic shapes: Rectangle, Circle, Line, Arrow
- Duration: 60-90 seconds

NARRATION REQUIREMENTS:
- Write ACTUAL SPOKEN WORDS that explain the topic
- Natural conversational tone
- No timing cues like "0-5 seconds" or asterisks
- Explain concepts clearly as if teaching a student
- Should be 60-90 seconds when spoken aloud

Topic: {topic}

Format your response EXACTLY like this:

MANIM_CODE:
```python
from manim import *
class TopicVideo(Scene):
    def construct(self):
        self.camera.background_color = WHITE
        # Your animation code here
```

NARRATION:
Hello everyone! Today we're going to explore [topic]. Let me explain the key concepts...
[Continue with actual narration text that teaches the topic]
"""
        
        try:
            print(f"🤖 Generating LaTeX-free content for: {topic}")
            response = self.model.generate_content(prompt)
            content = response.text
            print(f"✅ AI response received!")
            
            # Parse response
            if "MANIM_CODE:" in content and "NARRATION:" in content:
                parts = content.split("NARRATION:")
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
                    manim_code = manim_section
                
                # Validate code (no LaTeX)
                manim_code = self._ensure_latex_free(manim_code, topic)
                
                print(f"📝 Generated LaTeX-free code ({len(manim_code)} chars)")
                print(f"🎵 Generated narration ({len(narration)} chars)")
                return manim_code, narration
            else:
                return self._generate_latex_free_fallback(topic)
                
        except Exception as e:
            print(f"❌ API error: {e}")
            return self._generate_latex_free_fallback(topic)

    def _ensure_latex_free(self, code: str, topic: str) -> str:
        """Remove LaTeX elements and replace with Text()"""
        
        # Replace MathTex with Text
        if "MathTex" in code or "Tex(" in code:
            print("⚠️ Found LaTeX in generated code, converting to Text...")
            
            # Simple replacements for common math expressions
            replacements = {
                r"MathTex(r\"\\frac{df}{dx}": "Text(\"df/dx",
                r"MathTex(r\"\\lim_{": "Text(\"limit as ",
                r"MathTex(r\"": "Text(\"",
                r"MathTex(": "Text(",
                r"Tex(": "Text(",
                r"\\to": " approaches ",
                r"\\frac{": "",
                r"}{": "/",
                r"\\": "",
            }
            
            for old, new in replacements.items():
                code = code.replace(old, new)
        
        return code
    
    def _generate_latex_free_fallback(self, topic: str) -> tuple:
        """Generate guaranteed LaTeX-free Manim code"""
        
        class_name = "".join(word.capitalize() for word in topic.split())
        if class_name[0].isdigit():
            class_name = "Topic" + class_name
            
        manim_code = f'''from manim import *

class {class_name}Video(Scene):
    def construct(self):
        # White background for whiteboard effect
        self.camera.background_color = WHITE
        
        # Title
        title = Text("{topic.title()}", font_size=52, color=BLACK, weight=BOLD)
        title.to_edge(UP, buff=0.8)
        self.play(Write(title), run_time=2)
        self.wait(1)
        
        # Subtitle
        subtitle = Text("A Step-by-Step Guide", font_size=32, color=DARK_BLUE)
        subtitle.next_to(title, DOWN, buff=0.5)
        self.play(Write(subtitle), run_time=1.5)
        self.wait(1)
        
        # Main content area
        content_box = Rectangle(
            width=10, height=4,
            color=BLACK, stroke_width=2,
            fill_opacity=0.05, fill_color=LIGHT_GRAY
        )
        content_box.move_to(ORIGIN)
        self.play(Create(content_box), run_time=1)
        
        # Key concepts (using only Text)
        concept1 = Text("1. Fundamental Concepts", font_size=28, color=BLACK)
        concept2 = Text("2. Core Principles", font_size=28, color=BLACK)
        concept3 = Text("3. Practical Applications", font_size=28, color=BLACK)
        
        concepts = VGroup(concept1, concept2, concept3)
        concepts.arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        concepts.move_to(content_box.get_center() + UP*0.5)
        
        for i, concept in enumerate(concepts):
            self.play(Write(concept), run_time=1)
            self.wait(0.8)
        
        # Example section with shapes
        example_title = Text("Example:", font_size=36, color=DARK_RED, weight=BOLD)
        example_title.next_to(content_box, DOWN, buff=0.8)
        self.play(Write(example_title), run_time=1)
        
        # Visual example using basic shapes
        circle = Circle(radius=0.5, color=BLUE, fill_opacity=0.3)
        arrow = Arrow(start=LEFT, end=RIGHT, color=GREEN, stroke_width=6)
        result_box = Rectangle(width=2, height=0.8, color=RED, stroke_width=3)
        result_text = Text("Result", font_size=24, color=RED)
        
        example_group = VGroup(circle, arrow, result_box)
        example_group.arrange(RIGHT, buff=0.5)
        example_group.next_to(example_title, DOWN, buff=0.5)
        result_text.move_to(result_box.get_center())
        
        self.play(Create(circle), run_time=1)
        self.play(Create(arrow), run_time=1)
        self.play(Create(result_box), run_time=1)
        self.play(Write(result_text), run_time=1)
        self.wait(2)
        
        # Formula representation (using Text only)
        formula_title = Text("Key Formula:", font_size=32, color=DARK_GREEN, weight=BOLD)
        formula_title.to_edge(DOWN, buff=2.5)
        
        # Simple text-based formula (no LaTeX)
        if "calculus" in "{topic}".lower():
            formula_text = Text("f'(x) = limit as h approaches 0 of [f(x+h) - f(x)] / h", 
                              font_size=20, color=BLACK)
        elif "algebra" in "{topic}".lower():
            formula_text = Text("y = mx + b  (slope-intercept form)", 
                              font_size=24, color=BLACK)
        else:
            formula_text = Text(f"Key principle of {topic}", 
                              font_size=24, color=BLACK)
        
        formula_text.next_to(formula_title, DOWN, buff=0.3)
        
        self.play(Write(formula_title), run_time=1)
        self.play(Write(formula_text), run_time=2)
        self.wait(2)
        
        # Conclusion
        conclusion = Text("Thank you for learning!", 
                         font_size=40, color=DARK_GREEN, weight=BOLD)
        conclusion.move_to(ORIGIN)
        
        # Clear screen for conclusion
        everything = VGroup(
            subtitle, content_box, concepts, example_title, 
            circle, arrow, result_box, result_text,
            formula_title, formula_text
        )
        
        self.play(FadeOut(everything), run_time=1.5)
        self.play(Write(conclusion), run_time=2)
        self.wait(2)
'''
        
        narration = f"""
Hello everyone! Welcome to today's lesson on {topic}.

{topic} is a fundamental area of mathematics that plays a crucial role in understanding how things change and optimize in the real world.

Let me walk you through the key concepts you need to understand.

First, let's talk about the fundamental concepts. These form the building blocks of everything we'll learn today. Understanding these basics is essential before we move to more complex ideas.

Next, we have the core principles that govern how {topic} works. These principles help us solve problems systematically and provide a framework for approaching new challenges.

Finally, we'll explore practical applications. This is where {topic} becomes really exciting, as we can see how these mathematical concepts solve real-world problems in fields like engineering, economics, and data science.

Let me show you a simple example to illustrate these concepts. We start with our input data or problem, apply our mathematical process, and arrive at our solution or result.

Now, here's a key relationship that's fundamental to {topic}. This mathematical principle helps us understand the underlying patterns and relationships in the data or problems we're working with.

Understanding these concepts gives you a powerful toolkit for problem-solving. The beauty of {topic} is that once you grasp these fundamentals, you can apply them to countless situations.

Thank you for joining me in this exploration of {topic}. I encourage you to practice these concepts and experiment with different problems to deepen your understanding. Remember, mathematics is best learned through active engagement and practice.
"""
        
        return manim_code, narration

    def _clean_narration_text(self, narration: str) -> str:
        """Clean narration text for proper TTS"""
        
        # Remove timing instructions and formatting
        clean_text = narration
        
        # Remove common TTS-unfriendly patterns
        patterns_to_remove = [
            r'\*.*?\*',  # Remove *asterisk text*
            r'\[.*?\]',  # Remove [bracket text] 
            r'\d+\s*-\s*\d+\s*seconds?',  # Remove "0-5 seconds"
            r'Zero to \w+ second',  # Remove "Zero to five second"
            r'asterisk',  # Remove literal "asterisk"
            r'\(.*?\)',  # Remove parenthetical instructions
        ]
        
        import re
        for pattern in patterns_to_remove:
            clean_text = re.sub(pattern, '', clean_text, flags=re.IGNORECASE)
        
        # Clean up whitespace and formatting
        clean_text = clean_text.replace('\n', ' ')
        clean_text = re.sub(r'\s+', ' ', clean_text)  # Multiple spaces to single
        clean_text = clean_text.strip()
        
        # Ensure it's proper narration text
        if len(clean_text) < 50:  # If too short, it might be instructions
            clean_text = f"""
            Hello everyone! Welcome to today's lesson on the fascinating topic we're exploring.
            
            Let me walk you through the key concepts step by step. Understanding these fundamentals 
            will give you a solid foundation for more advanced topics.
            
            First, we'll cover the basic principles. Then we'll look at practical applications. 
            Finally, we'll see how these concepts connect to real-world problem solving.
            
            The beauty of this subject is how it provides us with powerful tools for understanding 
            and solving complex problems in many different fields.
            
            Thank you for joining me in this learning journey. Remember, practice and exploration 
            are key to mastering these concepts.
            """
        
        return clean_text.strip()

    def _combine_media(self, video_file: str, audio_file: str, topic: str, timestamp: str) -> str:
        """Combine video and audio"""
        
        try:
            print("🎞️ Combining video and audio...")
            
            video = VideoFileClip(video_file)
            audio = AudioFileClip(audio_file)
            
            # Match durations
            min_duration = min(video.duration, audio.duration)
            video = video.subclip(0, min_duration)
            audio = audio.subclip(0, min_duration)
            
            final = video.set_audio(audio)
            
            # Save final video
            output_file = f"{topic.replace(' ', '_')}_{timestamp}_LaTeXFree.mp4"
            final.write_videofile(
                output_file, 
                codec='libx264', 
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Cleanup
            video.close()
            audio.close()  
            final.close()
            
            print(f"🎉 Final video saved: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"❌ Media combination failed: {e}")
            return None
    
    def create_video(self, topic: str) -> str:
        """Create video without LaTeX dependencies"""
        
        print(f"🎬 Creating LaTeX-free video for: {topic}")
        
        # Generate content
        manim_code, narration = self.generate_manim_code(topic)
        
        if not manim_code or not narration:
            print("❌ Failed to generate content from AI - stopping")
            return None
        
        # Create temp files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.mkdtemp()
        
        manim_file = os.path.join(temp_dir, "animation.py")
        audio_file = os.path.join(temp_dir, "narration.mp3")
        
        # Save files
        with open(manim_file, 'w', encoding='utf-8') as f:
            f.write(manim_code)
        print(f"💾 Animation code saved")
        
        # Generate audio with better processing
        print("🎵 Generating narration...")
        try:
            # Clean and process narration
            clean_narration = self._clean_narration_text(narration)
            print(f"📝 Narration preview: {clean_narration[:100]}...")
            
            tts = gTTS(text=clean_narration, lang='en', slow=False)
            tts.save(audio_file)
            print(f"🔊 Audio generated successfully ({len(clean_narration)} characters)")
        except Exception as e:
            print(f"❌ Audio generation failed: {e}")
            return None
        
        # Render video
        print("🎥 Rendering animation...")
        try:
            # Find class name
            lines = manim_code.split('\n')
            class_name = None
            for line in lines:
                if 'class ' in line and '(Scene):' in line:
                    class_name = line.split('class ')[1].split('(')[0].strip()
                    break
            
            if not class_name:
                print("❌ Could not find class name")
                return None
            
            print(f"🎯 Rendering class: {class_name}")
            
            # Render with Manim (low quality for speed)
            cmd = [
                "manim", 
                manim_file,
                class_name,
                "-pql",  # Preview quality, low resolution
                "--format", "mp4",
                "--media_dir", temp_dir
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=temp_dir,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print("✅ Animation rendered successfully!")
                
                # Find video file
                video_file = None
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.mp4') and 'videos' in root:
                            video_file = os.path.join(root, file)
                            break
                    if video_file:
                        break
                
                if video_file and os.path.exists(video_file):
                    final_video = self._combine_media(video_file, audio_file, topic, timestamp)
                    return final_video
                else:
                    print("❌ Video file not found after rendering")
                    return None
            else:
                print(f"❌ Manim rendering failed:")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Rendering timed out (>5 minutes)")
            return None
        except Exception as e:
            print(f"❌ Rendering error: {e}")
            return None

def main():
    print("🚀 LaTeX-Free Video Generator (Windows Compatible)")
    print("=" * 50)
    
    api_key = input("Enter your Gemini API key: ").strip()
    if not api_key:
        print("❌ API key required!")
        return
    
    try:
        generator = LaTeXFreeVideoGenerator(api_key)
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    topic = input("Enter topic: ").strip()
    if not topic:
        print("❌ Topic required!")
        return
    
    print(f"\n🎬 Creating video for: {topic}")
    print("📝 Note: Using LaTeX-free mode for Windows compatibility")
    
    output = generator.create_video(topic)
    
    if output:
        print(f"\n🎊 SUCCESS!")
        print(f"📁 Video file: {output}")
        print(f"🎬 Ready for upload!")
        print(f"💡 This version works without LaTeX installation!")
    else:
        print(f"\n❌ Video creation failed")
        print(f"💡 Try installing LaTeX if you want math formulas:")
        print(f"   - Download MiKTeX: https://miktex.org/download")
        print(f"   - Or use this LaTeX-free version for basic content")

if __name__ == "__main__":
    main()