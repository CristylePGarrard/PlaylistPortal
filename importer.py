
import pandas as pd

COLUMN_ALIASES = {
    "playlist_name": ["playlist_name", "playlist", "playlist title"],
    "track_name": ["track_name", "title", "track", "song"],
    "artist_name": ["artist_name", "artist", "artists"],
    "album_name": ["album_name", "album"],
    "position": ["position", "track_number", "track number", "index"],
}


def normalize_tracks(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize common playlist CSV column names."""
    df = df.copy()

    # Standardize headers
    df.columns = [
        str(column).strip().lower().replace("-", "_")
        for column in df.columns
    ]

    rename = {}
    for standard_name, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in df.columns:
                rename[alias] = standard_name
                break

    df = df.rename(columns=rename)

    required = ["playlist_name", "track_name", "artist_name"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
            + ". Required: playlist_name, track_name, artist_name."
        )

    if "album_name" not in df.columns:
        df["album_name"] = ""

    if "position" not in df.columns:
        df["position"] = range(1, len(df) + 1)

    for col in ["playlist_name", "track_name", "artist_name", "album_name"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df = df[
        (df["playlist_name"] != "")
        & (df["track_name"] != "")
        & (df["artist_name"] != "")
    ].copy()

    df["position"] = pd.to_numeric(
        df["position"], errors="coerce"
    )

    return df.sort_values(
        ["playlist_name", "position"],
        kind="stable",
        na_position="last",
    ).reset_index(drop=True)

