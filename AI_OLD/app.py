import streamlit as st
import time
import os
from script_generator import ScienceVideoGenerator
from manim_code_generator import ManIMCodeGenerator
# from v0 import manim_generator
from animation_creator import create_animation_from_code

st.set_page_config(
    page_title="EduGen",
    page_icon="🎓",
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# Custom CSS for minimal ChatGPT-like interface
st.markdown("""
<style>
/* Hide default streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main container styling */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 48rem;
    margin: 0 auto;
}

/* Chat messages styling */
.stChatMessage {
    background: transparent;
    border: none;
    padding: 1rem 0;
}

/* User message styling */
.stChatMessage[data-testid="user-message"] {
    background-color: transparent;
}

/* Assistant message styling */  
.stChatMessage[data-testid="assistant-message"] {
    background-color: #f7f7f8;
    border-radius: 0.75rem;
    margin: 1rem 0;
    padding: 1.5rem;
}

/* Input styling */
.stChatInputContainer {
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 0.75rem;
    padding: 0.75rem;
    margin-top: 1rem;
}

/* Sidebar styling */
.css-1d391kg {
    background-color: #f9fafb;
    border-right: 1px solid #e5e7eb;
}

/* Status container minimal styling */
.element-container div[data-testid="stStatus"] {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 0.5rem;
}

/* Button styling */
.stButton > button {
    background: #ffffff;
    color: #374151;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    padding: 0.5rem 1rem;
    font-weight: 500;
}

.stButton > button:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

/* Expander styling */
.streamlit-expanderHeader {
    background: transparent;
    border: none;
    color: #6b7280;
    font-size: 0.875rem;
}

/* Minimal video container */
.video-container {
    margin: 1rem 0;
    border-radius: 0.75rem;
    overflow: hidden;
    border: 1px solid #e5e7eb;
}

/* Title styling */
h1 {
    font-size: 2rem;
    font-weight: 600;
    color: #111827;
    text-align: center;
    margin-bottom: 0.5rem;
}

/* Subtitle styling */
.subtitle {
    color: #6b7280;
    text-align: center;
    font-size: 1rem;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Minimal header
st.title(" 🧬 EduGen 🎬")
st.markdown('<div class="subtitle">Create educational science videos with AI</div>', unsafe_allow_html=True)

# Minimal sidebar with settings
with st.sidebar:
    st.markdown("### Settings")
    
    # Complexity level
    complexity = st.selectbox(
        "Complexity:",
        ["elementary", "middle-school", "high-school", "undergraduate", "advanced"],
        index=2,
        label_visibility="collapsed"
    )
    
    # Scientific domain (auto-detect from query, but user can override)
    domain = st.selectbox(
        "Domain:",
        ["auto-detect", "physics", "chemistry", "biology", "earth-science", "mathematics", "computer-science"],
        index=0,
        label_visibility="collapsed"
    )
    
    # Video quality
    video_quality = st.selectbox(
        "Quality:",
        ["medium", "high", "low"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Minimal example section
    st.markdown("**Examples by Domain:**")
    
    with st.expander("🔬 Physics"):
        st.markdown("• Newton's laws of motion\n• Wave properties and behavior\n• Electromagnetic induction\n• Quantum mechanics basics")
    
    with st.expander("🧪 Chemistry"):
        st.markdown("• Atomic structure and bonding\n• Chemical reactions and equilibrium\n• Periodic table trends\n• Molecular geometry")
    
    with st.expander("🧬 Biology"):
        st.markdown("• Cell structure and function\n• DNA replication and transcription\n• Photosynthesis process\n• Evolution and natural selection")
    
    with st.expander("🌍 Earth Science"):
        st.markdown("• Plate tectonics\n• Water cycle and weather\n• Rock cycle and formation\n• Climate change mechanisms")
    
    with st.expander("📊 Mathematics"):
        st.markdown("• Algebra and equations\n• Geometric theorems\n• Calculus fundamentals\n• Statistics and probability")
    
    with st.expander("💻 Computer Science"):
        st.markdown("• Algorithm complexity\n• Data structures\n• Programming concepts\n• Machine learning basics")
    
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.processing = False
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display video if available
        if message.get("video_path"):
            st.video(message["video_path"])
            
            # Minimal download button
            try:
                with open(message["video_path"], 'rb') as video_file:
                    st.download_button(
                        label="Download video",
                        data=video_file.read(),
                        file_name=f"math_animation_{int(time.time())}.mp4",
                        mime="video/mp4",
                        key=f"download_{message.get('timestamp', 0)}",
                        use_container_width=False
                    )
            except FileNotFoundError:
                st.error("Video file not found. Please try regenerating.")
        
        # Minimal structured content display
        if message.get("educational_breakdown"):
            with st.expander("View educational details"):
                educational_breakdown = message["educational_breakdown"]
                manim_structure = message.get("manim_structure", {})
                
                # Educational content details
                st.write(f"**Title:** {educational_breakdown.get('title', 'Math Concept')}")
                st.write(f"**Target Audience:** {educational_breakdown.get('target_audience', 'N/A')}")
                st.write(f"**Duration:** {educational_breakdown.get('estimated_total_duration', 'N/A')} seconds")
                
                # Learning objectives
                if educational_breakdown.get('learning_objectives'):
                    st.write("**Learning Objectives:**")
                    for obj in educational_breakdown['learning_objectives']:
                        st.write(f"• {obj}")
                
                # Educational steps summary
                if educational_breakdown.get('educational_steps'):
                    st.write("**Educational Steps:**")
                    for i, step in enumerate(educational_breakdown['educational_steps'][:3], 1):
                        st.write(f"{i}. **{step.get('step_title', f'Step {i}')}** ({step.get('duration_seconds', 'N/A')}s)")
                        st.write(f"   {step.get('description', '')[:100]}...")
                
                # Prerequisites and applications
                col1, col2 = st.columns(2)
                with col1:
                    if educational_breakdown.get('prerequisites'):
                        st.write("**Prerequisites:**")
                        for prereq in educational_breakdown['prerequisites']:
                            st.write(f"• {prereq}")
                
                with col2:
                    if educational_breakdown.get('real_world_applications'):
                        st.write("**Applications:**")
                        for app in educational_breakdown['real_world_applications']:
                            st.write(f"• {app}")
                
                # Common misconceptions
                if educational_breakdown.get('common_misconceptions'):
                    st.write("**Common Misconceptions:**")
                    for misconception in educational_breakdown['common_misconceptions']:
                        st.write(f"⚠️ {misconception}")
                
                # Animation details
                if manim_structure and manim_structure.get('animation_steps'):
                    st.write("**Animation Steps:**")
                    for step in manim_structure['animation_steps'][:3]:
                        objects = ', '.join(step.get('manim_objects', [])[:3])
                        animations = ', '.join(step.get('animations', [])[:3])
                        st.write(f"• {step.get('description', 'Animation step')}")
                        st.write(f"  Objects: {objects}")
                        st.write(f"  Animations: {animations}")

# Chat input - simplified
if prompt := st.chat_input("What scientific concept would you like me to explain?"):
    if not st.session_state.processing:
        # Add user message to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": time.time()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the request
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            status_container = st.container()
            
            st.session_state.processing = True
            
            try:
                # Step 1: Generate complete video plan (both educational and Manim structure)
                with status_container:
                    status = st.status("Understanding your request...", expanded=False)
                    with status:
                        st.write("Analyzing scientific concept...")
                        
                        enhanced_prompt = f"""
                        Create an educational video animation about: {prompt}
                        
                        Requirements:
                        - Complexity level: {complexity}
                        - Scientific domain: {domain}
                        - Generate comprehensive educational content with clear step-by-step explanations
                        - Include detailed visual descriptions and animation plans
                        - Create engaging learning objectives and real-world applications
                        - Design content suitable for animated video format with proper timing
                        - Include scientific equations, diagrams, models, and interactive elements
                        - Use appropriate scientific terminology and concepts
                        """
                        
                        # FIX: Create instance of ScienceVideoGenerator and call the method
                        video_generator = ScienceVideoGenerator(google_api_key = os.getenv('GOOGLE_API_KEY'))
                        video_plan = video_generator.generate_complete_video_plan(enhanced_prompt)
                        
                        if video_plan and "error" not in video_plan:
                            st.write("✅ Educational content generated")
                        else:
                            st.error("Failed to generate educational content")
                            st.session_state.processing = False
                            st.stop()
                
                # Step 2: Generate Manim code
                with status_container:
                    status.update(label="Creating animation code...", state="running")
                    with status:
                        st.write("Converting to Manim code...")
                        
                        # Create Manim code generator instance
                        manim_generator = ManIMCodeGenerator(google_api_key = os.getenv('GOOGLE_API_KEY'))
                        
                        # Generate the code using the complete video plan
                        manim_code = manim_generator.generate_3b1b_manim_code(video_plan)
                        
                        if manim_code:
                            st.write("✅ Animation code generated")
                        else:
                            st.error("Failed to generate animation code")
                            st.session_state.processing = False
                            st.stop()
                
                # Step 3: Create animation
                with status_container:
                    status.update(label="Rendering animation...", state="running")
                    with status:
                        st.write("Creating video file...")
                        
                        # Create the animation
                        video_path = create_animation_from_code(
                            manim_code, 
                           # quality=video_quality,
                            output_dir="animations"
                        )
                        
                        if video_path and os.path.exists(video_path):
                            st.write("✅ Animation rendered successfully")
                            status.update(label="Animation complete!", state="complete")
                        else:
                            st.error("Failed to create animation")
                            st.session_state.processing = False
                            st.stop()
                
                # Display results
                response_text = f"""
I've created an educational video animation about **{video_plan.get('topic', prompt)}**!

**Educational Overview:**
- **Complexity Level:** {complexity}
- **Domain:** {domain if domain != 'auto-detect' else 'Auto-detected'}
- **Duration:** ~{video_plan.get('generation_metadata', {}).get('total_duration', 'N/A')} seconds
- **Steps:** {video_plan.get('generation_metadata', {}).get('educational_steps', 'N/A')} educational concepts

The animation covers key learning objectives with step-by-step visual explanations designed for your specified audience level.
                """
                
                message_placeholder.markdown(response_text)
                
                # Display the video
                if video_path:
                    st.video(video_path)
                    
                    # Download button
                    try:
                        with open(video_path, 'rb') as video_file:
                            st.download_button(
                                label="📥 Download Animation",
                                data=video_file.read(),
                                file_name=f"science_animation_{int(time.time())}.mp4",
                                mime="video/mp4",
                                use_container_width=False
                            )
                    except FileNotFoundError:
                        st.error("Video file not found.")
                
                # Add assistant message to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "video_path": video_path,
                    "educational_breakdown": video_plan.get("educational_breakdown"),
                    "manim_structure": video_plan.get("manim_structure"),
                    "timestamp": time.time()
                })
                
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.write("Please try again with a different topic or check your configuration.")
            
            finally:
                st.session_state.processing = False
    else:
        st.warning("Please wait for the current animation to finish processing.")

# Minimal footer
st.markdown("---")
st.markdown("*EduGen - AI-powered science education*")