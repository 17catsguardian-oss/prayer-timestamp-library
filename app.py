import streamlit as st
import re
import urllib.request
import json
from supabase import create_client, Client

st.set_page_config(page_title="🕊️ Prayer Library", layout="centered")
st.title("📖 Find Prayer Timestamps")

# Load Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    st.error("⚠️ Database not connected.")
    st.stop()

def get_captions_youtube_api(video_id):
    """Try to get captions using YouTube's public API"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
        
        # Look for caption tracks in the page
        if '"captionTracks"' in html:
            return True
        return False
    except:
        return False

def search_in_captions_simple(video_id, query):
    """Simple search using youtube-transcript-api"""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        
        matches = []
        query_lower = query.lower()
        
        for seg in transcript:
            text = seg.get('text', '').lower()
            if query_lower in text:
                sec = int(seg.get('start', 0))
                matches.append({
                    'time': f"{sec//60:02d}:{sec%60:02d}",
                    'text': seg.get('text', ''),
                    'link': f"https://youtu.be/{video_id}?t={sec}"
                })
                if len(matches) >= 3:
                    break
        
        return matches, None
    except Exception as e:
        return [], str(e)

# Search Section
st.header("🔍 Search Video")
url = st.text_input("YouTube URL (Pastor Jerry Eze)")
query = st.text_input("Search word (e.g., 'healing', 'ADHD')")

if st.button("Search"):
    if url and query:
        # Extract video ID more carefully
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11})',
            r'youtu\.be\/([0-9A-Za-z_-]{11})',
            r'live\/([0-9A-Za-z_-]{11})'
        ]
        
        video_id = None
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                break
        
        if video_id:
            st.info(f"🎬 Video ID: {video_id}")
            
            with st.spinner("🔍 Checking for captions..."):
                # First check if captions exist
                has_captions = get_captions_youtube_api(video_id)
                
                if not has_captions:
                    st.warning("⚠️ YouTube shows this video has no public captions track.")
                    st.info("💡 Note: Even if you see CC on YouTube, the auto-captions might not be saved as a public track yet.")
                
                with st.spinner("🔍 Searching captions..."):
                    matches, error = search_in_captions_simple(video_id, query)
                    
                    if matches:
                        st.success(f"✅ Found {len(matches)} match(es)!")
                        for m in matches:
                            with st.container(border=True):
                                st.markdown(f"⏱️ **{m['time']}**")
                                st.write(f"*{m['text']}*")
                                st.link_button("🔗 Watch on YouTube", m['link'])
                    elif error:
                        st.error(f"❌ Could not fetch captions: {error}")
                        st.info("💡 This video might not have captions available via API yet. Try a different video or wait a few hours.")
                    else:
                        st.warning(f"🔍 No matches found for '{query}'")
        else:
            st.error("❌ Could not extract video ID from URL")

st.divider()
st.header("📚 Community Library")
st.info("Coming soon - submit and browse prayer moments!")
