import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from supabase import create_client, Client

st.set_page_config(page_title="🕊️ Prayer Library", layout="centered")
st.title("📖 Find Prayer Timestamps")

# Load Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("⚠️ Database not connected. Add Supabase secrets in Settings.")
    st.stop()

# Search Section
st.header("🔍 Search Video")
url = st.text_input("YouTube URL")
query = st.text_input("Search word (e.g., 'healing')")

if st.button("Search"):
    if url and query:
        match = re.search(r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})', url)
        if match:
            video_id = match.group(1)
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                st.success("✅ Found captions!")
                
                for seg in transcript[:3]:  # Show first 3 matches
                    if query.lower() in seg['text'].lower():
                        sec = int(seg['start'])
                        link = f"https://youtu.be/{video_id}?t={sec}"
                        st.markdown(f"⏱️ **{sec//60}:{sec%60:02d}** - {seg['text'][:100]}...")
                        st.link_button("🔗 Watch", link)
            except:
                st.error("❌ No captions available")
        else:
            st.error("Invalid URL")

st.header("📚 Community Library")
st.write("Coming soon - submit your prayer moments!")
