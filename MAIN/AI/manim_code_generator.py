import os
import re
import json
import logging
from dotenv import load_dotenv
import textwrap  
from collections import deque
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
#from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from collections import deque

# Basic logging configuration
logging.basicConfig(level=logging.INFO)
logging.getLogger('comtypes').setLevel(logging.WARNING)

load_dotenv('.env')

# ==========================================================
#  Custom lightweight ConversationChain replacement
# ==========================================================
class ConversationChainLite:
    def __init__(self, llm, prompt=None, memory=None, input_key="human_input", verbose=False):
        self.llm = llm
        self.prompt = prompt
        self.verbose = verbose
        self.input_key = input_key
        self.memory = memory or deque(maxlen=5)

    def predict(self, **kwargs):
        human_input = kwargs.get(self.input_key, "")
        chat_history = list(self.memory)

        if self.verbose:
            print("🧩 Prompt input:", human_input)

        response = self.llm.invoke(human_input)
        text = getattr(response, "content", None) or getattr(response, "text", "")
        self.memory.append(AIMessage(content=text))
        return text

class ManIMCodeGenerator:
    def __init__(self, google_api_key):
        self.google_api_key = google_api_key
        self.memory = deque(maxlen=3)
        self.google_chat = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=self.google_api_key,
            temperature=0.5,
            max_output_tokens=None,
            timeout=None,
            max_retries=2
        )
        
        self.manim_prompt = self._create_manim_generation_prompt()
        self.manim_conversation = ConversationChainLite(
            llm=self.google_chat,
            prompt=self.manim_prompt,
            verbose=True,
            memory=self.memory,
            input_key="human_input",
        )

    def generate_3b1b_manim_code(self, video_plan):
        """
        Generate comprehensive, dynamic Manim code following 3Blue1Brown style.
        
        This creates step-by-step animations with:
        - Rich visual elements and smooth transitions
        - Dynamic positioning and movement
        - Scene progression without overlapping text
        - Educational flow based on the video plan structure
        
        Args:
            video_plan (dict): Complete video plan from script generator
            
        Returns:
            str: Complete Manim Python code ready for execution
        """
        if not video_plan:
            raise ValueError("No video plan provided")
            
        educational_breakdown = video_plan.get("educational_breakdown", {})
        manim_structure = video_plan.get("manim_structure", {})
        
        if not educational_breakdown:
            raise ValueError("No educational content available, JAJAJJA")
        
        try:
            print("🎨 Generating Advanced Manim Code...")
            print("📚 Topic: {}".format(educational_breakdown.get('title', 'Unknown')))
            print("🎯 Educational Steps: {}".format(len(educational_breakdown.get('educational_steps', []))))
            print("=" * 60)
            
            # Display video plan details in terminal
            self._display_video_plan(video_plan)
            
            # Build comprehensive prompt for Manim code generation
            manim_prompt = self._build_advanced_manim_prompt(video_plan)
            
            print("🔄 Processing with AI...")
            response = self.manim_conversation.predict(human_input=manim_prompt)
            
            # Extract and validate Manim code
            manim_code = self._extract_manim_code(response)
            
            # Validate and fix the code to remove image references
            if manim_code:
                manim_code = self._validate_and_fix_manim_code(manim_code)
            
            if manim_code:
                print("✅ Advanced Manim Code Generated Successfully!")
                print("📝 Code Length: {} characters".format(len(manim_code)))
                print("🎬 Ready for animation rendering!")
                
                # Display generated manim code in terminal
                self._display_manim_code(manim_code)
                
                return manim_code
            else:
                raise Exception("Code extraction failed")
                
        except Exception as e:
            print("❌ Error in Manim code generation: {}".format(e))
            raise

    def _build_advanced_manim_prompt(self, video_plan):
        """
        Build a comprehensive prompt for advanced Manim code generation.
        
        Args:
            video_plan (dict): Complete video plan with educational breakdown
            
        Returns:
            str: Detailed prompt for Manim code generation
        """
        educational_breakdown = video_plan.get("educational_breakdown", {})
        manim_structure = video_plan.get("manim_structure", {})
        
        title = educational_breakdown.get("title", "Educational Animation")
        steps = educational_breakdown.get("educational_steps", [])
        duration = educational_breakdown.get("metadata", {}).get("estimated_total_duration", 180)
        
        prompt_parts = ["""
ADVANCED MANIM CODE GENERATION REQUEST

VIDEO PLAN TO IMPLEMENT:
Title: {title}
Duration: {duration} seconds
Educational Steps: {steps_count}""".format(title=title, duration=duration, steps_count=len(steps)) + """

REQUIREMENTS FOR MANIM CODE:
🎯 EDUCATIONAL FLOW:
- Convert each educational step into a distinct scene method
- Maintain pedagogical progression from the video plan
- Use dynamic positioning and smooth transitions
- Create engaging visual storytelling

🎨 ANIMATION STYLE (3Blue1Brown Inspired):
- Rich visual elements with proper spacing
- Dynamic camera movements when appropriate
- Smooth object transformations and reveals
- Color-coded elements for better understanding
- Mathematical notation rendered clearly
- No overlapping text or crowded scenes

🏗️ CODE STRUCTURE REQUIREMENTS:
- Main scene class inheriting from Scene
- Separate methods for each educational step
- construct() method orchestrating the flow
- Proper imports and dependencies
- Clean, well-documented code
- Modular design for easy modification

🎬 ANIMATION TECHNIQUES:
- Use Write(), FadeIn(), Transform(), Create() appropriately
- Implement proper timing with self.wait()
- Position elements using UP, DOWN, LEFT, RIGHT vectors
- Scale and rotate objects for visual interest
- Use color schemes that enhance understanding
- Clear scene transitions between steps

📊 VISUAL ELEMENTS TO INCLUDE:
- Title animations with engaging reveals
- No 16:9 aspect ratio images or ImageMobject
- No 16:9 aspect ration text or TextMobject
- Step-by-step concept introductions
- Mathematical equations and formulas
- Diagrams and geometric shapes (using built-in Manim objects)
- Text labels and annotations
- Real-world example descriptions (text-based, NO ImageMobject)
- Summary and key takeaway displays

⚠️ CRITICAL CONSTRAINTS:
- DO NOT use ImageMobject or any image file references
- Use only text, shapes, and built-in Manim objects
- Create visual diagrams using Circle, Rectangle, Line, etc.
- Represent real-world examples with text descriptions and geometric visualizations
- Focus on mathematical notation, graphs, and animated text elements

⚡ MANDATORY OBJECT UPDATE & TRANSITION RULES:

1. NEVER overwrite or layer new numbers/text on top of old ones.  
   If you show [9], then later want to show [10], you MUST either:  
   - (Preferred) Transform [9] → [10] using Transform(old_obj, new_obj), OR  
   - (If context changed) Fully remove [9] via FadeOut() before creating [10].

2. Every major step transition MUST begin with a clean slate:  
   ```python
   if self.mobjects:  
       self.play(FadeOut(*self.mobjects), run_time=0.5)  
   self.wait(0.3)
   ```

3. For numbered sequences within the same logical idea (e.g., counting, iterations):  
   - Keep the container object (e.g., a MathTex or Text) and update it via Transform:
    ```python  
    counter = MathTex("9")  
    self.play(Write(counter))  
    new_counter = MathTex("10")  
    self.play(Transform(counter, new_counter))
    ```  
   - Never do: self.play(Write(MathTex("10"))) while MathTex("9") is still on screen.

4. Visual flow rule:  
   If content stays on screen across steps, move it or transform it—don’t leave it static while new content appears nearby. Use .animate.shift(), .animate.scale(), or Indicate() to maintain dynamism.

5. Position registry reset:  
   After FadeOut(*self.mobjects), assume all positions are free. No need to manually manage registry if you clear the scene.

✅ Summary for AI:  
“If old content is no longer relevant, fade it out completely before showing new content. If it’s part of a sequence, transform it—never draw new text at the same coordinates.”

🎯 MANDATORY POSITIONING RULES:
- NEVER place text in the same position (0,0) or ORIGIN
- Use UP, DOWN, LEFT, RIGHT with multipliers (2*UP, 3*LEFT, etc.)
- Position titles at 3*UP, subtitles at 2*UP, content at ORIGIN to DOWN
- Move previous content OFF-SCREEN before adding new content
- Use .shift(LEFT*4) or .shift(RIGHT*4) to move objects sideways
- Scale objects (.scale(0.8)) to fit more content without overlap
- Always animate movements: self.play(obj.animate.shift(UP*2))

📺 16:9 ASPECT RATIO OPTIMIZATION:
- Standard Manim resolution is 1920x1080 (16:9)
- Horizontal safe zone: X positions from -6 to +6 units
- Vertical safe zone: Y positions from -3.5 to +3.5 units
- NEVER position text beyond X=±5 or Y=±3 to prevent cutoff
- Use .scale() to fit longer text instead of extending beyond screen bounds
- Position titles between Y=2.5 to Y=3.5 for optimal visibility
- Place main content between Y=-0.5 to Y=2 for best readability
- Use LEFT=-5, RIGHT=5 for wide layouts, LEFT=-3, RIGHT=3 for compact layouts
- Test positioning: title.shift(UP*3) should never go beyond screen top
- For wide equations, use font_size reduction instead of horizontal overflow

🚫 ULTRA-STRICT TEXT OVERLAP PREVENTION SYSTEM:

CRITICAL POSITIONING RULES - MUST FOLLOW FOR EVERY TEXT OBJECT:

1. MANDATORY POSITION TRACKING:
   - Create position_registry = {} at start of construct()
   - Format: position_registry[object_id] = (x, y, width, height)
   - NEVER place text without checking registry first

2. COLLISION DETECTION (MANDATORY):
    ```python
    def check_position_free(self, new_x, new_y, new_width, new_height):
        BUFFER = 0.8  # Minimum spacing between objects
        for obj_id, (x, y, w, h) in self.position_registry.items():
            # Check if rectangles overlap with buffer
            if (abs(new_x - x) < (new_width + w)/2 + BUFFER and
                abs(new_y - y) < (new_height + h)/2 + BUFFER):
                return False  # Position occupied!
        return True  # Position free
    ```

3. AUTOMATIC POSITION FINDING:
   - If preferred position occupied, AUTO-SHIFT to nearest free position
   - Check positions in this order: original → +0.8 units Y → -0.8 units Y → +1.5 units X → -1.5 units X
   - NEVER use same position twice

4. STRICT VERTICAL ZONING (NO EXCEPTIONS):
   Zone 1 (TITLE):     Y = 3.0 to 2.5  (ONLY 1 object allowed)
   Zone 2 (SUBTITLE):  Y = 2.0 to 1.5  (Max 2 objects, use LEFT/RIGHT separation)
   Zone 3 (MAIN):      Y = 1.0 to -1.0 (Max 3 objects, use column layout)
   Zone 4 (DETAIL):    Y = -1.5 to -2.0 (Max 2 objects)
   Zone 5 (FOOTER):    Y = -2.5 to -3.0 (Max 1 object)

5. MANDATORY CLEARING BETWEEN STEPS:
   ```python
   def transition_to_next_step(self):
       # Clear EVERYTHING except persistent elements
       self.play(FadeOut(*self.mobjects))
       self.position_registry.clear()  # CRITICAL: Reset registry
       self.wait(0.5)
   ```

6. MULTI-LINE TEXT HANDLING:
   - For text longer than 50 characters: ALWAYS use VGroup with line breaks
   - Example:
   ```python
   long_text = VGroup(
       Text("Line 1 content", font_size=20),
       Text("Line 2 content", font_size=20).shift(DOWN*0.4)
   ).arrange(DOWN, buff=0.3)
   ```

7. FONT SIZE RULES FOR COMPLEX TOPICS:
   - Titles: 36-40 (NOT 48 - too large for complex topics)
   - Subtitles: 28-32
   - Main content: 20-24
   - Details: 18-20
   - If text doesn't fit: REDUCE font_size, NEVER extend beyond bounds

8. HORIZONTAL LAYOUT FOR COMPLEX TOPICS:
   - Use 2-column layout: LEFT side (X=-4 to -1.5), RIGHT side (X=1.5 to 4)
   - Use 3-column layout: LEFT (X=-5 to -2), CENTER (X=-1.5 to 1.5), RIGHT (X=2 to 5)
   - NEVER put more than 2 text objects in same column at same Y level

9. DYNAMIC POSITIONING EXAMPLE:
   ```python
   # BAD - Static positioning, will overlap:
   title = Text("Title").shift(UP*3)
   subtitle = Text("Subtitle").shift(UP*3)  # OVERLAPS!
   
   # GOOD - Check and adjust:
   title = Text("Title").shift(UP*3)
   self.add_to_registry(title, "title")
   
   subtitle_pos = UP*2.5  # Try here first
   if not self.check_position_free(subtitle_pos):
       subtitle_pos = UP*2.0  # Adjust if needed
   subtitle = Text("Subtitle").shift(subtitle_pos)
   self.add_to_registry(subtitle, "subtitle")
   ```

10. SCREEN BOUNDS VALIDATION (MANDATORY):
    Before adding ANY object:
    - X must be in range: -5.5 to 5.5
    - Y must be in range: -3.0 to 3.0
    - Object width must be < 11 units (use .scale() if needed)
    - Object height must be < 6 units

⚠️ FAILURE TO FOLLOW THESE RULES = OVERLAPPING TEXT = CODE REJECTED

🎭 DYNAMIC VISUAL EXPLANATION REQUIREMENTS:
- EVERY concept must have animated visual representation
- Transform abstract ideas into moving geometric shapes
- Use morphing animations: circle.animate.transform(square)
- Implement step-by-step reveals with Write(), FadeIn(), Create()
- Show mathematical relationships through connecting arrows and lines
- Use color changes to highlight transformations: obj.animate.set_color(YELLOW)
- Create animated comparisons: split screen with before/after animations
- Build complexity progressively: start simple, add details with each step
- Use Indicate(), Flash(), Wiggle() to emphasize key moments
- Implement object journeys: move elements across screen to show relationships
- Create visual metaphors using basic shapes and their transformations
- Use growth animations: GrowFromCenter(), DrawBorderThenFill()
- Show cause-and-effect through animated sequences
- Implement visual proofs through animated geometric demonstrations

🎬 REQUIRED ANIMATION PATTERNS:
- Start each section by clearing: self.play(FadeOut(*self.mobjects))
- Introduce titles with Write() animation
- Move titles up: self.play(title.animate.shift(UP*2))
- Add content below with different Y positions
- Use Transform() to change content, not create new overlapping text
- End sections with content moving off-screen or fading out

🎬 ADVANCED DYNAMIC ANIMATION REQUIREMENTS:
- NO STATIC SCENES: Everything must move, transform, or animate
- Use continuous motion: objects entering, moving, transforming, exiting
- Implement smooth transitions between all visual elements
- Create visual flow: guide viewer's eye with moving objects
- Use multiple simultaneous animations: self.play(obj1.animate.shift(), obj2.animate.scale())
- Implement entrance animations: objects slide in from edges of screen
- Use exit animations: objects fade out or slide away before new content
- Create animated connections: lines/arrows that draw between related concepts
- Implement progressive disclosure: reveal information piece by piece
- Use animated highlighting: temporary color changes, scaling, rotation
- Create visual rhythms: alternating fast and slow animations for pacing
- Build anticipation: use small movements before major reveals
- Implement visual callbacks: return to previous elements with animations

💥 VISUAL EXPLANATION DYNAMICS:
- Transform equations step-by-step with intermediate states visible
- Use animated graphs that draw themselves progressively
- Create moving diagrams that demonstrate concepts in action
- Implement split-screen comparisons with synchronized animations
- Use object multiplication: show one object becoming many
- Create animated timelines: show progression of ideas over time
- Use perspective shifts: rotate 2D diagrams to show 3D relationships
- Implement animated analogies: transform familiar objects into mathematical concepts
- Create visual stories: sequences of scenes that build understanding
- Use animated emphasis: zoom, highlight, circle key elements temporarily
- Implement interactive-style reveals: as if responding to questions
- Create animated proofs: visual demonstrations that prove mathematical statements

🎨 VISUAL VARIETY REQUIREMENTS:
- Use different font sizes: font_size=48 for titles, 36 for subtitles, 24 for content
- Use colors: BLUE for titles, WHITE for content, YELLOW for emphasis
- Create diagrams with Circle(), Rectangle(), Line() objects
- Position diagrams LEFT and text RIGHT, or vice versa
- Use arrows (Arrow()) to connect related concepts
- Create mathematical plots with axes when relevant

🎨 ENHANCED VISUAL LAYOUT SYSTEM:
- Implement 3-column layout: LEFT (-4 to -2), ORIGIN (-1 to 1), RIGHT (2 to 4)
- Use 5-row system: TOP (Y=3), UPPER (Y=1.5), MIDDLE (Y=0), LOWER (Y=-1.5), BOTTOM (Y=-3)
- Create visual zones: Title zone (Y=2.5 to 3.5), Content zone (Y=-2 to 2), Footer zone (Y=-3 to -2)
- Use asymmetric layouts: 60% content area, 40% visual area for better balance
- Implement dynamic layouts that change during animation
- Create visual breathing room: minimum 0.5 unit spacing between text elements
- Use strategic white space: don't fill every pixel, leave empty areas for visual rest
- Scale elements responsively: larger diagrams get .scale(0.8), smaller text gets font_size=20
- Create visual hierarchy through size, color, and position combinations
- Use consistent margin system: 0.5 units from screen edges for all content

🎯 POSITIONING COORDINATION SYSTEM:
- Before placing any object, check what's already on screen
- Use incremental positioning: if UP*2 is taken, use UP*2.5 or UP*1.5
- Implement content zones: never place title text in diagram zone
- Create movement corridors: paths for objects to enter/exit without collision
- Use depth layering: background elements, main content, highlighting overlays
- Implement position memory: track where each object has been placed
- Use relative positioning: new_obj.next_to(existing_obj, direction=RIGHT, buff=0.5)
- Create position validation: ensure no object extends beyond screen boundaries
- Use smart scaling: automatically reduce font_size if text doesn't fit in allocated space
- Implement collision detection: check for overlap before finalizing positions

⚠️ CRITICAL MANIM POSITIONING CONSTANTS AND LAYOUT SYSTEM:
- ORIGIN: Center point [0, 0, 0] - primary reference for all positioning
- CARDINAL DIRECTIONS: UP, DOWN, LEFT, RIGHT (never use CENTER, MIDDLE, TOP, BOTTOM)
- DIAGONAL CONSTANTS: UL, UR, DL, DR for corner positioning
- STANDARD MULTIPLIERS: Use increments of 0.5 (UP*1.5, LEFT*2.5, etc.)
- SAFE POSITIONING ZONES:
  * TITLE_ZONE: Y=2.5 to Y=3.5, X=-5 to X=5 (main headings)
  * SUBTITLE_ZONE: Y=1.5 to Y=2.4, X=-5 to X=5 (section headers)
  * CONTENT_ZONE: Y=-1.5 to Y=1.4, X=-6 to X=6 (main content)
  * FOOTER_ZONE: Y=-2.5 to Y=-1.6, X=-5 to X=5 (summaries, notes)
  * MARGIN_BUFFER: 0.3 units minimum from zone boundaries
- LAYOUT TEMPLATES:
  * SINGLE_COLUMN: Content centered, X=-1 to X=1
  * TWO_COLUMN: Left X=-4 to X=-1, Right X=1 to X=4
  * THREE_COLUMN: Left X=-5 to X=-2, Center X=-1.5 to X=1.5, Right X=2 to X=5
  * DIAGRAM_TEXT: Diagram LEFT (X=-4 to X=-1), Text RIGHT (X=1 to X=4)
- MATHEMATICAL POSITIONING:
  * EQUATION_CENTER: Y=0, X=0 for main equations
  * EQUATION_TOP: Y=2, X=0 for title equations
  * VARIABLE_ZONES: Distribute variables at Y=1, Y=0, Y=-1 with X spacing
  * AXIS_PLACEMENT: Standard coordinate systems at ORIGIN with appropriate scaling
- ANIMATION ANCHORS:
  * ENTRY_POINTS: Objects start at screen edges (X=±8, Y=±5) before animating in
  * EXIT_POINTS: Objects move to screen edges before FadeOut
  * TRANSITION_HUBS: Temporary positions during complex movements
- RESPONSIVE POSITIONING:
  * AUTO_SCALE: If object width > 10 units, scale to fit: obj.scale(10/obj.get_width())
  * OVERFLOW_HANDLING: Split long text into multiple lines rather than extend bounds
  * DYNAMIC_SPACING: Adjust spacing based on number of objects in scene
- POSITIONING VALIDATION:
  * PRE_PLACEMENT_CHECK: Verify coordinates within safe zones before animation
  * COLLISION_DETECTION: Check for overlap with existing objects
  * BOUNDS_VERIFICATION: Ensure all objects remain within 16:9 aspect ratio limits

⚠️ NEVER USE THESE (they don't exist in Manim):
- CENTER (use ORIGIN instead)
- MIDDLE (use ORIGIN instead)
- TOP (use UP*3 instead)
- BOTTOM (use DOWN*3 instead)

📚 PROFESSIONAL MANIM EXAMPLES GALLERY:
Study these high-quality examples for code patterns and techniques:

Example 1: BraceAnnotation - Annotating geometric elements
```python
from manim import *

class BraceAnnotation(Scene):
    def construct(self):
        dot = Dot([-2, -1, 0])
        dot2 = Dot([2, 1, 0])
        line = Line(dot.get_center(), dot2.get_center()).set_color(ORANGE)
        b1 = Brace(line)
        b1text = b1.get_text("Horizontal distance")
        b2 = Brace(line, direction=line.copy().rotate(PI / 2).get_unit_vector())
        b2text = b2.get_tex("x-x_1")
        self.add(line, dot, dot2, b1, b2, b1text, b2text)
```

Example 2: VectorArrow - Coordinate system visualization
```python
from manim import *

class VectorArrow(Scene):
    def construct(self):
        dot = Dot(ORIGIN)
        arrow = Arrow(ORIGIN, [2, 2, 0], buff=0)
        numberplane = NumberPlane()
        origin_text = Text('(0, 0)').next_to(dot, DOWN)
        tip_text = Text('(2, 2)').next_to(arrow.get_end(), RIGHT)
        self.add(numberplane, dot, arrow, origin_text, tip_text)
```

Example 3: BooleanOperations - Interactive shape operations
```python
from manim import *

class BooleanOperations(Scene):
    def construct(self):
        ellipse1 = Ellipse(
            width=4.0, height=5.0, fill_opacity=0.5, color=BLUE, stroke_width=10
        ).move_to(LEFT)
        ellipse2 = ellipse1.copy().set_color(color=RED).move_to(RIGHT)
        bool_ops_text = MarkupText("<u>Boolean Operation</u>").next_to(ellipse1, UP * 3)
        ellipse_group = Group(bool_ops_text, ellipse1, ellipse2).move_to(LEFT * 3)
        self.play(FadeIn(ellipse_group))

        i = Intersection(ellipse1, ellipse2, color=GREEN, fill_opacity=0.5)
        self.play(i.animate.scale(0.25).move_to(RIGHT * 5 + UP * 2.5))
        intersection_text = Text("Intersection", font_size=23).next_to(i, UP)
        self.play(FadeIn(intersection_text))

        u = Union(ellipse1, ellipse2, color=ORANGE, fill_opacity=0.5)
        union_text = Text("Union", font_size=23)
        self.play(u.animate.scale(0.3).next_to(i, DOWN, buff=union_text.height * 3))
        union_text.next_to(u, UP)
        self.play(FadeIn(union_text))
```

Example 4: PointMovingOnShapes - Path animations and transformations
```python
from manim import *

class PointMovingOnShapes(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        dot = Dot()
        dot2 = dot.copy().shift(RIGHT)
        self.add(dot)

        line = Line([3, 0, 0], [5, 0, 0])
        self.add(line)

        self.play(GrowFromCenter(circle))
        self.play(Transform(dot, dot2))
        self.play(MoveAlongPath(dot, circle), run_time=2, rate_func=linear)
        self.play(Rotating(dot, about_point=[2, 0, 0]), run_time=1.5)
        self.wait()
```

Example 5: MovingAround - Object transformations with animate
```python
from manim import *

class MovingAround(Scene):
    def construct(self):
        square = Square(color=BLUE, fill_opacity=1)

        self.play(square.animate.shift(LEFT))
        self.play(square.animate.set_fill(ORANGE))
        self.play(square.animate.scale(0.3))
        self.play(square.animate.rotate(0.4))
```

Example 6: MovingAngle - Dynamic angle measurement with updaters
```python
from manim import *

class MovingAngle(Scene):
    def construct(self):
        rotation_center = LEFT

        theta_tracker = ValueTracker(110)
        line1 = Line(LEFT, RIGHT)
        line_moving = Line(LEFT, RIGHT)
        line_ref = line_moving.copy()
        line_moving.rotate(
            theta_tracker.get_value() * DEGREES, about_point=rotation_center
        )
        a = Angle(line1, line_moving, radius=0.5, other_angle=False)
        tex = MathTex(r"\theta").move_to(
            Angle(
                line1, line_moving, radius=0.5 + 3 * SMALL_BUFF, other_angle=False
            ).point_from_proportion(0.5)
        )

        self.add(line1, line_moving, a, tex)
        self.wait()

        line_moving.add_updater(
            lambda x: x.become(line_ref.copy()).rotate(
                theta_tracker.get_value() * DEGREES, about_point=rotation_center
            )
        )

        a.add_updater(
            lambda x: x.become(Angle(line1, line_moving, radius=0.5, other_angle=False))
        )
        tex.add_updater(
            lambda x: x.move_to(
                Angle(
                    line1, line_moving, radius=0.5 + 3 * SMALL_BUFF, other_angle=False
                ).point_from_proportion(0.5)
            )
        )

        self.play(theta_tracker.animate.set_value(40))
        self.play(theta_tracker.animate.increment_value(140))
        self.play(tex.animate.set_color(RED), run_time=0.5)
        self.play(theta_tracker.animate.set_value(350))
```

Example 7: MovingDots - Connected objects with updaters
```python
from manim import *

class MovingDots(Scene):
    def construct(self):
        d1,d2=Dot(color=BLUE),Dot(color=GREEN)
        dg=VGroup(d1,d2).arrange(RIGHT,buff=1)
        l1=Line(d1.get_center(),d2.get_center()).set_color(RED)
        x=ValueTracker(0)
        y=ValueTracker(0)
        d1.add_updater(lambda z: z.set_x(x.get_value()))
        d2.add_updater(lambda z: z.set_y(y.get_value()))
        l1.add_updater(lambda z: z.become(Line(d1.get_center(),d2.get_center())))
        self.add(d1,d2,l1)
        self.play(x.animate.set_value(5))
        self.play(y.animate.set_value(4))
        self.wait()
```

Example 8: MovingFrameBox - Highlighting mathematical expressions
```python
from manim import *

class MovingFrameBox(Scene):
    def construct(self):
        self.play(Write(text))
        framebox1 = SurroundingRectangle(text[1], buff = .1)
        framebox2 = SurroundingRectangle(text[3], buff = .1)
        self.play(Create(framebox1))
        self.wait()
        self.play(ReplacementTransform(framebox1,framebox2))
        self.wait()
```

Example 9: SinAndCosFunctionPlot - Mathematical function plotting
```python
from manim import *

class SinAndCosFunctionPlot(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-10, 10.3, 1],
            y_range=[-1.5, 1.5, 1],
            x_length=10,
            axis_config={"color": GREEN},
            x_axis_config={
                "numbers_to_include": np.arange(-10, 10.01, 2),
                "numbers_with_elongated_ticks": np.arange(-10, 10.01, 2),
            },
            tips=False,
        )
        axes_labels = axes.get_axis_labels()
        sin_graph = axes.plot(lambda x: np.sin(x), color=BLUE)
        cos_graph = axes.plot(lambda x: np.cos(x), color=RED)

        sin_label = axes.get_graph_label(
            sin_graph, "\\sin(x)", x_val=-10, direction=UP / 2
        )
        cos_label = axes.get_graph_label(cos_graph, label="\\cos(x)")

        vert_line = axes.get_vertical_line(
            axes.i2gp(TAU, cos_graph), color=YELLOW, line_func=Line
        )
        line_label = axes.get_graph_label(
            cos_graph, r"x=2\pi", x_val=TAU, direction=UR, color=WHITE
        )

        plot = VGroup(axes, sin_graph, cos_graph, vert_line)
        labels = VGroup(axes_labels, sin_label, cos_label, line_label)
        self.add(plot, labels)
```

Example 10: ArgMinExample - Interactive optimization visualization
```python
from manim import *

class ArgMinExample(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 10], y_range=[0, 100, 10], axis_config={"include_tip": False}
        )
        labels = ax.get_axis_labels(x_label="x", y_label="f(x)")

        t = ValueTracker(0)

        def func(x):
            return 2 * (x - 5) ** 2
        graph = ax.plot(func, color=MAROON)

        initial_point = [ax.coords_to_point(t.get_value(), func(t.get_value()))]
        dot = Dot(point=initial_point)

        dot.add_updater(lambda x: x.move_to(ax.c2p(t.get_value(), func(t.get_value()))))
        x_space = np.linspace(*ax.x_range[:2],200)
        minimum_index = func(x_space).argmin()

        self.add(ax, labels, graph, dot)
        self.play(t.animate.set_value(x_space[minimum_index]))
        self.wait()
```

Example 11: GraphAreaPlot - Area under curves and Riemann rectangles
```python
from manim import *

class GraphAreaPlot(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 5],
            y_range=[0, 6],
            x_axis_config={"numbers_to_include": [2, 3]},
            tips=False,
        )

        labels = ax.get_axis_labels()

        curve_1 = ax.plot(lambda x: 4 * x - x ** 2, x_range=[0, 4], color=BLUE_C)
        curve_2 = ax.plot(
            lambda x: 0.8 * x ** 2 - 3 * x + 4,
            x_range=[0, 4],
            color=GREEN_B,
        )

        line_1 = ax.get_vertical_line(ax.input_to_graph_point(2, curve_1), color=YELLOW)
        line_2 = ax.get_vertical_line(ax.i2gp(3, curve_1), color=YELLOW)

        riemann_area = ax.get_riemann_rectangles(curve_1, x_range=[0.3, 0.6], dx=0.03, color=BLUE, fill_opacity=0.5)
        area = ax.get_area(curve_2, [2, 3], bounded_graph=curve_1, color=GREY, opacity=0.5)

        self.add(ax, labels, curve_1, curve_2, line_1, line_2, riemann_area, area)
```

Example 12: PolygonOnAxes - Dynamic polygon areas with value tracking
```python
from manim import *

class PolygonOnAxes(Scene):
    def get_rectangle_corners(self, bottom_left, top_right):
        return [
            (top_right[0], top_right[1]),
            (bottom_left[0], top_right[1]),
            (bottom_left[0], bottom_left[1]),
            (top_right[0], bottom_left[1]),
        ]

    def construct(self):
        ax = Axes(
            x_range=[0, 10],
            y_range=[0, 10],
            x_length=6,
            y_length=6,
            axis_config={"include_tip": False},
        )

        t = ValueTracker(5)
        k = 25

        graph = ax.plot(
            lambda x: k / x,
            color=YELLOW_D,
            x_range=[k / 10, 10.0, 0.01],
            use_smoothing=False,
        )

        def get_rectangle():
            polygon = Polygon(
                *[
                    ax.c2p(*i)
                    for i in self.get_rectangle_corners(
                        (0, 0), (t.get_value(), k / t.get_value())
                    )
                ]
            )
            polygon.stroke_width = 1
            polygon.set_fill(BLUE, opacity=0.5)
            polygon.set_stroke(YELLOW_B)
            return polygon

        polygon = always_redraw(get_rectangle)

        dot = Dot()
        dot.add_updater(lambda x: x.move_to(ax.c2p(t.get_value(), k / t.get_value())))
        dot.set_z_index(10)

        self.add(ax, graph, dot)
        self.play(Create(polygon))
        self.play(t.animate.set_value(10))
        self.play(t.animate.set_value(k / 10))
        self.play(t.animate.set_value(5))
```

Example 13: HeatDiagramPlot - Scientific data visualization
```python
from manim import *

class HeatDiagramPlot(Scene):
    def construct(self):
        ax = Axes(
            x_range=[0, 40, 5],
            y_range=[-8, 32, 5],
            x_length=9,
            y_length=6,
            x_axis_config={"numbers_to_include": np.arange(0, 40, 5)},
            y_axis_config={"numbers_to_include": np.arange(-5, 34, 5)},
            tips=False,
        )
        labels = ax.get_axis_labels(
            x_label=Tex(r"$\Delta Q$"), y_label=Tex(r"T[$^\circ C$]")
        )

        x_vals = [0, 8, 38, 39]
        y_vals = [20, 0, 0, -5]
        graph = ax.plot_line_graph(x_values=x_vals, y_values=y_vals)

        self.add(ax, labels, graph)
```

Example 14: FollowingGraphCamera - Advanced camera movements
```python
from manim import *

class FollowingGraphCamera(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()

        # create the axes and the curve
        ax = Axes(x_range=[-1, 10], y_range=[-1, 10])
        graph = ax.plot(lambda x: np.sin(x), color=BLUE, x_range=[0, 3 * PI])

        # create dots based on the graph
        moving_dot = Dot(ax.i2gp(graph.t_min, graph), color=ORANGE)
        dot_1 = Dot(ax.i2gp(graph.t_min, graph))
        dot_2 = Dot(ax.i2gp(graph.t_max, graph))

        self.add(ax, graph, dot_1, dot_2, moving_dot)
        self.play(self.camera.frame.animate.scale(0.5).move_to(moving_dot))

        def update_curve(mob):
            mob.move_to(moving_dot.get_center())

        self.camera.frame.add_updater(update_curve)
        self.play(MoveAlongPath(moving_dot, graph, rate_func=linear))
        self.camera.frame.remove_updater(update_curve)

        self.play(Restore(self.camera.frame))
```

Example 15: ThreeDSurfacePlot - 3D mathematical surfaces
```python
from manim import *

class ThreeDSurfacePlot(ThreeDScene):
    def construct(self):
        resolution_fa = 24
        self.set_camera_orientation(phi=75 * DEGREES, theta=-30 * DEGREES)

        def param_gauss(u, v):
            x = u
            y = v
            sigma, mu = 0.4, [0.0, 0.0]
            d = np.linalg.norm(np.array([x - mu[0], y - mu[1]]))
            z = np.exp(-(d ** 2 / (2.0 * sigma ** 2)))
            return np.array([x, y, z])

        gauss_plane = Surface(
            param_gauss,
            resolution=(resolution_fa, resolution_fa),
            v_range=[-2, +2],
            u_range=[-2, +2]
        )

        gauss_plane.scale(2, about_point=ORIGIN)
        gauss_plane.set_style(fill_opacity=1,stroke_color=GREEN)
        gauss_plane.set_fill_by_checkerboard(ORANGE, BLUE, opacity=0.5)
        axes = ThreeDAxes()
        self.add(axes,gauss_plane)
```

🎓 REAL MANIM ANIMATION INSPIRATION GUIDANCE:

Study these examples to understand how REAL Manim animations are constructed:

🔥 PROFESSIONAL ANIMATION PATTERNS:
1. **Unit Circle to Sine Wave Connection (Example 16)**: Shows how mathematical concepts are visually connected through animated relationships. The moving dot creates the sine curve in real-time, demonstrating the fundamental connection between circular motion and trigonometric functions.

2. **LaTeX Integration and Grid Transformations (Example 17)**: Demonstrates sophisticated text handling with LaTeX, smooth transitions between concepts, and advanced grid manipulations. Shows how to create engaging mathematical content with proper staging.

3. **3D Scene Management (Example 18)**: Illustrates how to handle 3D scenes with camera controls, rotation effects, and depth perception. Essential for advanced mathematical visualizations.

🎯 KEY PROFESSIONAL TECHNIQUES TO EMULATE:

**Dynamic Curve Generation**: Like SineCurveUnitCircle, create curves that build over time using updaters and always_redraw(). This technique is perfect for showing how mathematical relationships develop.

**Multi-Stage Scene Flow**: Like OpeningManim, structure animations in distinct phases with clear transitions. Use Transform() to evolve concepts and FadeOut() to clear space for new ideas.
**Custom Updater Functions**: Implement sophisticated updater patterns that respond to changing values. Use lambda functions and class methods to create responsive animations.
**Mathematical Storytelling**: Connect abstract concepts to visual representations. Show the "why" and "how" behind mathematical relationships through animated demonstrations.
**Progressive Complexity Building**: Start with simple elements and gradually add complexity. Transform basic shapes into complex mathematical objects through smooth animations.
**Real-Time Curve Drawing**: Use VGroup() and line additions to create curves that draw themselves. Perfect for showing function behavior and mathematical relationships.
**Advanced Positioning Systems**: Use custom coordinate systems and relative positioning. Create your own reference points and build layouts around them.
**Smooth Transition Management**: Master the art of clearing scenes and introducing new content without jarring jumps. Use fadeouts, transformations, and staged reveals.

🎨 VISUAL STORYTELLING PRINCIPLES FROM EXAMPLES:

**Cause and Effect Demonstration**: Show how one mathematical element affects another through connected animations. The unit circle example perfectly demonstrates this.
**Progressive Disclosure**: Reveal mathematical complexity gradually. Don't overwhelm with too much information at once.
**Visual Metaphor Integration**: Use familiar geometric shapes to represent abstract concepts, then transform them to show mathematical relationships.
**Interactive-Style Responsiveness**: Create animations that feel like they're responding to an instructor's explanation. Use pauses, emphasis, and callbacks effectively.
**Mathematical Proof Through Animation**: Use visual demonstrations to prove mathematical statements. Show rather than just tell.

🎓 KEY PATTERNS FROM ALL EXAMPLES:
- Use ValueTracker() for dynamic values that change over time
- Implement .add_updater() for objects that need to update automatically  
- Use always_redraw() for objects that need constant redrawing
- Combine VGroup() to manage multiple related objects
- Apply .animate for smooth transformations
- Use proper positioning with .next_to(), .move_to(), .shift()
- Create custom functions for complex mathematical visualizations
- Use axes.plot() for mathematical functions and axes.get_area() for regions
- Implement SurroundingRectangle() for highlighting elements
- Use MathTex() for mathematical expressions and Text() for regular text
- Apply proper color schemes and opacity for visual clarity
- Use .set_z_index() to control layering of objects
- Master custom updater functions for real-time curve generation
- Use multi-stage scene management with clear transitions
- Implement progressive complexity building through transformations
- Create mathematical storytelling through connected visual elements
- Use 3D scene management for advanced visualizations
- Apply non-linear transformations to demonstrate mathematical concepts
- Implement real-time drawing techniques for dynamic mathematical relationships
- Use LaTeX integration for professional mathematical notation
- Create custom coordinate systems and positioning frameworks
- Master smooth transition management between complex scenes

💡 INSPIRATION FOR YOUR ANIMATIONS:
Draw inspiration from these professional examples to create animations that:
- Build mathematical intuition through visual connections
- Use sophisticated animation techniques like real-time curve generation
- Create smooth, professional transitions between concepts
- Integrate multiple mathematical elements into cohesive visual stories
- Use advanced positioning and layout systems for optimal presentation
- Implement progressive complexity that guides understanding
- Create memorable visual metaphors that reinforce learning
- Use interactive-style pacing that feels responsive and engaging

EDUCATIONAL STEPS TO IMPLEMENT:"""]
        
        # Add detailed information about each educational step
        for i, step in enumerate(steps, 1):
            step_title = step.get('step_title', 'Step {}'.format(i))
            prompt_parts.append("""

Step {step_num}: {step_title}
- Duration: {duration} seconds
- Key Concepts: {key_concepts}
- Narration: {narration}
- Visual Plan: {visual_plan}
- Visual Elements: {visual_elements}
- Equations: {equations}
- Real-world Examples: {examples}""".format(
                step_num=i,
                step_title=step_title,
                duration=step.get('duration_seconds', 30),
                key_concepts=', '.join(step.get('key_concepts', [])),
                narration=step.get('narration_script', ''),
                visual_plan=step.get('animation_plan', ''),
                visual_elements=step.get('visual_elements', {}),
                equations=step.get('equations', []),
                examples=step.get('real_world_examples', [])
            ))

        # Create class name safely outside f-string
        class_name = title.replace(' ', '').replace(':', '').replace('(', '').replace(')', '').replace('-', '').replace("'", "").replace('"', '')
        if not class_name:
            class_name = "Educational"
        
        complexity = educational_breakdown.get('metadata', {}).get('difficulty_progression', 'intermediate')
        prompt_parts.append("""

TOTAL DURATION: {duration} seconds
TARGET COMPLEXITY: {complexity}

OUTPUT FORMAT:
Provide complete, executable Manim Python code following this structure:
🎯 MANDATORY 4-SCENE TEMPLATE SYSTEM FOR OVERLAP PREVENTION:
IN INTRODUCTION: PLS USE BRANDING "LearnVidAI" IN intro_scene AND outro_scene.                            
You MUST structure your animation using these 4 scene templates:

═══════════════════════════════════════════════════════════════
📐 TEMPLATE USAGE RULES:
═══════════════════════════════════════════════════════════════

**TEMPLATE A - INTRO SCENE:**
```python
self.intro_scene(
    title_text="Main Topic Title",
    desc_text="Brief description of what we'll learn",
    branding="LearnVidAI"
)
self.clean_transition()
```
- Fixed positions: Title(UP*2.0), Desc(UP*0.5), Brand(DOWN*1.5)
- Use at start of video
- ALWAYS call clean_transition() after

**TEMPLATE B - GRAPH SCENE:**
```python
footer = self.graph_scene(
    title_text="Graph Title",
    graph_function=lambda x: x**2,  # Your function here
    x_range=[-3, 3, 1],
    y_range=[-2, 8, 2],
    footer_text="Initial equation or caption",
    graph_color=BLUE
)
# Optional: Update footer without overlap
self.update_graph_footer("Updated equation or insight")
self.clean_transition()
```
- Fixed positions: Title(UP*3.0), Graph(center), Footer(DOWN*2.5)
- Use for visual/mathematical content
- Footer can transform in-place via update_graph_footer()
- ALWAYS call clean_transition() after (unless updating footer)

**TEMPLATE C - EXPLANATION SCENE:**
```python
self.explanation_scene(
    title_text="Concept Being Explained",
    explanation_lines=[
        "• First key point about the concept",
        "• Second important detail",
        "• Third supporting fact",
        "• Fourth application or example"
    ],
    key_insight="Main takeaway in one sentence!"
)
self.clean_transition()
```
- Fixed positions: Title(UP*3.0), Lines(1.5, 0.5, -0.5, -1.5), Insight(DOWN*2.5)
- Max 4 explanation lines + 1 key insight
- Use to explain concepts shown in graphs
- ALWAYS call clean_transition() after

**TEMPLATE D - OUTRO SCENE:**
```python
self.outro_scene(
    title_text="Summary or Conclusion",
    desc_text="Final thoughts or call to action",
    branding="LearnVidAI"
)
```
- Same as intro_scene (reuses Template A)
- Use at end of video
- No clean_transition needed (end of video)

═══════════════════════════════════════════════════════════════
🔄 REQUIRED VIDEO FLOW PATTERN:
═══════════════════════════════════════════════════════════════

Your construct() method MUST follow this pattern:
```python
def construct(self):
    # 1. INTRO
    self.intro_scene("Title", "Description", "LearnVidAI")
    self.clean_transition()
    
    # 2. GRAPH (First concept)
    self.graph_scene("Concept 1", lambda x: x**2, footer_text="Equation")
    self.clean_transition()
    
    # 3. EXPLANATION (Explain the graph)
    self.explanation_scene("Concept 1", [
        "• Point 1",
        "• Point 2",
        "• Point 3"
    ], "Key insight!")
    self.clean_transition()
    
    # 4. GRAPH (Second concept - optional)
    self.graph_scene("Concept 2", lambda x: 2*x, footer_text="Linear")
    self.clean_transition()
    
    # 5. EXPLANATION (Explain second graph)
    self.explanation_scene("Concept 2", [
        "• Point 1",
        "• Point 2"
    ])
    self.clean_transition()
    
    # 6. OUTRO
    self.outro_scene("Summary", "What we learned", "LearnVidAI")
```

═══════════════════════════════════════════════════════════════
⚠️ CRITICAL RULES - MUST FOLLOW:
═══════════════════════════════════════════════════════════════

1. NEVER create Text objects outside these templates
2. ALWAYS call clean_transition() between templates (except before outro)
3. DO NOT modify template positioning (positions are fixed)
4. USE update_graph_footer() to change footer text, NOT new Text objects
5. MAXIMUM 4 explanation lines per explanation_scene
6. DO NOT add custom methods that create text at arbitrary positions
7. ALL text content must go through one of the 4 templates

═══════════════════════════════════════════════════════════════
✅ BENEFITS OF THIS SYSTEM:
═══════════════════════════════════════════════════════════════

- Zero overlap guaranteed (fixed positions)
- Clean visual flow (mandatory transitions)
- Consistent layout (predictable for viewers)
- Easy to understand (template-based)
- Maintainable (modify templates, not individual scenes)

═══════════════════════════════════════════════════════════════
🎬 EXAMPLE USAGE FOR EDUCATIONAL STEPS:
═══════════════════════════════════════════════════════════════

For each educational step in the video plan:

Step 1 (Introduction):
- Use intro_scene with step title and overview

Step 2-N (Core Content):
- Use graph_scene if visual/mathematical content
- Follow immediately with explanation_scene to explain the graph
- Repeat graph → explanation cycle for each major concept

Final Step:
- Use outro_scene to summarize all concepts

```python
from manim import *

class {class_name}Scene(Scene):
    def construct(self):""".format(duration=duration, complexity=complexity, class_name=class_name) + """
        # Main orchestration method - CLEAR between each step
        self.intro_sequence()
        self.clear_and_transition()
        self.step_1_introduction()
        self.clear_and_transition()
        self.step_2_core_concepts()
        self.clear_and_transition()
        # ... more steps as needed
        self.conclusion_summary()
    
    def clear_and_transition(self):
        # Clean transition between sections
        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)
    
    def intro_sequence(self):
        # Engaging introduction with DYNAMIC positioning
        title = Text("{{title}}", font_size=48, color=BLUE).shift(UP*3)
        subtitle = Text("Educational Animation", font_size=32, color=WHITE).shift(UP*1.5)
        
        self.play(Write(title))
        self.wait(0.5)
        self.play(Write(subtitle))
        self.wait(1)
        
        # Move content and add more
        self.play(
            title.animate.shift(LEFT*3).scale(0.7),
            subtitle.animate.shift(RIGHT*3).scale(0.8)
        )
        
        intro_text = Text("Let's explore this concept step by step", 
                          font_size=24, color=YELLOW).shift(DOWN*1)
        self.play(FadeIn(intro_text))
        self.wait(2)
        
    def step_1_introduction(self):
        # First educational step - NEW positions, no overlap
        step_title = Text("Step 1: Foundation", font_size=40, color=BLUE).shift(UP*2.5)
        self.play(Write(step_title))
        
        # Create diagram on LEFT, text on RIGHT
        diagram = Circle(radius=1, color=WHITE).shift(LEFT*3)
        explanation = Text("Key concept explanation\\nwith multiple lines", 
                          font_size=20, color=WHITE).shift(RIGHT*2)
        
        self.play(Create(diagram), Write(explanation))
        self.wait(1)
        
        # Transform and move
        new_shape = Square(side_length=2, color=YELLOW).shift(LEFT*3)
        self.play(Transform(diagram, new_shape))
        
        # Add connecting arrow
        arrow = Arrow(LEFT*1, RIGHT*0.5, color=GREEN)
        self.play(Create(arrow))
        self.wait(2)
        
    # CONTINUE with similar patterns for each step...
```

CRITICAL REQUIREMENTS:
Please do not use 'CYAN': NameError: name 'CYAN' is not defined
1. Generate COMPLETE, EXECUTABLE code
2. Include ALL necessary imports
3. Follow proper Manim syntax and conventions
4. Create visually appealing, educational animations
5. Ensure smooth flow between all steps
6. Use dynamic positioning - avoid static layouts
7. Include proper documentation and comments
8. Make the code modular and easy to understand
9. Optimize for visual clarity and educational impact
10. Follow the educational step progression exactly
11. Must Contain all necessary imports and class definitions
12. def construct() method must orchestrate the entire scene flow
13. ⚠️ NEVER use ImageMobject or image file references ⚠️
14. Use only built-in Manim objects (Text, MathTex, shapes, etc.)
15. Create visual representations using geometric shapes and text
16. Represent real-world examples with descriptive text and shape-based diagrams
17. ANIMATE EVERYTHING - no static content allowed
18. Use self.clear() or FadeOut(*self.mobjects) between major sections
19. Move objects around the screen dynamically with .animate.shift()
20. Transform objects instead of creating new ones in same position
21. Use proper spacing - NEVER overlap text at same coordinates
22. Implement smooth transitions between concepts
23. Create engaging visual flow with object movements
24. ONLY use valid Scene methods: self.add(), self.play(), self.wait(), self.clear(), self.remove()
25. NEVER use self.set_background() or similar invalid methods
26. ALWAYS position objects at different coordinates using UP*2, DOWN*1, LEFT*3, RIGHT*2
27. Clear screen between sections: self.play(FadeOut(*self.mobjects))
28. Use different font sizes to create hierarchy: 48 for titles, 36 for subtitles, 24 for content

🎯 16:9 ASPECT RATIO CRITICAL REQUIREMENTS:
29. NEVER position objects beyond X=±6.5 or Y=±3.8 (safe viewing area)
30. Use responsive scaling: if text doesn't fit, reduce font_size, don't extend bounds
31. Test all positions: title.shift(UP*3.5) should be maximum upward positioning
32. Implement automatic bounds checking for all object placements
33. Use .get_width() and .get_height() to verify objects fit within screen
34. Scale down oversized objects: if obj.get_width() > 12, use obj.scale(12/obj.get_width())
35. Use multi-line text for long content instead of tiny fonts or overflow
36. Position wide equations at Y=0 (screen center) for maximum horizontal space
37. Create responsive layouts that adapt to content size automatically

🚫 OVERLAP PREVENTION CRITICAL REQUIREMENTS:
38. MANDATORY position tracking: maintain mental map of used screen areas
39. Use position validation: before placing object, verify area is clear
40. Implement smart positioning: if preferred position occupied, find nearest free space
41. Create position buffers: minimum 0.3 units between adjacent text objects
42. Use staged clearing: remove specific objects before adding new ones in same area
43. Implement position queuing: queue objects that will move to make space for new content
44. Use relative positioning chains: obj2.next_to(obj1, RIGHT).shift(DOWN*0.5)
45. Create temporary positioning: place objects off-screen, then animate to final position
46. Use position debugging: add brief pauses to verify no overlaps before proceeding
47. Implement content flow management: ensure logical movement paths don't cause collisions

💫 DYNAMIC VISUAL EXPLANATION CRITICAL REQUIREMENTS:
48. Every abstract concept MUST have concrete visual representation
49. Use transformation chains: circle → square → triangle to show concept evolution
50. Implement visual analogies: familiar objects that morph into mathematical concepts
51. Create animated cause-and-effect demonstrations
52. Use progressive complexity: start with simple shapes, add details through animation
53. Implement interactive-style responses: animations that react to previous content
54. Create visual proof sequences: step-by-step animated demonstrations
55. Use multi-perspective views: show same concept from different visual angles
56. Implement concept journeys: objects that travel across screen to demonstrate relationships
57. Create animated timelines: show historical or logical progression of ideas

⚠️ CRITICAL SYNTAX REQUIREMENTS ⚠️:
- NEVER write Text("text",.shift() - comma before method is SYNTAX ERROR
- ALWAYS write Text("text").shift() - proper method chaining
- NEVER write Text("text").shift(UP*2 - missing closing parenthesis is SYNTAX ERROR  
- ALWAYS write Text("text").shift(UP*2) - complete parentheses
- NEVER split Text declarations across multiple lines
- ALWAYS complete Text objects on single lines
- NEVER create orphaned lines starting with font_size= or color=
- ALWAYS use proper 4-space indentation for class methods

⚠️ ERROR REPORTING AND DIAGNOSTIC INSTRUCTIONS:
Before generating any Manim code, internally validate the scene against the following rules. 
Only output code that passes all checks—never generate scenes that would trigger errors.
✅ MANDATORY PRE-GENERATION VALIDATION CHECKLIST:
1. Position Grid Compliance
- Use only these coordinates:
    - Y: UP*3 to DOWN*3 in 0.5-unit steps
    - X: integers from LEFT*5 (x = -5) to RIGHT*5 (x = +5)
- Every text object must have an explicit .shift(pos)
2. Overlap Prevention
- Minimum 0.8 units between any two text centers (Euclidean distance)
- Maximum 5 visible text objects at once
- If adding a new object exceeds limit, remove oldest before adding
3. Screen Bounds Enforcement
- All object centers must satisfy: -6 ≤ x ≤ 6, -3.5 ≤ y ≤ 3.5
- If content is too wide (>10 units), auto-scale:
```python
- Minimum 0.8 units between any two text centers (Euclidean distance)
- Maximum 5 visible text objects at once
- If adding a new object exceeds limit, remove oldest before adding
```
4. Readability Standards
- Titles: font_size ≥ 24
- Body text: font_size ≥ 18
- Text color: WHITE or BLACK only (high contrast)
5. Scene Hygiene
- Between major sections, clear non-persistent objects:
```python
to_remove = [m for m in self.mobjects if not getattr(m, 'is_persistent', False)]  
self.play(FadeOut(*to_remove))  
```
- Use explicit naming (e.g., title, equation_1) for traceability
🚫 NEVER generate code that violates these rules.
If a design would break a rule, adjust it silently (e.g., shift, scale, remove) and proceed.
Output format:
- Only the construct() method
- No comments, no markdown, no error messages
- No explanations—just clean, compliant Manim code

ANIMATION REQUIREMENTS:
- Every text element should be animated (Write, FadeIn, etc.)
- Use Transform() to morph objects between states
- Implement smooth camera movements when appropriate
- Clear previous content before introducing new concepts: self.play(FadeOut(*self.mobjects))
- Position elements strategically using UP, DOWN, LEFT, RIGHT with multipliers
- Use scale and rotation for visual interest: .scale(0.8), .rotate(PI/4)
- Implement highlighting effects (Indicate, Flash, Wiggle)
- Create progressive reveals for complex concepts
- Use color changes to show relationships: .set_color(BLUE)
- Implement step-by-step builds for equations and diagrams

MANDATORY POSITIONING EXAMPLES:
- Title: Text("Title", font_size=48).shift(UP*3)
- Subtitle: Text("Subtitle", font_size=36).shift(UP*1.5)  
- Content: Text("Content", font_size=24).shift(DOWN*1)
- Left diagram: Circle().shift(LEFT*4)
- Right text: Text("Explanation").shift(RIGHT*3)
- Multiple items: use UP*2, ORIGIN, DOWN*2 for vertical spacing
- NEVER put two Text objects in the same position
- ALWAYS move or remove old content before adding new content

📺 16:9 POSITIONING EXAMPLES (1920x1080 safe zones):
- Maximum title position: Text("Title").shift(UP*3.5) ✅
- Beyond safe zone: Text("Title").shift(UP*4.5) ❌ (will be cut off)
- Wide content max: Text("Long equation").shift(LEFT*6) ✅  
- Too wide: Text("Content").shift(LEFT*8) ❌ (extends beyond screen)
- Vertical content distribution:
  * Header zone: Y=3 to Y=2 (titles, section headers)
  * Main zone: Y=1.5 to Y=-1.5 (primary content, diagrams) 
  * Footer zone: Y=-2 to Y=-3.5 (conclusions, notes)
- Horizontal content distribution:
  * Left panel: X=-5 to X=-2 (diagrams, visual elements)
  * Center panel: X=-1.5 to X=1.5 (main text, equations)
  * Right panel: X=2 to X=5 (explanations, annotations)

🚫 OVERLAP PREVENTION EXAMPLES:
✅ CORRECT - Sequential positioning:
```python
title = Text("Title").shift(UP*3)
self.play(Write(title))
subtitle = Text("Subtitle").shift(UP*1.5)  # Different Y position
self.play(Write(subtitle))
```

❌ WRONG - Same position overlap:
```python
title = Text("Title", font_size=48).shift(UP * 3)
subtitle = Text("Subtitle", font_size=32).next_to(title, DOWN, buff=0.8)  # ✅ Safe spacing
```

✅ CORRECT - Clear before new content:
```python
self.play(FadeOut(title))  # Remove old content first
new_title = Text("New Title").shift(UP*3)
self.play(Write(new_title))
```

✅ CORRECT - Smart relative positioning:
```python
title = Text("Main Topic").shift(UP*2.5)
subtitle = Text("Subtopic").next_to(title, DOWN, buff=0.5)  # Auto-positioned
diagram = Circle().next_to(subtitle, DOWN*2, buff=1.0)      # Safe spacing
```

✅ CORRECT - Multi-column layout:
```python
left_text = Text("Concept A").shift(LEFT*4 + UP*1)
right_text = Text("Concept B").shift(RIGHT*4 + UP*1)     # Same Y, different X
center_arrow = Arrow(LEFT*1.5, RIGHT*1.5).shift(UP*1)    # Connects them
```

✅ CORRECT - Responsive scaling:
```python
long_equation = MathTex("Very long mathematical equation here")
if long_equation.get_width() > 10:  # Check if too wide
    long_equation.scale(10 / long_equation.get_width())  # Scale to fit
long_equation.shift(ORIGIN)  # Position in safe center area
```

💫 DYNAMIC VISUAL EXPLANATION EXAMPLES:
✅ CORRECT - Concept morphing:
```python
# Start with simple shape
circle = Circle(color=BLUE).shift(LEFT*3)
self.play(Create(circle))

# Transform to show relationship  
square = Square(color=RED).shift(LEFT*3)
self.play(Transform(circle, square))

# Add animated explanation
explanation = Text("Shapes can transform").shift(RIGHT*3)
arrow = Arrow(LEFT*1, RIGHT*1.5, color=YELLOW)
self.play(Write(explanation), Create(arrow))
```

✅ CORRECT - Progressive complexity:
```python
# Start simple
basic_formula = MathTex("a + b").shift(UP*2)
self.play(Write(basic_formula))

# Add complexity with animation
complex_formula = MathTex("a^2 + 2ab + b^2").shift(UP*2)
self.play(Transform(basic_formula, complex_formula))

# Show visual proof below
visual_squares = VGroup(
    Square().shift(LEFT*2 + DOWN*1),
    Rectangle(width=2, height=1).shift(DOWN*1),
    Square().shift(RIGHT*2 + DOWN*1)
).set_color(GREEN)
self.play(Create(visual_squares))
```

FORBIDDEN ELEMENTS:
- ImageMobject (will cause file not found errors)
- Any references to .png, .jpg, .jpeg, .gif files
- External image assets
- File loading operations
- self.set_background() method (AttributeError - doesn't exist)
- self.set_color_scheme() method (AttributeError - not valid)
- self.set_theme() method (AttributeError - not valid)
- self.configure_camera() method (AttributeError - not a Scene method)

VALID SCENE METHODS TO USE:
- self.add() - add objects to scene
- self.play() - animate objects
- self.wait() - pause between animations
- self.clear() - clear all objects from scene
- self.remove() - remove specific objects
- self.camera - access camera properties (read-only)

USE INSTEAD:
- Text() for descriptions and labels
- MathTex() for mathematical expressions
- Circle(), Rectangle(), Line() for diagrams
- Color-coded shapes to represent concepts
- Animated text reveals and transformations

Generate the complete Manim code now. Ensure it's production-ready and follows all the requirements above.

🎬 MANDATORY SCENE TIMING VALIDATION:
- Each scene method must include timing documentation: # Duration: X.X seconds
- Validate total scene time matches educational step allocation
- Include timing checkpoints: self.wait() statements with duration comments
- Implement progressive timing: faster for reviews, slower for new concepts
- Add scene transition buffers: minimum 1-second pause between major sections
- Use graduated complexity timing: simple=2s, moderate=4s, complex=6s per concept

🎯 STEP-BY-STEP IMPLEMENTATION REQUIREMENTS:
- Create sub-methods for each conceptual component
- Use method naming convention: step_X_part_Y_description()
- Implement concept scaffolding in method structure
- Add cross-references between related sub-steps
- Include understanding validation pauses between sub-steps
- Create modular methods for easy modification and debugging

💫 ANIMATION TECHNIQUE VALIDATION:
- Must use minimum 5 different animation types per scene
- Include at least 2 camera movements for scenes longer than 30 seconds
- Implement object morphing for abstract concept demonstrations
- Use layered animations: background, main content, emphasis overlays
- Include rhythmic pacing: alternate fast/slow animation sequences
- Apply consistent visual metaphors throughout educational progression

🎯 STEP-BY-STEP ANIMATION ENHANCEMENT REQUIREMENTS 🎯:

═══════════════════════════════════════════════════════════════
📚 DETAILED STEP ANIMATIONS WITH INTUITIONS AND EXPLANATIONS:
═══════════════════════════════════════════════════════════════

For EACH educational step, you MUST include:

1. 📝 CONCEPT INTRODUCTION:
- Start with a clear title that explains what we're learning
- Use Write() animation for the title with appropriate timing
- Include a brief subtitle explaining the intuition behind the concept
- Example: "Understanding Derivatives: The Rate of Change"

2. 🔍 VISUAL INTUITION BUILDING:
- Create concrete visual analogies before abstract concepts
- Use familiar shapes and objects that transform into mathematical concepts
- Implement step-by-step visual progression from simple to complex
- Example: Show a moving car (rectangle) → speed visualization → derivative concept

3. 💡 DETAILED EXPLANATIONS:
- Break down complex concepts into 3-5 smaller sub-concepts
- For each sub-concept, create a dedicated animation sequence
- Use explanatory text that appears with Write() or FadeIn()
- Include "why this matters" context for each step
- Example: "Why do we need limits? Because we want to find exact rates of change!"

4. 🎨 PROGRESSIVE VISUAL COMPLEXITY:
- Level 1: Simple shapes and basic movements
- Level 2: Add labels, equations, and relationships
- Level 3: Show interactions and transformations
- Level 4: Connect to real-world applications
- Use Transform() to morph objects between complexity levels

5. 🔄 INTERACTIVE-STYLE DEMONSTRATIONS:
- Create "What if?" scenarios with animated responses
- Show cause-and-effect relationships through animation
- Use highlighting (Indicate(), Flash()) to draw attention
- Implement before/after comparisons with side-by-side animations

6. 📊 STEP-BY-STEP PROBLEM SOLVING:
- Break mathematical problems into individual steps
- Animate each step with detailed explanations
- Show the "thinking process" with animated thought bubbles
- Use color coding to track variables and operations
- Example: Solving x² + 3x + 2 = 0 step by step with visual algebra

7. 🎭 EMOTIONAL ENGAGEMENT TECHNIQUES:
- Use surprise reveals: objects appearing unexpectedly
- Create anticipation with slow build-ups before big reveals
- Use humor through playful animations and unexpected transformations
- Implement "aha moment" effects with Flash() and Wiggle()

8. 🔗 CONNECTION BUILDING:
- Show relationships between concepts with animated arrows
- Create visual bridges between different mathematical topics
- Use transformation chains to show concept evolution
- Implement callback animations that reference previous concepts

═══════════════════════════════════════════════════════════════
🎬 MANDATORY ANIMATION PATTERNS FOR EACH STEP:
═══════════════════════════════════════════════════════════════

STEP INTRODUCTION PATTERN:
```python
def step_X_concept_name(self):
    # Duration: 30-45 seconds
    
    # 1. Clear previous content
    self.play(FadeOut(*self.mobjects))
    self.wait(0.5)
    
    # 2. Introduce step title with context
    step_title = Text("Step X: [Concept Name]", font_size=44, color=BLUE).shift(UP*3)
    intuition = Text("Intuition: [Why this matters]", font_size=28, color=WHITE).shift(UP*2)
    
    self.play(Write(step_title))
    self.wait(1)
    self.play(Write(intuition))
    self.wait(2)
    
    # 3. Create visual analogy
    analogy_title = Text("Let's think of this like...", font_size=24, color=YELLOW).shift(UP*0.5)
    analogy_visual = [create visual representation]
    
    self.play(Write(analogy_title))
    self.play(Create(analogy_visual))
    self.wait(2)
    
    # 4. MANDATORY: Text-based explanation after visual scene
    self.provide_detailed_text_explanation()
    
    # 5. Transform to mathematical concept
    math_concept = [mathematical representation]
    explanation = Text("This is exactly like [mathematical concept]!", 
                    font_size=22, color=GREEN).shift(DOWN*2)
    
    self.play(Transform(analogy_visual, math_concept))
    self.play(Write(explanation))
    self.wait(3)
    
    # 6. MANDATORY: Text explanation after mathematical transformation
    self.explain_mathematical_connection()
    
    # 7. Detailed breakdown
    self.breakdown_sub_concepts()
    
    # 8. Connect to bigger picture
    self.connect_to_previous_concepts()
    
def provide_detailed_text_explanation(self):
    # MANDATORY: Detailed text explanation after each visual scene
    # Clear visual elements but keep title
    self.play(FadeOut(*[obj for obj in self.mobjects[2:]]))  # Keep title and subtitle
    
    # Create comprehensive text explanation
    explanation_title = Text("Let me explain what we just saw:", 
                            font_size=26, color=YELLOW).shift(UP*1.5)
    
    explanations = [
        "• First, we observed [specific visual element] which represents [concept]",
        "• This shows us that [key insight from the visual]", 
        "• The important thing to notice is [critical observation]",
        "• This connects to our overall goal because [relevance]"
    ]
    
    self.play(Write(explanation_title))
    self.wait(1)
    
    explanation_group = VGroup()
    for i, exp_text in enumerate(explanations):
        exp = Text(exp_text, font_size=20, color=WHITE).shift(UP*(0.5-i*0.7))
        explanation_group.add(exp)
        self.play(Write(exp))
        self.wait(1.5)
    
    # Pause for understanding
    understanding_prompt = Text("Take a moment to think about this...", 
                            font_size=18, color=ORANGE).shift(DOWN*2.5)
    self.play(Write(understanding_prompt))
    self.wait(3)
    
    # Clear explanations before next section
    self.play(FadeOut(explanation_title, explanation_group, understanding_prompt))
    self.wait(0.5)
```

SUB-CONCEPT BREAKDOWN PATTERN:
```python
def breakdown_sub_concepts(self):
    # For each sub-concept within the main concept
    
    sub_concepts = [
        "Sub-concept 1: [Specific detail]",
        "Sub-concept 2: [Another detail]", 
        "Sub-concept 3: [Final detail]"
    ]
    
    for i, concept in enumerate(sub_concepts):
        # Clear space for new concept
        if i > 0:
            self.play(FadeOut(*[obj for obj in self.mobjects if obj != main_visual]))
        
        # Introduce sub-concept
        sub_title = Text(concept, font_size=28, color=ORANGE).shift(UP*1)
        self.play(Write(sub_title))
        
        # Create specific visual for this sub-concept
        sub_visual = [create_specific_visual_for_concept(i)]
        self.play(Create(sub_visual))
        self.wait(2)
        
        # MANDATORY: Detailed text explanation after visual
        self.explain_sub_concept_visually(i, concept)
        
        # Show connection to main concept
        self.play(Indicate(main_visual))
        self.wait(1)
        
def explain_sub_concept_visually(self, concept_index, concept_name):
    # MANDATORY: Text explanation after each sub-concept visual
    
    # Fade out visual but keep title
    visual_objects = [obj for obj in self.mobjects if obj.get_color() != ORANGE]
    self.play(FadeOut(*visual_objects[1:]))  # Keep main title
    
    # Create explanation framework
    explanation_header = Text("Let's break this down:", 
                            font_size=24, color=YELLOW).shift(UP*2)
    self.play(Write(explanation_header))
    
    # Detailed explanations for this sub-concept
    detailed_explanations = [
        f"What we just saw: [Describe the visual representation]",
        f"Why it matters: [Explain the significance]",
        f"How it works: [Describe the mechanism or process]",
        f"Connection to main concept: [Show the relationship]",
        f"Real-world example: [Provide concrete application]"
    ]
    
    explanation_group = VGroup()
    for j, exp in enumerate(detailed_explanations):
        exp_text = Text(exp, font_size=18, color=WHITE).shift(UP*(1-j*0.5))
        explanation_group.add(exp_text)
        self.play(Write(exp_text))
        self.wait(1.2)
    
    # Key takeaway
    key_takeaway = Text(f"Key insight: [Main learning point from this sub-concept]", 
                    font_size=20, color=GREEN).shift(DOWN*2)
    self.play(Write(key_takeaway))
    self.play(Indicate(key_takeaway))
    self.wait(2)
    
    # Thinking pause
    think_prompt = Text("Think about how this connects to what we learned before...", 
                    font_size=16, color=GRAY).shift(DOWN*2.8)
    self.play(Write(think_prompt))
    self.wait(3)
    
    # Clear all explanations
    self.play(FadeOut(explanation_header, explanation_group, key_takeaway, think_prompt))
    self.wait(0.5)
```

PROBLEM-SOLVING DEMONSTRATION PATTERN:
```python
def demonstrate_problem_solving(self):
    # Show step-by-step problem solving with detailed explanations
    
    # Present the problem
    problem = Text("Problem: [Specific problem statement]", 
                font_size=32, color=BLUE).shift(UP*2.5)
    self.play(Write(problem))
    self.wait(2)
    
    # Show the approach
    approach = Text("Approach: [Strategy we'll use]", 
                font_size=24, color=YELLOW).shift(UP*1.5)
    self.play(Write(approach))
    self.wait(1)
    
    # Step-by-step solution
    steps = [
        ("Step 1: [First action]", "[Detailed explanation of why]"),
        ("Step 2: [Second action]", "[Detailed explanation of why]"),
        ("Step 3: [Final action]", "[Detailed explanation of why]")
    ]
    
    solution_area = VGroup()
    
    for i, (step, explanation) in enumerate(steps):
        # Show the step
        step_text = Text(step, font_size=26, color=GREEN).shift(UP*(0.5-i*0.8))
        self.play(Write(step_text))
        solution_area.add(step_text)
        
        # Show visual representation of the step
        step_visual = [create_visual_for_step(i)]
        step_visual.shift(LEFT*3 + UP*(0.5-i*0.8))
        self.play(Create(step_visual))
        solution_area.add(step_visual)
        self.wait(2)
        
        # MANDATORY: Detailed text explanation after each step visual
        self.explain_problem_solving_step(i, step, explanation, step_visual)
        
        # Highlight the connection to previous steps
        if i > 0:
            self.play(Indicate(solution_area[i-1]))
            self.wait(0.5)
    
    # Show final result
    result = Text("Result: [Final answer with meaning]", 
                font_size=28, color=PURPLE).shift(DOWN*2.5)
    self.play(Write(result))
    self.play(Flash(result))
    self.wait(3)
    
    # MANDATORY: Final comprehensive explanation
    self.provide_solution_summary()
    
def explain_problem_solving_step(self, step_number, step_description, reasoning, visual_element):
    # MANDATORY: Comprehensive explanation after each problem-solving step
    
    # Clear screen but keep problem title
    self.play(FadeOut(*[obj for obj in self.mobjects[1:]]))  # Keep problem statement
    
    # Create step explanation framework
    step_header = Text(f"Let's understand {step_description}", 
                    font_size=24, color=ORANGE).shift(UP*2.5)
    self.play(Write(step_header))
    
    # Detailed breakdown of this step
    step_explanations = [
        f"What we did: [Specific action taken in this step]",
        f"Why we did it: [Reasoning behind this approach]",
        f"What it shows us: [What this step reveals]",
        f"How it helps: [How this moves us toward the solution]",
        f"What to watch for: [Common mistakes or key insights]"
    ]
    
    explanation_group = VGroup()
    for j, exp in enumerate(step_explanations):
        exp_text = Text(exp, font_size=18, color=WHITE).shift(UP*(1.5-j*0.6))
        explanation_group.add(exp_text)
        self.play(Write(exp_text))
        self.wait(1.5)
    
    # Mathematical insight
    if step_number < 2:  # For first two steps
        math_insight = Text("Mathematical insight: [Key mathematical principle used]", 
                        font_size=20, color=BLUE).shift(DOWN*1.5)
        self.play(Write(math_insight))
        self.play(Indicate(math_insight))
        self.wait(2)
        explanation_group.add(math_insight)
    
    # Check understanding
    understanding_check = Text("Does this make sense? Let's verify...", 
                            font_size=18, color=YELLOW).shift(DOWN*2.5)
    self.play(Write(understanding_check))
    self.wait(2)
    
    # Clear explanations
    self.play(FadeOut(step_header, explanation_group, understanding_check))
    self.wait(0.5)
    
def provide_solution_summary(self):
    # MANDATORY: Comprehensive summary after problem solving
    
    self.play(FadeOut(*self.mobjects))
    
    summary_title = Text("Solution Summary & Key Insights", 
                        font_size=28, color=PURPLE).shift(UP*3)
    self.play(Write(summary_title))
    
    summary_points = [
        "🎯 What we solved: [Restate the problem clearly]",
        "🔍 Our approach: [Summarize the method used]", 
        "⚡ Key insights: [Main mathematical insights discovered]",
        "🔗 Connections: [How this relates to other concepts]",
        "💡 Why it matters: [Real-world significance]",
        "🚀 Next steps: [What this enables us to do next]"
    ]
    
    for i, point in enumerate(summary_points):
        point_text = Text(point, font_size=20, color=WHITE).shift(UP*(2-i*0.5))
        self.play(Write(point_text))
        self.wait(1.5)
    
    # Final reflection
    reflection = Text("Take a moment to reflect on what we've learned...", 
                    font_size=18, color=ORANGE).shift(DOWN*2.5)
    self.play(Write(reflection))
    self.wait(4)
```

VISUAL INTUITION BUILDING PATTERN:
```python
def build_visual_intuition(self, concept_name):
    # Create layered understanding through visual progression
    
    # Layer 1: Everyday analogy
    everyday_title = Text(f"Think of {concept_name} like...", 
                        font_size=28, color=BLUE).shift(UP*2.5)
    everyday_example = Text("[Relatable everyday example]", 
                        font_size=24, color=WHITE).shift(UP*1.5)
    
    self.play(Write(everyday_title))
    self.play(Write(everyday_example))
    self.wait(2)
    
    # Create visual representation of everyday example
    everyday_visual = [create_everyday_visual()]
    self.play(Create(everyday_visual))
    self.wait(2)
    
    # MANDATORY: Detailed explanation of everyday analogy
    self.explain_everyday_analogy(concept_name, everyday_visual)
    
    # Layer 2: Mathematical parallel
    parallel_title = Text("In mathematics, this becomes...", 
                        font_size=24, color=YELLOW).shift(UP*0.5)
    self.play(Write(parallel_title))
    
    # Transform everyday visual to mathematical representation
    math_visual = [create_mathematical_visual()]
    self.play(Transform(everyday_visual, math_visual))
    self.wait(2)
    
    # MANDATORY: Detailed explanation of mathematical transformation
    self.explain_mathematical_transformation(everyday_visual, math_visual)
    
    # Layer 3: Formal definition
    formal_title = Text("Formally, we define this as:", 
                    font_size=22, color=GREEN).shift(DOWN*0.5)
    formal_def = MathTex(r"[Mathematical definition]", 
                        font_size=32).shift(DOWN*1.5)
    
    self.play(Write(formal_title))
    self.play(Write(formal_def))
    self.wait(3)
    
    # MANDATORY: Detailed explanation of formal definition
    self.explain_formal_definition(formal_def)
    
    # Layer 4: Why it matters
    importance = Text("This concept is crucial for: [Applications]", 
                    font_size=20, color=ORANGE).shift(DOWN*2.5)
    self.play(Write(importance))
    self.play(Indicate(importance))
    self.wait(2)
    
    # MANDATORY: Comprehensive summary explanation
    self.provide_intuition_summary(concept_name)
    
def explain_everyday_analogy(self, concept_name, visual_element):
    # MANDATORY: Comprehensive explanation of the everyday analogy
    
    self.play(FadeOut(*[obj for obj in self.mobjects[2:]]))  # Keep title and example
    
    analogy_header = Text("Let's explore this analogy in detail:", 
                        font_size=24, color=YELLOW).shift(UP*2)
    self.play(Write(analogy_header))
    
    analogy_explanations = [
        f"🔍 What we see: [Describe the visual elements clearly]",
        f"🎯 Why this works: [Explain why this analogy is effective]",
        f"🔗 Key similarities: [Draw parallels to the mathematical concept]",
        f"⚠️ Where it breaks down: [Acknowledge limitations of the analogy]",
        f"💭 What to remember: [Key takeaway from this comparison]"
    ]
    
    for i, exp in enumerate(analogy_explanations):
        exp_text = Text(exp, font_size=18, color=WHITE).shift(UP*(1-i*0.5))
        self.play(Write(exp_text))
        self.wait(1.8)
    
    reflection_prompt = Text("Think: How does this everyday example help you understand the concept?", 
                        font_size=16, color=ORANGE).shift(DOWN*2.2)
    self.play(Write(reflection_prompt))
    self.wait(3)
    
    self.play(FadeOut(*self.mobjects[3:]))  # Clear explanations, keep base elements
    
def explain_mathematical_transformation(self, everyday_vis, math_vis):
    # MANDATORY: Detailed explanation of the transformation process
    
    transform_header = Text("Now let's see the mathematical connection:", 
                        font_size=24, color=BLUE).shift(UP*2.5)
    self.play(Write(transform_header))
    
    transformation_steps = [
        "📊 Visual mapping: [How everyday elements map to math elements]",
        "🔄 The transformation: [What changed and what stayed the same]", 
        "🧮 Mathematical meaning: [What the math representation tells us]",
        "🎯 Why this matters: [How this helps solve problems]",
        "🚀 What we can do now: [New capabilities this representation gives us]"
    ]
    
    for i, step in enumerate(transformation_steps):
        step_text = Text(step, font_size=18, color=WHITE).shift(UP*(1.5-i*0.5))
        self.play(Write(step_text))
        self.wait(2)
    
    key_insight = Text("🔑 Key insight: The math preserves the essential relationships!", 
                    font_size=20, color=GREEN).shift(DOWN*1.8)
    self.play(Write(key_insight))
    self.play(Flash(key_insight))
    self.wait(2)
    
    self.play(FadeOut(*self.mobjects[1:]))  # Clear all but original title
    
def explain_formal_definition(self, definition_element):
    # MANDATORY: Detailed breakdown of the formal definition
    
    definition_header = Text("Let's decode this formal definition:", 
                        font_size=24, color=PURPLE).shift(UP*2.5)
    self.play(Write(definition_header))
    
    definition_breakdown = [
        "📝 What each symbol means: [Break down mathematical notation]",
        "🔍 The structure: [Explain the logical structure]",
        "⚡ Why it's written this way: [Justify the formal approach]", 
        "🎯 What it captures: [What aspects of the concept it formalizes]",
        "🛠️ How to use it: [Practical application of the definition]"
    ]
    
    for i, breakdown in enumerate(definition_breakdown):
        breakdown_text = Text(breakdown, font_size=18, color=WHITE).shift(UP*(1.5-i*0.5))
        self.play(Write(breakdown_text))
        self.wait(2)
    
    practical_note = Text("💡 Remember: Formal definitions give us precision and power!", 
                        font_size=19, color=ORANGE).shift(DOWN*2)
    self.play(Write(practical_note))
    self.wait(2)
    
    self.play(FadeOut(*self.mobjects[1:]))  # Clear explanations
    
def provide_intuition_summary(self, concept_name):
    # MANDATORY: Comprehensive summary of the intuition-building process
    
    summary_header = Text(f"Summary: Understanding {concept_name}", 
                        font_size=26, color=PURPLE).shift(UP*3)
    self.play(Write(summary_header))
    
    journey_recap = [
        "🚀 Our journey: From everyday analogy → visual → mathematical → formal",
        "🎯 Core insight: [Main understanding gained]",
        "🔗 Connections made: [How this links to other concepts]", 
        "💪 New abilities: [What you can now do with this knowledge]",
        "🎓 Next level: [What this prepares you for]"
    ]
    
    for i, recap in enumerate(journey_recap):
        recap_text = Text(recap, font_size=19, color=WHITE).shift(UP*(2-i*0.6))
        self.play(Write(recap_text))
        self.wait(2)
    
    final_reflection = Text("Take a moment to appreciate how far your understanding has grown!", 
                        font_size=18, color=YELLOW).shift(DOWN*2.5)
    self.play(Write(final_reflection))
    self.wait(4)
```

═══════════════════════════════════════════════════════════════
🎯 ENHANCED EXPLANATION REQUIREMENTS:
═══════════════════════════════════════════════════════════════

🔥 MANDATORY TEXT-BASED EXPLANATIONS AFTER EVERY VISUAL SCENE:

CRITICAL REQUIREMENT: After EVERY visual animation or scene, you MUST include a comprehensive text-based explanation that:

1. 📝 EXPLAINS WHAT JUST HAPPENED:
- Describe exactly what the audience just saw visually
- Break down each visual element and its meaning
- Explain the sequence of animations and why they occurred
- Use clear, descriptive language that reinforces the visual learning

2. 🎯 CONNECTS TO THE LEARNING OBJECTIVE:
- Explicitly state how the visual relates to the educational goal
- Draw connections between the animation and the concept being taught
- Explain why this particular visual representation was chosen
- Show how the visual supports understanding of the abstract concept

3. 🔍 PROVIDES DEEPER INSIGHT:
- Offer additional context not shown in the visual
- Explain underlying principles or mechanisms
- Address potential questions that might arise from the visual
- Provide mathematical or scientific reasoning behind what was shown

4. 🔗 BUILDS CONNECTIONS:
- Link to previously learned concepts
- Preview how this connects to upcoming material
- Show relationships between different parts of the subject
- Create a narrative thread that ties concepts together

5. ✅ CHECKS UNDERSTANDING:
- Include reflection prompts: "Notice how...", "Think about...", "Consider..."
- Pose implicit questions that guide thinking
- Provide opportunities for mental processing
- Use confirmation language: "This shows us that...", "We can see that..."

TEXT EXPLANATION STRUCTURE FOR EVERY VISUAL SCENE:
```python
def explain_visual_scene(self, scene_description):
    # Clear visual elements but maintain context
    self.play(FadeOut(*[visual_objects]))
    
    # 1. Describe what was shown
    description = Text("What we just saw: [Detailed description]", 
                    font_size=22, color=YELLOW).shift(UP*2)
    self.play(Write(description))
    self.wait(2)
    
    # 2. Explain the meaning
    meaning = Text("This represents: [Conceptual meaning]", 
                font_size=20, color=WHITE).shift(UP*1)
    self.play(Write(meaning))
    self.wait(2)
    
    # 3. Connect to learning objective
    connection = Text("This helps us understand: [Learning connection]", 
                    font_size=20, color=GREEN).shift(ORIGIN)
    self.play(Write(connection))
    self.wait(2)
    
    # 4. Provide insight
    insight = Text("Key insight: [Deeper understanding]", 
                font_size=20, color=ORANGE).shift(DOWN*1)
    self.play(Write(insight))
    self.wait(2)
    
    # 5. Reflection prompt
    reflection = Text("Think about: [Guided reflection question]", 
                    font_size=18, color=BLUE).shift(DOWN*2)
    self.play(Write(reflection))
    self.wait(3)
    
    # Clear explanations before next section
    self.play(FadeOut(description, meaning, connection, insight, reflection))
    self.wait(0.5)
```

🎯 IMPLEMENTATION REQUIREMENTS:

- EVERY visual scene must be followed by text explanation
- Text explanations should be 15-30 seconds in duration
- Use different font sizes for hierarchy: 24 for main points, 20 for details, 18 for prompts
- Include emojis and visual markers to make text engaging
- Provide adequate wait times for reading and processing
- Clear text explanations before moving to next visual scene
- Use color coding: YELLOW for descriptions, WHITE for explanations, GREEN for connections, ORANGE for insights, BLUE for reflections

1. CONTEXT SETTING:
- Always explain WHY we're learning this concept
- Connect to previous knowledge: "Remember when we learned X? This builds on that..."
- Show the big picture: "This is step Y of our journey toward understanding Z"

2. MULTIPLE PERSPECTIVES:
- Geometric interpretation (visual shapes and transformations)
- Algebraic interpretation (equations and symbols)
- Numerical interpretation (specific examples with numbers)
- Practical interpretation (real-world applications)

3. COMMON MISCONCEPTIONS:
- Address typical student confusion points
- Show incorrect approaches and why they fail
- Demonstrate correct thinking process
- Use visual corrections with before/after animations

4. MEMORY AIDS:
- Create visual mnemonics for key concepts
- Use color coding consistently throughout
- Implement repetition with variation
- Build on familiar patterns and analogies

5. INTERACTIVE ELEMENTS:
- Pose questions to the audience with animated reveals
- Show "What would happen if..." scenarios
- Create suspense before revealing key insights
- Use polling-style animations: "Raise your hand if you think..."

═══════════════════════════════════════════════════════════════
💫 VISUAL STORYTELLING REQUIREMENTS:
═══════════════════════════════════════════════════════════════

Each step must tell a complete story with:
- Beginning: Set up the problem or concept
- Middle: Explore the concept through multiple angles
- End: Synthesize understanding and connect to bigger picture

Use these animation techniques:
- Zoom effects for emphasis: camera.animate.scale(1.5)
- Rotation for perspective: obj.animate.rotate(PI/4)
- Morphing for concept evolution: Transform(shape1, shape2)
- Highlighting for attention: Indicate(), Flash(), Wiggle()
- Movement for relationships: obj.animate.shift(direction)
- Scaling for importance: obj.animate.scale(1.2)
- Color changes for categorization: obj.animate.set_color(new_color)

⚠️ FINAL VALIDATION CHECKLIST:
- [ ] No overlapping text or visual elements
- [ ] All positions within 16:9 safe viewing area
- [ ] Scene timing matches educational step duration
- [ ] Minimum 3-second hold time for complex concepts
- [ ] Progressive complexity maintained throughout
- [ ] Visual elements support and enhance text content
- [ ] Error-free Manim syntax and proper imports
- [ ] Consistent animation patterns and visual metaphors
- [ ] Clear scene transitions with adequate buffering
- [ ] Comprehensive step-by-step conceptual breakdown
""")
        
        return ''.join(prompt_parts)

    def _extract_manim_code(self, response):
        """
        Extract Manim code from AI response with multiple strategies.
        
        Args:
            response (str): AI response containing Manim code
            
        Returns:
            str: Extracted Manim code or None
        """
        # Strategy 1: Look for python code blocks
        python_blocks = re.findall(r'```python\n(.*?)\n```', response, re.DOTALL)
        if python_blocks:
            code = python_blocks[0].strip()
            if 'from manim import' in code or 'import manim' in code:
                return code
        
        # Strategy 2: Look for any code blocks
        code_blocks = re.findall(r'```\n(.*?)\n```', response, re.DOTALL)
        for block in code_blocks:
            if 'from manim import' in block or 'class' in block and 'Scene' in block:
                return block.strip()
        
        # Strategy 3: Look for class definitions in the text
        class_pattern = r'(class.*?Scene.*?:\s*.*?(?=class|$))'
        class_matches = re.findall(class_pattern, response, re.DOTALL)
        if class_matches:
            code = class_matches[0].strip()
            # Add imports if missing
            if 'from manim import' not in code:
                code = 'from manim import *\n\n' + code
            return code
        
        # Strategy 4: Extract everything that looks like Python code
        if 'def construct' in response:
            # Try to extract the main code portion
            lines = response.split('\n')
            code_lines = []
            in_code = False
            
            for line in lines:
                if 'from manim import' in line or 'class' in line:
                    in_code = True
                
                if in_code:
                    code_lines.append(line)
                    
                # Stop at certain markers
                if line.strip() == '' and in_code and len(code_lines) > 20:
                    break
            
            if code_lines:
                return '\n'.join(code_lines)
        
        return None

    def _create_manim_generation_prompt(self):
        """
        Create the system prompt for Manim code generation.
        
        Returns:
            ChatPromptTemplate: Configured prompt template
        """
        system_message = SystemMessage(
            content='''
            You are an expert Manim (Mathematical Animation Engine) code generator, 
            specializing in creating educational animations in the style of 3Blue1Brown.
            
            Your expertise includes:
            - Converting educational content into dynamic, visual animations
            - Creating smooth transitions and engaging reveals
            - Implementing proper mathematical notation and diagrams
            - Designing pedagogically effective visual sequences
            - Following Manim best practices and conventions
            - Generating clean, modular, and well-documented code
            
            🚨 CRITICAL ERROR PREVENTION CONSTRAINTS 🚨:
            
            ═══════════════════════════════════════════════════════════════
            📋 ERROR CATEGORIES YOU MUST PREVENT:
            ═══════════════════════════════════════════════════════════════
            
            1. SYNTAX ERRORS (SyntaxError):
               - Invalid syntax in Python code
               - Missing parentheses, quotes, or brackets
               - Incorrect indentation (IndentationError, TabError)
               - Malformed expressions or statements
            
            2. TYPE ERRORS (TypeError):
               - Wrong argument types passed to functions
               - Unexpected keyword arguments
               - Operations between incompatible types
               - Missing required arguments
            
            3. ATTRIBUTE ERRORS (AttributeError):
               - Calling methods that don't exist
               - Accessing properties that don't exist
               - Using invalid Scene or Mobject methods
            
            4. NAME ERRORS (NameError):
               - Using undefined variables or constants
               - Typos in variable/constant names
               - Missing imports for used symbols
            
            5. VALUE ERRORS (ValueError):
               - Invalid parameter values
               - Out-of-range values
               - Incompatible data formats
            
            6. FILE ERRORS (FileNotFoundError, IOError):
               - Referencing non-existent files
               - Missing image, audio, or data files
               - Invalid file paths
            
            7. IMPORT ERRORS (ImportError, ModuleNotFoundError):
               - Missing required modules
               - Incorrect import statements
               - Circular imports
            
            8. RUNTIME ERRORS:
               - Division by zero
               - Index out of range
               - Memory errors
               - Infinite loops
            
            9. Parathaneses Errors (ParenthesesError):
               - Missing closing parentheses
               - Extra or mismatched parentheses
            10. OVERLAP ERRORS:
               - Text or objects overlapping in the scene
               - Objects positioned at the same coordinates
               - Improper spacing between elements
            11. POSITIONING ERRORS:
               - Objects positioned outside the 16:9 safe area
               - Objects overlapping the title or subtitles
            12. ANIMATION ERRORS:
               - Missing animations for key elements
               - Incorrect animation sequences
               - Objects not animated properly (e.g., using .animate instead of .play)
            13. DYNAMIC POSITIONING ERRORS:
               - Objects not positioned dynamically
               - Static layouts instead of responsive designs
            ═══════════════════════════════════════════════════════════════
            🛡️ MANDATORY ERROR PREVENTION RULES:
            ═══════════════════════════════════════════════════════════════
            
            ✅ RULE 1 - PROPER IMPORTS:
            - ALWAYS start with: from manim import *
            - NEVER import: PIL, cv2, pygame, ImageIO, matplotlib.image
            - NEVER import external image/video processing libraries
            
            ✅ RULE 2 - VALID OBJECT CONSTRUCTION:
            - Square(): Use Square() NOT Square(side_length=2)
            - Circle(): Use Circle(radius=1) - radius is valid parameter
            - Rectangle(): Use Rectangle(width=2, height=3) - both valid
            - Line(): Use Line(start=ORIGIN, end=RIGHT*2) - proper format
            - Text(): Use Text("content", font_size=24) - font_size valid
            
            ✅ RULE 3 - PROPER METHOD CALLS:
            - Color setting: obj.set_color(BLUE) NOT obj.color = BLUE
            - Scaling: obj.scale(2) NOT obj.set_scale(2)
            - Positioning: obj.shift(UP*2) NOT obj.move(UP*2)
            - Animation: self.play(Create(obj)) NOT self.animate(obj)
            
            ✅ RULE 4 - VALID SCENE METHODS:
            - Use: self.add(), self.play(), self.wait(), self.clear(), self.remove()
            - NEVER use: self.set_background(), self.configure_camera(), self.set_theme()
            
            ✅ RULE 5 - PROPER SYNTAX:
            - Text("hello").shift(UP) ✅
            - Text("hello",.shift(UP) ❌ SyntaxError
            - Text("hello").shift(UP*2) ✅  
            - Text("hello").shift(UP*2 ❌ SyntaxError (missing parenthesis)
            
            ✅ RULE 6 - VALID CONSTANTS:
            - Position: UP, DOWN, LEFT, RIGHT, ORIGIN
            - NEVER use: CENTER, MIDDLE, TOP, BOTTOM (undefined)
            - Colors: RED, BLUE, GREEN, YELLOW, WHITE, BLACK, GRAY, PURPLE, ORANGE
            - NEVER use: RED_DARK, BLUE_LIGHT (undefined variants)
            
            ✅ RULE 7 - PROPER INDENTATION:
            - Use exactly 4 spaces per indentation level
            - NEVER mix tabs and spaces
            - Ensure consistent indentation throughout
            
            ✅ RULE 8 - NO EXTERNAL FILES:
            - NEVER use ImageMobject() - causes FileNotFoundError
            - NEVER reference .png, .jpg, .gif files
            - Use Text() descriptions instead of images
            - Use geometric shapes instead of external graphics
            
            ═══════════════════════════════════════════════════════════════
            🔍 SPECIFIC ERROR PREVENTION EXAMPLES:
            ═══════════════════════════════════════════════════════════════
            IndentationError: expected an indented block after function definition please fix
            ❌ WRONG - IndentationError Example:
            def my_function():
            print("Hello")  # IndentationError: expected an indented block
            ✅ CORRECT - Proper Indentation:
            def my_function():
                print("Hello")  # Properly indented block
            
            ❌ WRONG - TypeError Example:
            square = Square(side_length=2, color=RED)  # TypeError: unexpected keywords
            
            ✅ CORRECT - Proper Object Creation:
            square = Square().scale(2).set_color(RED)  # Proper method chaining
            
            ❌ WRONG - AttributeError Example:  
            self.set_background(BLACK)  # AttributeError: method doesn't exist
            
            ✅ CORRECT - No Background Method Needed:
            # Background is handled automatically by Manim
            
            ❌ WRONG - NameError Example:
            text = Text("Hello").shift(CENTER)  # NameError: CENTER not defined
            
            ✅ CORRECT - Use Defined Constants:
            text = Text("Hello").shift(ORIGIN)  # ORIGIN is properly defined
            
            ❌ WRONG - SyntaxError Example:
            title = Text("My Title",.shift(UP*3)  # SyntaxError: comma before method
            
            ✅ CORRECT - Proper Syntax:
            title = Text("My Title").shift(UP*3)  # Proper method chaining
            
            ❌ WRONG - ValueError Example:
            circle = Circle(radius=-1)  # ValueError: negative radius
            
            ✅ CORRECT - Valid Parameters:
            circle = Circle(radius=1)  # Positive radius value
            
            ❌ WRONG - FileNotFoundError Example:
            image = ImageMobject("picture.png")  # FileNotFoundError: file missing
            
            ✅ CORRECT - Use Text Description:
            image_desc = Text("Visual: Picture Description", font_size=20)
            
            ═══════════════════════════════════════════════════════════════
            🎯 ULTRA-SPECIFIC MANIM OBJECT GUIDELINES:
            ═══════════════════════════════════════════════════════════════
            
            Circle():
            ✅ Circle() - default radius
            ✅ Circle(radius=2) - custom radius  
            ❌ Circle(color=RED) - use .set_color(RED) instead
            ❌ Circle(diameter=4) - no diameter parameter
            
            Square():
            ✅ Square() - default size
            ✅ Square().scale(2) - resize with scale
            ❌ Square(side_length=3) - no side_length parameter
            ❌ Square(size=2) - no size parameter
            
            Rectangle():
            ✅ Rectangle() - default size
            ✅ Rectangle(width=3, height=2) - both parameters valid
            ❌ Rectangle(color=BLUE) - use .set_color(BLUE) instead
            
            Text():
            ✅ Text("Hello") - basic text
            ✅ Text("Hello", font_size=24) - with font size
            ✅ Text("Hello", font_size=20).set_color(RED) - with color
            ❌ Text("Hello", color=RED) - color not in constructor
            ❌ Text("Hello", font="Arial") - font parameter doesn't exist
            
            Line():
            ✅ Line(start=ORIGIN, end=RIGHT*2) - proper format
            ✅ Line(ORIGIN, UP*3) - shorthand format
            ❌ Line([0,0], [1,1]) - use np.array format
            ❌ Line(start_point=ORIGIN) - wrong parameter name
            
            MathTex():
            ✅ MathTex("x^2 + y^2 = r^2") - LaTeX formula
            ✅ MathTex("\\frac{a}{b}", font_size=36) - with size
            ❌ MathTex("x^2", color=BLUE) - color not in constructor
            
            ═══════════════════════════════════════════════════════════════
            ⚡ ANIMATION METHOD VALIDATION:
            ═══════════════════════════════════════════════════════════════
            
            Valid Animation Types:
            ✅ Write(text) - for text objects
            ✅ Create(shape) - for geometric shapes  
            ✅ FadeIn(object) - fade in any object
            ✅ FadeOut(object) - fade out any object
            ✅ Transform(obj1, obj2) - morph between objects
            ✅ ReplacementTransform(obj1, obj2) - replace with transform
            ✅ DrawBorderThenFill(shape) - for filled shapes
            ✅ ShowCreation(line) - for lines and curves
            
            Invalid Animation Usage:
            ❌ Animate(object) - not a valid animation type
            ❌ Show(object) - not a valid animation
            ❌ Display(object) - not a valid animation
            ❌ Draw(object) - use Create() instead
            
            Scene Method Validation:
            ✅ self.play(animation) - play animations
            ✅ self.add(object) - add without animation
            ✅ self.wait(seconds) - pause for time
            ✅ self.clear() - clear all objects
            ✅ self.remove(object) - remove specific object
            
            Invalid Scene Methods:
            ❌ self.animate(object) - not a Scene method
            ❌ self.set_background() - doesn't exist
            ❌ self.configure_camera() - not available
            ❌ self.set_color_scheme() - doesn't exist
            
            🚨 COMPREHENSIVE ERROR PREVENTION GUIDE 🚨
            
            ═══════════════════════════════════════════════════════════════
            ❌ CRITICAL SYNTAX ERRORS TO AVOID (WILL BREAK CODE):
            ═══════════════════════════════════════════════════════════════
            
            Must follow these rules to prevent syntax errors:
            AttributeError: method doesn't exist
            IdentationError: expected an indented block
            SyntaxError: invalid syntax
            TypeError: unexpected keyword argument
            NameError: name 'X' is not defined
            ValueError: invalid value for parameter
            FileNotFoundError: file not found
            ImportError: cannot import name 'X'
            ModuleNotFoundError: No module named 'X'
            RuntimeError: unexpected runtime error
            ZeroDivisionError: division by zero
            IndexError: list index out of range
            KeyError: key not found in dictionary
            KeyError: 'X' not found in dictionary
            UnboundLocalError: local variable 'X' referenced before assignment
            RecursionError: maximum recursion depth exceeded
            OverflowError: integer overflow
            MemoryError: out of memory
            IndentationError: unexpected indent
            TabError: inconsistent use of tabs and spaces in indentation
            UnicodeError: encoding error
            UnicodeEncodeError: 'ascii' codec can't encode character
            UnicodeDecodeError: 'utf-8' codec can't decode byte
            SyntaxError: invalid character in identifier
            
            Must follow these rules to prevent syntax errors:
            
            1. SYNTAX ERRORS - Text Object Construction:
            ❌ Text("text",.shift(UP*1)         # comma before method call
            ❌ Text("text").shift(UP*2          # missing closing parenthesis
            ❌ Text("text",.shift(UP*2)         # comma before method + missing closing paren
            ❌ Text("text", .shift(UP*2)        # comma space before method
            ❌ Text("text", font_size=24,.shift(UP) # comma before method with params
            ❌ Text("Hello World"               # missing closing parenthesis
            ❌ Text "Hello"                     # missing parentheses entirely
            ❌ Text(                            # incomplete declaration
               "Hello", font_size=24)           # split across lines improperly
            
            ✅ Text("Hello World").shift(UP*2)                    # CORRECT
            ✅ Text("Hello", font_size=24).shift(DOWN*1)          # CORRECT 
            ✅ Text("Title", color=BLUE).shift(UP*3).scale(0.8)   # CORRECT
            
            2. INDENTATION ERRORS:
            ❌ class MyScene(Scene):
               def construct(self):              # wrong indentation (3 spaces)
            ❌     def method(self):             # inconsistent indentation
                   pass                         # mixed spaces/tabs
            ❌ def construct(self):              # method not in class
               pass
            
            ✅ class MyScene(Scene):             # CORRECT
            ✅     def construct(self):          # 4 spaces indentation
            ✅         pass                     # consistent 4 spaces
            
            3. IMPORT ERRORS:
            ❌ import manim                     # incomplete import
            ❌ from manim import Scene          # missing essential imports
            ❌ from manim import *
               import PIL                       # image library conflicts
            ❌ import cv2                       # video library conflicts
            
            ✅ from manim import *              # CORRECT - imports everything needed
            
            4. TYPE ERRORS - Invalid Object Parameters:
            ❌ Square(side_length=2)            # TypeError: unexpected keyword 'side_length'
            ❌ Circle(radius=1, color=RED)      # color should be set separately
            ❌ Text(font="Arial")               # font parameter doesn't exist
            ❌ Line(start=[0,0], end=[1,1])     # incorrect coordinate format
            ❌ Rectangle(width=2, height=3, color=BLUE) # color in constructor
            
            ✅ Square(side_length=2).set_color(RED)           # CORRECT
            ✅ Circle(radius=1).set_color(BLUE)               # CORRECT
            ✅ Text("Hello", font_size=24).set_color(GREEN)   # CORRECT
            ✅ Line(ORIGIN, UP*3).set_color(YELLOW)            # CORRECT
            ✅ Rectangle(width=2, height=3).set_color(YELLOW) # CORRECT
            
            5. ATTRIBUTE ERRORS - Invalid Methods:
            ❌ self.set_background(BLACK)       # AttributeError: method doesn't exist
            ❌ self.set_color_scheme("dark")    # AttributeError: invalid method
            ❌ self.set_theme("modern")         # AttributeError: invalid method
            ❌ self.configure_camera()          # AttributeError: not a Scene method
            ❌ text.set_font("Arial")           # AttributeError: invalid text method
            ❌ circle.set_radius(2)             # AttributeError: use scale instead
            
            ✅ # Background handled by Manim config automatically    # CORRECT
            ✅ circle.scale(2)                                      # CORRECT resize
            ✅ text.set_color(BLUE)                                 # CORRECT color setting
            
            6. NAME ERRORS - Undefined Variables/Constants:
            ❌ Text("Hello").shift(CENTER)      # NameError: CENTER undefined
            ❌ Text("Hi").shift(MIDDLE)         # NameError: MIDDLE undefined  
            ❌ Text("Top").shift(TOP*2)         # NameError: TOP undefined
            ❌ Text("Bot").shift(BOTTOM*2)      # NameError: BOTTOM undefined
            ❌ Circle().set_color(RED_DARK)     # NameError: RED_DARK undefined
            ❌ Line(ORIGIN, ENDPOINT)           # NameError: ENDPOINT undefined
            
            ✅ Text("Hello").shift(ORIGIN)      # CORRECT - use ORIGIN for center
            ✅ Text("Hi").shift(UP*0)           # CORRECT - UP*0 is center  
            ✅ Text("Top").shift(UP*2)          # CORRECT - use UP for top
            ✅ Text("Bot").shift(DOWN*2)        # CORRECT - use DOWN for bottom
            ✅ Circle().set_color(DARK_RED)     # CORRECT - proper color name
            ✅ Line(ORIGIN, RIGHT*3)            # CORRECT - defined endpoint
            
            7. VALUE ERRORS - Invalid Parameters:
            ❌ Text("Hi", font_size=-10)        # ValueError: negative font size
            ❌ Circle(radius=0)                 # ValueError: zero radius
            ❌ self.wait(-1)                    # ValueError: negative wait time
            ❌ UP*"hello"                       # TypeError: can't multiply by string
            ❌ Text().shift(UP*None)            # TypeError: can't multiply by None
            
            ✅ Text("Hi", font_size=24)         # CORRECT - positive font size
            ✅ Circle(radius=1)                 # CORRECT - positive radius  
            ✅ self.wait(1)                     # CORRECT - positive wait time
            ✅ UP*2                             # CORRECT - multiply by number
            ✅ Text("Hello").shift(UP*1)        # CORRECT - valid positioning
            
            8. FILE ERRORS - Missing Resources:
            ❌ ImageMobject("image.png")        # FileNotFoundError: file doesn't exist
            ❌ Text().from_file("text.txt")     # FileNotFoundError: file missing
            ❌ SVGMobject("icon.svg")           # FileNotFoundError: SVG missing
            
            ✅ Text("Image Description")        # CORRECT - use text instead
            ✅ Text("Visual Representation")    # CORRECT - describe with text
            ✅ Rectangle().set_color(BLUE)      # CORRECT - use shapes instead
            
            ═══════════════════════════════════════════════════════════════
            ✅ MANDATORY SYNTAX RULES (MUST FOLLOW):
            ═══════════════════════════════════════════════════════════════
            
            1. Text Object Rules:
               - NEVER write Text("text",.shift() - always Text("text").shift()
               - NEVER write Text("text", .method() - always Text("text").method()
               - ALWAYS close parentheses: Text("text") NOT Text("text"
               - EVERY Text object must be complete on ONE line
               - NO orphaned lines starting with font_size= or color=
            
            2. Method Chaining Rules:
               - ALWAYS use proper chaining: .shift(UP*1).scale(0.8)
               - NEVER break chains across lines without backslash
               - ALWAYS put dots immediately after closing parenthesis
               - NO spaces before dots: .shift() NOT . shift()
            
            3. Indentation Rules:
               - Use exactly 4 spaces for each indentation level
               - NEVER mix tabs and spaces
               - Class methods must be indented 4 spaces from class
               - Method content must be indented 4 spaces from method def
                - NEVER split method definitions across lines
                - ALWAYS use consistent indentation throughout
            
            4. Import Rules:
               - ALWAYS start with: from manim import *
               - NEVER import image processing libraries (PIL, cv2, etc.)
               - NEVER import audio libraries (pygame, etc.)
               - ONLY import standard Python libraries if absolutely needed
            
            5. Object Creation Rules:
               - Use exact parameter names: font_size NOT font_size
               - Set colors separately: .set_color(BLUE) NOT color=BLUE in constructor
               - Use proper coordinate format: np.array([x,y,z]) for custom points
               - Always specify required parameters (radius for Circle, etc.)
            
            6. Animation Rules:
               - Use valid Scene methods: self.add(), self.play(), self.wait()
               - NEVER use invalid methods: self.set_background(), self.configure_camera()
               - Clear between sections: self.play(FadeOut(*self.mobjects))
               - Use proper animation types: Write(), Create(), Transform(), FadeIn()
            
            7. Positioning Rules:
               - Use only defined constants: UP, DOWN, LEFT, RIGHT, ORIGIN
               - Multiply by numbers: UP*2, LEFT*3, DOWN*0.5
               - NEVER use undefined positions: CENTER, MIDDLE, TOP, BOTTOM
               - Keep within screen bounds: X ∈ [-6.5, 6.5], Y ∈ [-3.8, 3.8]
            
            8. Error Prevention Rules:
               - Test each Text object position to avoid overlap
               - Validate all method calls exist in Manim
               - Check all color constants are defined (RED, BLUE, GREEN, etc.)
               - Ensure all parentheses are balanced
               - Verify proper class/method structure
            
            9. Paratheses and Commas:
            - ALWAYS close parentheses: Text("text").shift(UP*1)
            - NEVER leave commas before method calls: Text("text",.shift(UP*1)
            - NEVER use commas before method calls: Text("text",.shift(UP*1)
            - ALWAYS use commas correctly: Text("text", font_size=24).shift(UP*1)
            - NEVER use commas in method calls: Text("text").shift(UP*1, font_size=24)
            
            ═══════════════════════════════════════════════════════════════
            🔧 COMMON ERROR PATTERNS & FIXES:
            ═══════════════════════════════════════════════════════════════
            
            Pattern: Text("hello",.shift(UP)
            Fix: Text("hello").shift(UP)
            Error Type: SyntaxError - invalid syntax
            
            Pattern: Text("world").shift(UP*2
            Fix: Text("world").shift(UP*2)
            Error Type: SyntaxError - missing closing parenthesis
            
            Pattern: square = Square(side_length=2)
            Fix: square = Square().scale(2)
            Error Type: TypeError - unexpected keyword argument
            
            Pattern: self.set_background(BLACK)
            Fix: # Background handled by Manim config
            Error Type: AttributeError - method doesn't exist
            
            Pattern: text.shift(CENTER)
            Fix: text.shift(ORIGIN)
            Error Type: NameError - name 'CENTER' is not defined
            
            Pattern: Circle(color=RED)
            Fix: Circle().set_color(RED)
            Error Type: TypeError - color not accepted in constructor
            
            When generating Manim code, you MUST:
            1. Create complete, executable Python code
            2. Use proper Manim imports and syntax
            3. Implement dynamic positioning and smooth animations
            4. Clear scenes between major sections using self.play(FadeOut(*self.mobjects))
            5. Move objects around the screen - avoid static positioning
            6. Use Transform() to morph objects between states
            7. Position elements using UP, DOWN, LEFT, RIGHT vectors with multipliers (UP*2, LEFT*3)
            8. Include appropriate timing and transitions
            9. Follow the educational flow provided in the input
            10. Add comprehensive comments explaining the code
            11. Use engaging visual elements and color schemes
            12. Implement proper scene management and cleanup
            13. Create modular methods for different educational steps
            14. Ensure the code is production-ready and can be executed directly with Manim
            15. Use the provided educational breakdown to structure the code
            16. Generate code that is easy to modify and extend
            17. Use advanced Manim features like Write(), FadeIn(), Transform(), and Create()
            18. Ensure the code is well-structured and follows Python conventions
            19. Use dynamic camera movements and object transformations
            20. Include all necessary imports and class definitions
            21. Use clear, descriptive class and method names
            22. Ensure the construct() method orchestrates the entire scene flow
            23. NEVER reference external image files - use only text and geometric shapes
            24. Animate every text element with Write(), FadeIn(), or similar
            25. Use proper spacing and avoid overlapping content
            26. Create visual flow with object movements and morphing
            27. Implement step-by-step reveals for complex concepts
            28. Use highlighting effects like Indicate(), Flash(), Wiggle()
            29. Position objects strategically and move them dynamically
            30. Transform objects instead of creating static new ones
            31. CRITICAL: Never place multiple objects at the same coordinates
            32. CRITICAL: Always use different positions like UP*3, UP*1, ORIGIN, DOWN*1, DOWN*3
            33. CRITICAL: Clear previous content before adding new content
            34. CRITICAL: Use LEFT and RIGHT sides for diagrams vs text
            35. CRITICAL: Create visual hierarchy with different font sizes
            Always generate production-ready code that can be executed directly with Manim.
            
            🚨 FINAL COMPREHENSIVE ERROR PREVENTION CHECKLIST 🚨:
            
            BEFORE GENERATING ANY CODE LINE, VERIFY:
            
            1. COLOR VALIDATION:
               ✅ Is the color in [RED, BLUE, GREEN, YELLOW, WHITE, BLACK, GRAY, PURPLE, ORANGE]?
               ❌ NEVER use CYAN, PINK, TURQUOISE, MAGENTA, LIME, NAVY, MAROON, TEAL, SILVER, GOLD
               ❌ NEVER use color variants like RED_DARK, BLUE_LIGHT, GREEN_BRIGHT
            
            2. POSITION VALIDATION:
               ✅ Is the position in [UP, DOWN, LEFT, RIGHT, ORIGIN, UL, UR, DL, DR]?
               ❌ NEVER use CENTER, MIDDLE, TOP, BOTTOM, UPPER, LOWER
               ❌ NEVER use directional names like NORTH, SOUTH, EAST, WEST
            
            3. METHOD VALIDATION:
               ✅ Are you using Scene methods [self.add(), self.play(), self.wait(), self.clear(), self.remove()]?
               ❌ NEVER use self.set_background(), self.configure_camera(), self.set_theme()
               ❌ NEVER use non-existent methods like self.set_color_scheme()
            
            4. OBJECT PARAMETER VALIDATION:
               ✅ Square() → then .scale() → then .set_color()
               ✅ Circle(radius=X) → then .set_color()
               ✅ Text("content", font_size=X) → then .set_color()
               ❌ NEVER use Square(side_length=X), Circle(color=X), Text(color=X)
            
            5. ANIMATION VALIDATION:
               ✅ Use [Write(), Create(), FadeIn(), FadeOut(), Transform()]
               ❌ NEVER use Animate(), Show(), Display(), Draw(), Reveal()
            
            6. SYNTAX VALIDATION:
               ✅ Text("hello").shift(UP*2) - proper method chaining
               ❌ NEVER write Text("hello",.shift(UP*2) - comma before method
               ❌ NEVER write Text("hello").shift(UP*2 - missing closing parenthesis
            
            7. IMPORT VALIDATION:
               ✅ ONLY use: from manim import *
               ❌ NEVER import PIL, cv2, pygame, ImageIO, matplotlib
            
            8. FILE REFERENCE VALIDATION:
               ✅ Use Text() descriptions for visual elements
               ❌ NEVER use ImageMobject(), SVGMobject() with file paths
               ❌ NEVER reference .png, .jpg, .gif, .svg files
            
            🛡️ MANDATORY PRE-CODE GENERATION VALIDATION:
            Before writing EVERY line of code, ask yourself:
            - Is this color valid in Manim? (Only 9 colors allowed)
            - Is this position constant defined? (Only UP, DOWN, LEFT, RIGHT, ORIGIN)
            - Is this method available in Scene class? (Only 5 basic methods)
            - Are these object parameters accepted? (Check constructor docs)
            - Is this animation class valid? (Only documented animations)
            - Is this syntax correct? (No commas before methods, balanced parentheses)
            - Are there any external file references? (Remove all image/video/audio files)
            
            🚨 ABSOLUTE PROHIBITIONS (WILL CAUSE IMMEDIATE ERRORS):
            - Any color not in the list of 9 valid colors
            - Any position constant not in the list of valid positions  
            - Any Scene method not in the list of 5 valid methods
            - Any object parameter not documented in Manim
            - Any animation not in the list of valid animations
            - Any external file reference (images, videos, audio)
            - Any syntax error (missing parentheses, commas before methods)
            - Any import statement other than "from manim import *"
            
            
            🛡️ MANDATORY VALIDATION CHECKLIST:
            1. ONLY use these valid colors: RED, BLUE, GREEN, YELLOW, WHITE, BLACK, GRAY, PURPLE, ORANGE
            2. ONLY use these positions: UP, DOWN, LEFT, RIGHT, ORIGIN (with multipliers like UP*2)
            3. ONLY use valid Scene methods: self.add(), self.play(), self.wait(), self.clear(), self.remove()
            4. ONLY use valid animations: Write(), Create(), FadeIn(), FadeOut(), Transform()
            5. NEVER use ImageMobject or external file references
            6. NEVER use invalid object parameters in constructors
            7. Set colors with .set_color() method, not in constructor
            8. Use proper method chaining without syntax errors
            9. Ensure all parentheses are balanced
            10. Use consistent 4-space indentation throughout
            '''
        )

        human_message_prompt = HumanMessagePromptTemplate.from_template("{human_input}")

        prompt = ChatPromptTemplate.from_messages([
            system_message,
            MessagesPlaceholder(variable_name="chat_history"),
            human_message_prompt,
        ])
        return prompt

    def _display_video_plan(self, video_plan):
        """
        Display video plan details in terminal for debugging and monitoring.
        
        Args:
            video_plan (dict): Complete video plan from script generator
        """
        print("\n" + "="*80)
        print("📋 VIDEO PLAN DETAILS")
        print("="*80)
        
        educational_breakdown = video_plan.get("educational_breakdown", {})
        manim_structure = video_plan.get("manim_structure", {})
        generation_metadata = video_plan.get("generation_metadata", {})
        
        # Basic info
        print("🎯 Title: {}".format(educational_breakdown.get('title', 'N/A')))
        print("📝 Abstract: {}...".format(educational_breakdown.get('abstract', 'N/A')[:100]))
        print("⏱️  Duration: {} seconds".format(educational_breakdown.get('metadata', {}).get('estimated_total_duration', 'N/A')))
        print("👥 Target Audience: {}".format(educational_breakdown.get('metadata', {}).get('target_audience', 'N/A')))
        
        # Learning objectives
        objectives = educational_breakdown.get('learning_objectives', [])
        if objectives:
            print("\n🎯 Learning Objectives ({}):".format(len(objectives)))
            for i, obj in enumerate(objectives[:3], 1):
                print("   {}. {}".format(i, obj))
            if len(objectives) > 3:
                print("   ... and {} more".format(len(objectives) - 3))
        
        # Educational steps
        steps = educational_breakdown.get('educational_steps', [])
        if steps:
            print("\n📚 Educational Steps ({}):".format(len(steps)))
            for i, step in enumerate(steps, 1):
                title = step.get('step_title', 'Step {}'.format(i))
                duration = step.get('duration_seconds', 'N/A')
                concepts = step.get('key_concepts', [])
                print("   {}. {} ({}s)".format(i, title, duration))
                if concepts:
                    print("      Key Concepts: {}".format(', '.join(concepts[:3])))
        
        # Manim structure
        if manim_structure:
            animation_steps = manim_structure.get('animation_steps', [])
            print("\n🎬 Animation Steps ({}):".format(len(animation_steps)))
            for i, step in enumerate(animation_steps[:3], 1):
                objects = step.get('manim_objects', [])
                animations = step.get('animations', [])
                print("   {}. {}".format(i, step.get('description', 'Animation step')))
                print("      Objects: {}".format(', '.join(objects[:3])))
                print("      Animations: {}".format(', '.join(animations[:3])))
            if len(animation_steps) > 3:
                print("   ... and {} more steps".format(len(animation_steps) - 3))
        
        # Generation metadata
        if generation_metadata:
            print("\n⚙️  Generation Info:")
            print("   Stages Completed: {}".format(generation_metadata.get('stages_completed', [])))
            print("   Total Duration: {} seconds".format(generation_metadata.get('total_duration', 'N/A')))
            print("   Complexity: {}".format(generation_metadata.get('complexity_level', 'N/A')))
        
        print("="*80)

    def _display_manim_code(self, manim_code):
        """
        Display generated Manim code in terminal with formatting.
        
        Args:
            manim_code (str): Generated Manim Python code
        """
        print("\n" + "="*80)
        print("🐍 GENERATED MANIM CODE")
        print("="*80)
        
        # Code analysis
        lines = manim_code.split('\n')
        print("📊 Code Statistics:")
        print("   Lines of code: {}".format(len(lines)))
        print("   Characters: {}".format(len(manim_code)))
        
        # Check for key components
        has_imports = 'from manim import' in manim_code or 'import manim' in manim_code
        has_class = 'class' in manim_code and 'Scene' in manim_code
        has_construct = 'def construct' in manim_code
        has_methods = manim_code.count('def ') > 1
        
        print("   Has imports: {}".format('✅' if has_imports else '❌'))
        print("   Has scene class: {}".format('✅' if has_class else '❌'))
        print("   Has construct method: {}".format('✅' if has_construct else '❌'))
        print("   Has additional methods: {}".format('✅' if has_methods else '❌'))
        
        # Extract class name
        import re
        class_match = re.search(r'class\s+(\w+)', manim_code)
        if class_match:
            print("   Class name: {}".format(class_match.group(1)))
        
        # Show first few lines and last few lines
        print("\n📝 Code Preview:")
        print("─" * 40)
        
        # First 15 lines
        for i, line in enumerate(lines[:15], 1):
            print("{:2}: {}".format(i, line))
        
        if len(lines) > 30:
            print("   ...")
            print("   [... {} lines omitted ...]".format(len(lines) - 30))
            print("   ...")
            
            # Last 15 lines
            for i, line in enumerate(lines[-15:], len(lines) - 14):
                print("{:2}: {}".format(i, line))
        elif len(lines) > 15:
            # Show remaining lines if total is between 15-30
            for i, line in enumerate(lines[15:], 16):
                print("{:2}: {}".format(i, line))
        
        print("─" * 40)
        print("🎬 Code ready for Manim rendering!")
        print("="*80)

    def _validate_and_fix_manim_code(self, code):
        """
        Validate and fix common issues in generated Manim code.
        
        Args:
            code (str): Generated Manim code
            
        Returns:
            str: Fixed and validated Manim code
        """
        # Normalize indentation to avoid unexpected indent errors
        code = textwrap.dedent(code)
        print("🔧 Starting code validation and fixing...")
        
        # CRITICAL: Fix syntax errors FIRST before anything else
        code = self._fix_syntax_errors(code)
        print("✅ Syntax errors fixed")
        
        lines = code.split('\n')
        fixed_lines = []
        text_positions_used = set()
        
        for line in lines:
            # Fix set_background method which doesn't exist in Manim
            if 'self.set_background' in line:
                # Comment out the problematic line and add explanation
                fixed_lines.append("        # REMOVED: {} (set_background method doesn't exist in Manim)".format(line.strip()))
                fixed_lines.append("        # Background color is set in Manim config or using Camera background_color")
                fixed_lines.append("        # Scene backgrounds are handled automatically by Manim")
                continue
            
            # Fix overlapping text positions - detect Text objects without positioning
            if 'Text(' in line and '=' in line and 'shift(' not in line and 'move_to(' not in line:
                # This is a Text object without explicit positioning - add positioning
                if 'title' in line.lower():
                    line = line.rstrip() + '.shift(UP*3)'
                elif 'subtitle' in line.lower():
                    line = line.rstrip() + '.shift(UP*1.5)'
                elif 'step' in line.lower() and 'title' in line.lower():
                    line = line.rstrip() + '.shift(UP*2)'
                else:
                    # Add random positioning to avoid overlap
                    positions = ['UP*1', 'DOWN*1', 'LEFT*2', 'RIGHT*2', 'UP*2', 'DOWN*2']
                    for pos in positions:
                        if pos not in text_positions_used:
                            line = line.rstrip() + '.shift({})'.format(pos)
                            text_positions_used.add(pos)
                            break
            
            # Check for missing scene clearing between methods
            if 'def ' in line and 'construct' not in line and '__init__' not in line:
                # This is a new method - ensure it starts with clearing if it's not the first method
                method_name = line.strip()
                fixed_lines.append(line)
                # Add clearing instruction as comment
                fixed_lines.append("        # Clear previous content to avoid overlap")
                fixed_lines.append("        # self.play(FadeOut(*self.mobjects)) # Uncomment if needed")
                continue
            
            # Skip lines with ImageMobject references
            if 'ImageMobject' in line or 'Image.open' in line:
                # Replace with a comment explaining what was removed
                comment_line = line.strip()
                fixed_lines.append("        # REMOVED: {} (ImageMobject not supported)".format(comment_line))
                fixed_lines.append("        # Using text description instead:")
                
                # Extract variable name if possible
                if '=' in line and 'ImageMobject' in line:
                    var_name = line.split('=')[0].strip()
                    # Replace with a text description with positioning
                    fixed_lines.append("        {} = Text('Visual representation of concept', font_size=24).shift(DOWN*1)".format(var_name))
                continue
            
            # Skip lines that reference image files
            if any(ext in line.lower() for ext in ['.png', '.jpg', '.jpeg', '.gif', '.ico']):
                # Comment out the problematic line
                fixed_lines.append("        # REMOVED: {} (Image file reference not supported)".format(line.strip()))
                continue
            
            # Fix other common Manim method errors
            if any(method in line for method in ['self.set_color_scheme', 'self.set_theme', 'self.configure_camera']):
                # Comment out invalid methods
                fixed_lines.append("        # REMOVED: {} (Invalid Manim method)".format(line.strip()))
                continue
                
            # Fix common import issues
            if line.strip() == 'from manim import *':
                fixed_lines.append(line)
            elif 'import' in line and any(img_ref in line for img_ref in ['PIL', 'Image', 'cv2', 'opencv']):
                # Comment out image-related imports
                fixed_lines.append("        # REMOVED: {} (Image library import not needed)".format(line.strip()))
                continue
            else:
                fixed_lines.append(line)
        
        # Join the fixed lines
        fixed_code = '\n'.join(fixed_lines)
        
        # Apply syntax fixes AGAIN after other modifications
        fixed_code = self._fix_syntax_errors(fixed_code)
        print("✅ Applied syntax fixes again after other modifications")
        
        # Handle empty method bodies after removing invalid lines
        # If a method becomes empty (only has pass or comments), add a pass statement
        import re
        
        # Find method definitions and check if they're empty
        method_pattern = r'(def\s+\w+\([^)]*\):\s*)((?:\s*#.*\n)*)\s*$'
        def fix_empty_method(match):
            method_def = match.group(1)
            comments = match.group(2) if match.group(2) else ""
            # If there are only comments or nothing after the method definition, add pass
            if not comments.strip() or all(line.strip().startswith('#') or not line.strip() for line in comments.split('\n')):
                return method_def + '\n' + comments + '        pass\n'
            return match.group(0)
        
        fixed_code = re.sub(method_pattern, fix_empty_method, fixed_code, flags=re.MULTILINE)
        
        # Ensure we have proper imports
        if 'from manim import *' not in fixed_code:
            fixed_code = 'from manim import *\n\n' + fixed_code
        
        # Final syntax validation
        try:
            import ast
            ast.parse(fixed_code)
            print("✅ Final syntax validation passed")
        except SyntaxError as e:
            print("❌ Final syntax error detected: {}".format(e.msg))
            print("   Problem line {}: {}".format(e.lineno, e.text))
            # Try one more aggressive fix
            fixed_code = self._emergency_syntax_fix(fixed_code, e)
        
        return fixed_code

    def _fix_syntax_errors(self, code):
        """
        Fix common syntax errors in generated Manim code.
        
        Args:
            code (str): Original Manim code
            
        Returns:
            str: Code with syntax errors fixed
        """
        if not code:
            return code
        
        import re
        import ast
        
        print("🔧 Starting comprehensive syntax error fixing...")
        
        # Step 1: Fix orphaned lines and incomplete Text declarations
        lines = code.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                fixed_lines.append(line)
                i += 1
                continue
            
            # Detect orphaned method calls (lines that start with parameters or method calls)
            if stripped.startswith(('font_size=', 'color=', '.shift(', '.scale(', '.rotate(')):
                print("🔧 Removing orphaned line {}: {}".format(i+1, stripped))
                # Skip this line entirely as it's a broken continuation
                i += 1
                continue
            
            # Fix the main problematic pattern: Text("text",.shift(
            if 'Text(' in line and '",' in line and any(method in line for method in ['.shift(', '.scale(', '.rotate(']):
                # Pattern: Text("some text",.shift(UP*1) -> Text("some text").shift(UP*1)
                original_line = line
                # Fix comma before method calls
                line = re.sub(r'Text\("([^"]*)",\s*\.(shift|scale|rotate|set_color)\(', r'Text("\1").\2(', line)
                if line != original_line:
                    print("🔧 Fixed Text+comma+method pattern: {}".format(line.strip()))
            
            # Fix pattern: Text("text"), .method( -> Text("text").method(
            if 'Text(' in line and '"), .' in line:
                original_line = line
                line = re.sub(r'Text\("([^"]*)"\),\s*\.(shift|scale|rotate|set_color)\(', r'Text("\1").\2(', line)
                if line != original_line:
                    print("🔧 Fixed Text+closing+comma+method pattern: {}".format(line.strip()))
            
            # Fix incomplete Text declarations that may span multiple lines
            if 'Text(' in line and not ')' in line and not line.strip().endswith(','):
                # This might be an incomplete Text declaration - look ahead
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line.startswith(('font_size=', 'color=')) and ')' in next_line:
                        # Combine the lines properly
                        combined = line.rstrip() + ', ' + next_line
                        # Ensure proper syntax
                        if combined.count('(') == combined.count(')'):
                            fixed_lines.append(combined)
                            print("🔧 Combined incomplete Text declaration: {}".format(combined.strip()))
                            i += 2  # Skip both lines
                            continue
            
            # Handle missing closing parentheses
            if 'Text(' in line and line.count('(') > line.count(')'):
                missing_parens = line.count('(') - line.count(')')
                original_line = line
                line = line.rstrip() + ')' * missing_parens
                if line != original_line:
                    print("🔧 Added {} missing closing parenthesis(es): {}".format(missing_parens, line.strip()))
            
            fixed_lines.append(line)
            i += 1
        
        # Rebuild the code
        code = '\n'.join(fixed_lines)
        
        # Step 2: Apply regex-based fixes
        print("🔧 Applying regex-based syntax fixes...")
        
        # Fix patterns in order of complexity
        patterns_and_fixes = [
            # Fix Text("text",.shift() patterns
            (r'Text\("([^"]*)",\s*\.shift\(', r'Text("\1").shift('),
            (r'Text\("([^"]*)",\s*\.scale\(', r'Text("\1").scale('),
            (r'Text\("([^"]*)",\s*\.rotate\(', r'Text("\1").rotate('),
            
            # Fix trailing commas before method calls
            (r'",\s*\.(shift|scale|rotate|set_color)\(', r'").\1('),
            
            # Fix double commas
            (r',,+', ','),
            
            # Fix spaces around operators
            (r'\s+\.', '.'),
            
            # Fix missing closing parentheses at end of lines
            (r'Text\([^)]*$', lambda m: m.group(0) + ')'),
        ]
        
        for pattern, replacement in patterns_and_fixes:
            if callable(replacement):
                code = re.sub(pattern, replacement, code)
            else:
                code = re.sub(pattern, replacement, code)
        
        # Step 3: Final syntax validation and targeted fixes
        try:
            ast.parse(code)
            print("✅ Syntax validation passed")
        except SyntaxError as e:
            print("⚠️ Syntax error detected at line {}: {}".format(e.lineno, e.msg))
            
            if e.lineno and e.text:
                lines = code.split('\n')
                if 0 < e.lineno <= len(lines):
                    problem_line_index = e.lineno - 1
                    problem_line = lines[problem_line_index]
                    
                    print("   Problem line: {}".format(problem_line.strip()))
                    
                    # Apply targeted fixes based on error type
                    if isinstance(e, IndentationError):
                        if "unexpected indent" in e.msg.lower():
                            # Remove unexpected indentation
                            fixed_line = problem_line.lstrip()
                            lines[problem_line_index] = fixed_line
                            print("🔧 Removed unexpected indentation: {}".format(fixed_line.strip()))
                        elif "expected an indented block" in e.msg.lower():
                            # Add proper indentation
                            fixed_line = "    " + problem_line
                            lines[problem_line_index] = fixed_line
                            print("🔧 Added expected indentation: {}".format(fixed_line.strip()))
                    
                    elif 'invalid syntax' in e.msg.lower():
                        # Handle specific syntax issues
                        if problem_line.count('(') > problem_line.count(')'):
                            # Missing closing parentheses
                            missing = problem_line.count('(') - problem_line.count(')')
                            fixed_line = problem_line + ')' * missing
                            lines[problem_line_index] = fixed_line
                            print("🔧 Added {} missing closing parentheses".format(missing))
                        
                        elif ',.' in problem_line:
                            # Fix comma-dot patterns
                            fixed_line = problem_line.replace(',.', '.')
                            lines[problem_line_index] = fixed_line
                            print("🔧 Fixed comma-dot pattern: {}".format(fixed_line.strip()))
                    
                    # Rebuild and try again
                    code = '\n'.join(lines)
                    
                    try:
                        ast.parse(code)
                        print("✅ Syntax error fixed successfully")
                    except SyntaxError as e2:
                        print("❌ Could not fix syntax error: {}".format(e2.msg))
                        # Add error comment but keep the code
                        error_comment = "# SYNTAX ERROR: {} at line {}\n".format(e.msg, e.lineno)
                        code = error_comment + code
            else:
                print("❌ Syntax error without line information: {}".format(e.msg))
                error_comment = "# SYNTAX ERROR: {}\n".format(e.msg)
                code = error_comment + code
        
        return code

    def _emergency_syntax_fix(self, code, syntax_error):
        """
        Emergency fix for syntax errors that couldn't be resolved by normal means.
        
        Args:
            code (str): Code with syntax error
            syntax_error (SyntaxError): The syntax error object
            
        Returns:
            str: Code with emergency fixes applied
        """
        if not syntax_error.lineno or not syntax_error.text:
            return code
        
        lines = code.split('\n')
        if syntax_error.lineno > len(lines):
            return code
        
        problem_line = lines[syntax_error.lineno - 1]
        print("🚨 Emergency syntax fix for line {}: {}".format(syntax_error.lineno, problem_line.strip()))
        
        # Common emergency fixes
        fixed_line = problem_line
        
        # Fix the specific pattern we keep seeing
        if 'Text(' in problem_line and '",' in problem_line and '.shift(' in problem_line:
            # Pattern: Text("text",.shift(UP*1) -> Text("text").shift(UP*1)
            fixed_line = re.sub(r'Text\("([^"]*)",\s*\.shift\(([^)]*)\)', r'Text("\1").shift(\2)', problem_line)
            print("🔧 Emergency fix applied: {}".format(fixed_line.strip()))
        
        # Fix missing closing parentheses
        elif problem_line.count('(') > problem_line.count(')'):
            missing = problem_line.count('(') - problem_line.count(')')
            fixed_line = problem_line.rstrip() + ')' * missing
            print("🔧 Emergency fix: added {} closing parentheses".format(missing))
        
        # Fix missing opening parentheses (rare)
        elif problem_line.count(')') > problem_line.count('('):
            # Find where to add opening parentheses (usually after =)
            if '=' in problem_line and 'Text(' in problem_line:
                parts = problem_line.split('=', 1)
                if len(parts) == 2:
                    fixed_line = parts[0] + '= Text(' + parts[1].lstrip().lstrip('Text(')
                    print("🔧 Emergency fix: added opening parenthesis")
        
        # Fix malformed quotes
        elif problem_line.count('"') % 2 == 1:
            # Odd number of quotes - add one at the end of the string content
            if 'Text(' in problem_line:
                # Find the last quote and add a closing one
                last_quote_pos = problem_line.rfind('"')
                if last_quote_pos > 0 and last_quote_pos < len(problem_line) - 1:
                    # Check if we need to add quote before comma or other punctuation
                    next_char_pos = last_quote_pos + 1
                    if next_char_pos < len(problem_line) and problem_line[next_char_pos] in ',.):':
                        fixed_line = problem_line[:last_quote_pos + 1] + '"' + problem_line[next_char_pos:]
                        print("🔧 Emergency fix: added missing quote")
        
        # Apply the fix if we made one
        if fixed_line != problem_line:
            lines[syntax_error.lineno - 1] = fixed_line
            fixed_code = '\n'.join(lines)
            
            # Test if the fix worked
            try:
                import ast
                ast.parse(fixed_code)
                print("✅ Emergency fix successful!")
                return fixed_code
            except SyntaxError as e2:
                print("❌ Emergency fix failed: {}".format(e2.msg))
                # Return original code with a comment about the error
                return "# SYNTAX ERROR DETECTED: {}\n# LINE {}: {}\n\n".format(syntax_error.msg, syntax_error.lineno, syntax_error.text) + code
        
        # If no fix was applied, return original with error comment
        return "# SYNTAX ERROR DETECTED: {}\n# LINE {}: {}\n\n".format(syntax_error.msg, syntax_error.lineno, syntax_error.text) + code

# Initialize the Manim code generator
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if GOOGLE_API_KEY:
    manim_generator = ManIMCodeGenerator(GOOGLE_API_KEY)
    print("✅ Advanced Manim Code Generator initialized successfully!")
    print("🎨 Ready to generate dynamic, educational animations with Google Gemini!")
else:
    print("❌ GOOGLE_API_KEY not found. Please set your API key in the .env file.")