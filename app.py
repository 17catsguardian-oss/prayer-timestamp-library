import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
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

# Search Section
st.header("🔍 Search Video")
url = st.text_input("YouTube URL (Pastor Jerry Eze)")
query = st.text_input("Search word (e.g., 'healing', 'down syndrome')")

if st.button("Search"):
    if url and query:
        match = re.search(r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})', url)
        if match:
            video_id = match.group(1)
            with st.spinner("🔍 Fetching captions..."):
                try:
                    # Try to get transcript (works for live & regular videos)
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                    
                    # Search for matches
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
                    
                    if matches:
                        st.success(f"✅ Found {len(matches)} match(es)!")
                        for m in matches:
                            with st.container(border=True):
                                st.markdown(f"⏱️ **{m['time']}**")
                                st.write(f"*{m['text']}*")
                                st.link_button("🔗 Watch on YouTube", m['link'])
                    else:
                        st.warning(f"🔍 No matches for '{query}' in this video")
                        
                except TranscriptsDisabled:
                    st.error("❌ Captions are disabled for this video")
                except NoTranscriptFound:
                    st.error("❌ No captions found. Try again in 1-3 hours after the live stream ends.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.error("Invalid YouTube URL")

st.divider()
st.header("📚 Community Library")
st.info("Coming soon - submit and browse prayer moments!")
