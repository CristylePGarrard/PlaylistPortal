import pandas as pd
import streamlit as st

from src.importer import normalize_tracks

st.set_page_config(
    page_title="Playlist Portal",
    page_icon="🎧",
    layout="wide",
)

st.title("🎧 Playlist Portal")
st.caption("Your music library, ready for its next destination.")

uploaded_file = st.file_uploader(
    "Import your playlist library",
    type=["csv"],
    help="Upload a CSV with playlist, track, and artist columns.",
)

if uploaded_file is None:
    st.info("Upload a CSV to explore your music library.")

    st.markdown(
        """
        **Supported input:** CSV files containing playlist names,
        song titles, and artists.

        **Coming next:** Spotify JSON imports, YouTube matching,
        and migration progress tracking.
        """
    )
    st.stop()

try:
    raw_df = pd.read_csv(uploaded_file)
    tracks = normalize_tracks(raw_df)
except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
    st.error(f"Couldn't import this file: {exc}")
    st.stop()

if tracks.empty:
    st.warning("No usable tracks found. Check your CSV and try again.")
    st.stop()

st.success(f"Imported {len(tracks):,} track entries.")

total_playlists = tracks["playlist_name"].nunique()
unique_songs = tracks[
    ["track_name", "artist_name"]
].drop_duplicates().shape[0]

col1, col2, col3 = st.columns(3)
col1.metric("Playlists", f"{total_playlists:,}")
col2.metric("Track entries", f"{len(tracks):,}")
col3.metric("Unique song/artist pairs", f"{unique_songs:,}")

st.subheader("Your playlists")

summary = (
    tracks.groupby("playlist_name")
    .agg(
        track_count=("track_name", "size"),
        unique_songs=("track_name", "nunique"),
    )
    .reset_index()
    .sort_values("playlist_name")
)

st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader("Explore a playlist")

selected_playlist = st.selectbox(
    "Choose a playlist",
    summary["playlist_name"].tolist(),
)

playlist_tracks = tracks[
    tracks["playlist_name"] == selected_playlist
].copy()

st.dataframe(
    playlist_tracks[
        ["position", "track_name", "artist_name", "album_name"]
    ],
    use_container_width=True,
    hide_index=True,
)

csv_data = tracks.to_csv(index=False).encode("utf-8")

st.download_button(
    "Export normalized library",
    data=csv_data,
    file_name="playlist_portal_library.csv",
    mime="text/csv",
)

