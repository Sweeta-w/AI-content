import streamlit as st
from groq import Groq

# Page Configuration
st.set_page_config(
    page_title="AI Content Assistant",
    page_icon="✨",
    layout="centered"
)

# App Title & Subtitle
st.title("✨ AI Content Assistant")
st.write("Generate high-converting posts, captions, and hashtags in seconds.")

# Securely retrieve Groq API Key from Streamlit Secrets or Sidebar Input
api_key = st.secrets.get("GROQ_API_KEY", "")

if not api_key:
    api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")
    st.sidebar.caption("Get your free key at [console.groq.com](https://console.groq.com/keys)")

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
        
    with col2:
        tone = st.selectbox(
            "Tone", 
            ["Professional", "Casual & Friendly", "Bold & Persuasive", "Witty & Humorous", "Inspirational"]
        )
        target_audience = st.text_input(
            "Target Audience", 
            placeholder="e.g., Software Engineers, Small Business Owners"
        )
    
    topic = st.text_area(
        "Topic / Key Points", 
        placeholder="e.g., Why learning Python in 2026 is still a game-changer for career growth."
    )
    
    submit_btn = st.form_submit_button("Generate Content 🚀")

# Generation Logic
if submit_btn:
    if not api_key:
        st.error("Please provide a valid Groq API Key to proceed.")
    elif not topic.strip():
        st.warning("Please enter a topic or key points for your post.")
    else:
        try:
            client = Groq(api_key=api_key)
            
            prompt = f"""
            You are an expert social media manager. Generate a complete, engaging social media post based on the following options:

            - Platform: {platform}
            - Content Type: {content_type}
            - Tone: {tone}
            - Target Audience: {target_audience if target_audience else 'General Audience'}
            - Topic: {topic}

            Structuring Requirements:
            1. Create an attention-grabbing hook suited for {platform}.
            2. Write the main content tailored for {target_audience if target_audience else 'General Audience'} using a {tone} tone.
            3. Include a clear Call to Action (CTA).
            4. Provide 5–8 relevant, trending hashtags at the bottom.
            """

            with st.spinner("Crafting your post..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a professional social media content creator."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                
                generated_post = response.choices[0].message.content

            st.success("Post Generated Successfully!")
            st.subheader("Your Generated Post")
            st.text_area("Copy your post:", generated_post, height=350)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")