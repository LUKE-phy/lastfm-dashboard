import requests

# ===== Konfiguration =====
API_KEY = "YOUR_API_KEY"  # <-- Add your API Key.
USER = "YOUR_USER_NAME"    # <-- Enter your lastfm Username
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

# ===== Functions =====

def get_top_tracks(limit=5, period="7day"):
    params = {
        "method": "user.getTopTracks",
        "user": USER,
        "api_key": API_KEY,
        "format": "json",
        "limit": limit,
        "period": period
    }
    response = requests.get(BASE_URL, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()
    tracks = []
    for index, track in enumerate(data.get("toptracks", {}).get("track", []), start=1):
        image_url = track.get("image", [{}])[-1].get("#text")
        tracks.append({
            "rank": index,
            "title": track.get("name", ""),
            "artist": track.get("artist", {}).get("name", ""),
            "plays": int(track.get("playcount", 0)),
            "image_url": image_url
        })
    return tracks

def get_top_artists(limit=5, period="7day"):
    params = {
        "method": "user.getTopArtists",
        "user": USER,
        "api_key": API_KEY,
        "format": "json",
        "limit": limit,
        "period": period
    }
    response = requests.get(BASE_URL, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()
    artists = []
    for index, artist in enumerate(data.get("topartists", {}).get("artist", []), start=1):
        image_url = artist.get("image", [{}])[-1].get("#text")
        artists.append({
            "rank": index,
            "name": artist.get("name", ""),
            "plays": int(artist.get("playcount", 0)),
            "image_url": image_url
        })
    return artists

def get_top_albums(limit=8, period="7day"):
    params = {
        "method": "user.getTopAlbums",
        "user": USER,
        "api_key": API_KEY,
        "format": "json",
        "limit": limit,
        "period": period
    }
    response = requests.get(BASE_URL, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()
    albums = []
    for index, album in enumerate(data.get("topalbums", {}).get("album", []), start=1):
        image_url = album.get("image", [{}])[-1].get("#text")
        albums.append({
            "rank": index,
            "title": album.get("name", ""),
            "artist": album.get("artist", {}).get("name", ""),
            "plays": int(album.get("playcount", 0)),
            "image_url": image_url
        })
    return albums

def get_total_scrobbles():
    params = {
        "method": "user.getInfo",
        "user": USER,
        "api_key": API_KEY,
        "format": "json"
    }
    response = requests.get(BASE_URL, params=params, timeout=5)
    response.raise_for_status()
    data = response.json()
    return int(data.get("user", {}).get("playcount", 0))

def get_last_played():
    """Outputs the last played track""
    params = {
        "method": "user.getRecentTracks",
        "user": USER,
        "api_key": API_KEY,
        "format": "json",
        "limit": 1
    }
    response = requests.get(BASE_URL, params=params, timeout=5)
    try:
        response.raise_for_status()
        data = response.json()
        tracks = data.get("recenttracks", {}).get("track", [])
        if not tracks:
            return None
        track = tracks[0]
        return {
            "title": track.get("name", ""),
            "artist": track.get("artist", {}).get("#text", ""),
            "image_url": track.get("image", [{}])[-1].get("#text")
        }
    except Exception as e:
        print("Failure while loading last track:", e)
        return None
