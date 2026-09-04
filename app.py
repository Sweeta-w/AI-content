import re
import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(
    page_title="AI Content Assistant Pro",
    page_icon="✨",
    layout="centered"
)

# App Title
st.title("✨ AI Content Assistant Pro")
# Initialize generation history in session state
if "history" not in st.session_state:
    st.session_state["history"] = []
st.write("Generate high-converting posts, captions, hashtags, and visual prompts in seconds.")

# Securely retrieve Groq API Key
api_key = st.secrets.get("GROQ_API_KEY", "")

if not api_key:
    api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")
    st.sidebar.caption("Get your free key at console.groq.com")

# User Inputs Form
with st.form("content_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        platform = st.selectbox(
            "Platform", 
            ["LinkedIn", "Instagram", "Twitter / X", "Facebook", "YouTube Community"]
        )
        content_type = st.selectbox(
            "Content Type", 
            ["Educational", "Promotional", "Storytelling", "Thought Leadership", "Product Launch"]
        )
        language = st.selectbox(
            "Language",
            ["English", "Urdu", "Roman Urdu", "Spanish", "French"]
        )
        
    with col2:
        tone = st.selectbox(
            "Tone", 
            ["Professional", "Casual & Friendly", "Bold & Persuasive", "Witty & Humorous", "Inspirational"]
        )
        target_audience = st.text_input(
            "Target Audience", 
            placeholder="e.g., Software Engineers, Small Business Owners"
        )
        include_image_prompt = st.checkbox("Generate Matching Image Prompt", value=True)
    
    topic = st.text_area(
        "Topic / Key Points", 
        placeholder="e.g., Why learning Python in 2026 is still a game-changer for career growth."
    )
    
    submit_btn = st.form_submit_button("Generate Content 🚀")

# Generation Logic
# Generation Logic
if submit_btn:
    if not api_key:
        st.error("Please provide a valid Groq API Key to proceed.")
    elif not topic.strip():
        st.warning("Please enter a topic or key points for your post.")
    else:
        try:
            client = Groq(api_key=api_key)
            
            # Fixed Image Prompt Directive
            image_instruction = (
                "\n\nALSO PROVIDE A MATCHING IMAGE PROMPT AT THE VERY END:\n"
                "IMAGE PROMPT: A detailed, high-quality prompt for Midjourney/DALL-E describing a matching visual for this post."
                if include_image_prompt else ""
            )

            prompt = f"""
            You are an expert social media manager. Generate a complete, engaging social media post based on the following options:

            - Platform: {platform}
            - Content Type: {content_type}
            - Tone: {tone}
            - Target Audience: {target_audience if target_audience else 'General Audience'}
            - Language: {language}
            - Topic: {topic}

            CRITICAL FORMATTING INSTRUCTIONS:
            - Write the post in {language}.
            - Do NOT use markdown symbols like asterisks (**), hashtags for headings (#), or underscores in the main post.
            - Write in plain text format suitable for direct copy-pasting.
            - Use standard emojis for visual emphasis instead of markdown bolding.
            - Provide 5–8 relevant hashtags at the bottom of the post.
            {image_instruction}
            """

            with st.spinner("Crafting your post..."):
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[
                        {"role": "system", "content": "You are a professional social media content creator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1200
                )
                
                raw_text = response.choices[0].message.content
                clean_text = re.sub(r'\*+', '', raw_text)
                
                st.session_state["generated_post"] = clean_text
                st.session_state["post_platform"] = platform
                
                # Append to history list
                st.session_state["history"].append({
                    "platform": platform,
                    "topic": topic[:30] + "..." if len(topic) > 30 else topic,
                    "content": clean_text
                })

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
# Display Generated Output, Analytics & Export Options
if "generated_post" in st.session_state:
    post_text = st.session_state["generated_post"]
    selected_platform = st.session_state.get("post_platform", "LinkedIn")
    
    st.success("Post Generated Successfully!")
    
    # Character & Word Analytics
    char_count = len(post_text)
    word_count = len(post_text.split())
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Character Count", char_count)
    col_m2.metric("Word Count", word_count)
    
    # Platform Limit Checks
    limits = {"Twitter / X": 280, "LinkedIn": 3000, "Instagram": 2200, "Facebook": 63206}
    platform_limit = limits.get(selected_platform, 3000)
    
    if char_count > platform_limit:
        col_m3.error(f"Exceeds {selected_platform} limit ({platform_limit} chars)!")
    else:
        col_m3.success(f"Within {selected_platform} limit")

    st.subheader("Your Generated Post")
    st.code(post_text, language="text")

    # File Download Options
    file_prefix = selected_platform.lower().replace(" / ", "_").replace(" ", "_")
    
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📄 Download .txt",
            data=post_text,
            file_name=f"{file_prefix}_post.txt",
            mime="text/plain",
            use_container_width=True
        )
        
    with col_dl2:
        st.download_button(
            label="📝 Download .md",
            data=post_text,
            file_name=f"{file_prefix}_post.md",
            mime="text/markdown",
            use_container_width=True
        )
# Sidebar History Display
if st.session_state["history"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📜 Generation History")
    
    for idx, item in enumerate(reversed(st.session_state["history"])):
        with st.sidebar.expander(f"#{len(st.session_state['history']) - idx}: {item['platform']} - {item['topic']}"):
            st.code(item["content"], language="text")
