import pygame
import requests
import io
import time
import threading
from lastfm import (
    get_top_albums,
    get_top_tracks,
    get_top_artists,
    get_total_scrobbles,
    get_last_played,
    USER
)

# =========================
# Config
# =========================
WIDTH, HEIGHT = 480, 480
FPS = 30 
VIEW_DURATION = 30.0
FADE_SPEED = 8 # If higher = Faster transition

WEEKDAY_START, WEEKDAY_END = 13, 23
WEEKEND_START, WEEKEND_END = 11, 3

BG_COLOR = (18, 18, 18)
TEXT_COLOR = (240, 240, 240)
TEXT_DIM = (150, 150, 150)
BOX_COLOR = (45, 45, 45)
ACCENT_COLOR = (220, 60, 60)
LINE_COLOR = (80, 80, 80)

PADDING = 15
VIEWS = ["albums", "tracks", "artists"]

# =========================
# HELPER
# =========================
def is_display_time():
    now = time.localtime()
    h, wd = now.tm_hour, now.tm_wday
    if wd <= 4: return WEEKDAY_START <= h < WEEKDAY_END
    return h >= WEEKEND_START or h < WEEKEND_END

def create_rounded_image(surface, radius):
    if not surface: return None
    rect = surface.get_rect()
    mask = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask, (255, 255, 255), rect, border_radius=radius)
    new_surf = surface.copy()
    new_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return new_surf

# =========================
# SCROLLING LOGIK
# =========================
class ScrollingText:
    def __init__(self, text, font, color, max_w):
        safe_text = str(text) if text else "---"
        self.text_surf = font.render(safe_text, True, color).convert_alpha()
        self.max_w = max_w
        self.w = self.text_surf.get_width()
        self.h = self.text_surf.get_height()
        self.pos_x = 0
        self.scroll_speed = 1
        self.wait_timer = 60
        self.timer = self.wait_timer
        self.needs_scroll = self.w > max_w

    def update(self):
        if not self.needs_scroll: return
        if self.timer > 0:
            self.timer -= 1
        else:
            self.pos_x -= self.scroll_speed
            if self.pos_x < -self.w:
                self.pos_x = 10
                self.timer = 30

    def draw(self, target_surf, x, y):
        clip_surf = pygame.Surface((self.max_w, self.h + 5), pygame.SRCALPHA)
        if self.needs_scroll:
            clip_surf.blit(self.text_surf, (self.pos_x, 0))
        else:
            clip_surf.blit(self.text_surf, (0, 0))
        target_surf.blit(clip_surf, (x, y))

# =========================
# DATA MANAGER
# =========================
class DataManager:
    def __init__(self):
        self.data = {"scrobbles": "...", "last_played": {}, "albums": [], "tracks": [], "artists": []}
        self.images = {}
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        while self.running:
            if is_display_time():
                try:
                    sc = get_total_scrobbles()
                    lp = get_last_played()
                    al = get_top_albums(8)
                    tr = get_top_tracks(5)
                    ar = get_top_artists(5)
                    if lp: self._cache_image(lp.get("image_url"), 65)
                    if al: 
                        for a in al: self._cache_image(a.get("image_url"), 100)
                    with self.lock:
                        self.data.update({
                            "scrobbles": sc, "last_played": lp or {}, 
                            "albums": al or [], "tracks": tr or [], 
                            "artists": ar or [], "_timestamp": time.time()
                        })
                except: pass
            time.sleep(20)

    def _cache_image(self, url, size):
        if not url: return
        with self.lock:
            if url in self.images: return
        try:
            r = requests.get(url, timeout=5)
            self.images[url] = {"bytes": io.BytesIO(r.content), "size": size, "surf": None}
        except: pass

    def get_data(self):
        with self.lock: return self.data.copy()

    def get_image_surf(self, url):
        with self.lock:
            entry = self.images.get(url)
            if not entry: return None
            if entry["surf"]: return entry["surf"]
            try:
                entry["bytes"].seek(0)
                img = pygame.image.load(entry["bytes"]).convert_alpha()
                img = pygame.transform.smoothscale(img, (entry["size"], entry["size"]))
                entry["surf"] = img
                return img
            except: return None

# =========================
# MAIN APP
# =========================
class LastFMDisplay:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)
        self.clock = pygame.time.Clock()
        
        self.font_l = pygame.font.SysFont(None, 28)
        self.font_m = pygame.font.SysFont(None, 24)
        self.font_s = pygame.font.SysFont(None, 20)

        self.data_manager = DataManager()
        self.last_data_hash = 0
        self.current_view_idx = 0
        self.last_switch = time.time()
        self.view_surfaces = {}
        
        self.scroller_title = None
        self.scroller_artist = None
        
        # Fade Variables
        self.fade_alpha = 0
        self.prev_surface = None

    def render_base_surface(self, view_name, data):
        s = pygame.Surface((WIDTH, HEIGHT))
        s.fill(BG_COLOR)
        b_w, b_h = (WIDTH - 3 * PADDING) // 2, 130
        r_x = b_w + 2 * PADDING
        pygame.draw.rect(s, BOX_COLOR, (PADDING, PADDING, b_w, b_h), border_radius=10)
        pygame.draw.rect(s, BOX_COLOR, (r_x, PADDING, b_w, b_h), border_radius=10)
        s.blit(self.font_l.render(USER, True, ACCENT_COLOR), (PADDING + 12, PADDING + 12))
        s.blit(self.font_m.render(f"{data.get('scrobbles', '--')} Plays", True, TEXT_COLOR), (PADDING + 12, PADDING + 60))
        lp = data.get("last_played", {})
        s.blit(self.font_s.render("LAST PLAYED", True, ACCENT_COLOR), (r_x + 12, PADDING + 12))
        c_img = self.data_manager.get_image_surf(lp.get("image_url"))
        if c_img: s.blit(create_rounded_image(pygame.transform.smoothscale(c_img, (65, 65)), 6), (r_x + 12, PADDING + 45))
        else: pygame.draw.rect(s, (35, 35, 35), (r_x + 12, PADDING + 45, 65, 65), border_radius=6)
        h_y = 165
        t_map = {"albums": "TOP ALBUMS", "tracks": "TOP TRACKS", "artists": "TOP ARTISTS"}
        title_s = self.font_l.render(t_map.get(view_name, ""), True, ACCENT_COLOR)
        s.blit(title_s, ((WIDTH - title_s.get_width()) // 2, h_y))
        pygame.draw.line(s, LINE_COLOR, (PADDING, h_y + 28), (WIDTH - PADDING, h_y + 28), 1)
        y_c = h_y + 45
        if view_name == "albums":
            albs = data.get("albums", [])
            for i, a in enumerate(albs[:8]):
                ax = (WIDTH - (4 * 92 + 3 * 10)) // 2 + (i % 4) * 102
                ay = y_c + (i // 4) * 102
                ai = self.data_manager.get_image_surf(a.get("image_url"))
                if ai: s.blit(create_rounded_image(pygame.transform.smoothscale(ai, (92, 92)), 8), (ax, ay))
                else: pygame.draw.rect(s, (35, 35, 35), (ax, ay, 92, 92), border_radius=8)
        else:
            items = data.get("tracks" if view_name == "tracks" else "artists", [])
            for i, itm in enumerate(items[:5]):
                cy = y_c + i * 35
                name = itm.get('title', itm.get('name', 'Unknown'))
                s.blit(self.font_m.render(f"{i+1}. {name}", True, TEXT_COLOR), (40, cy), (0, 0, WIDTH-150, 30))
                p_s = self.font_s.render(f"{itm.get('plays', 0)} plays", True, TEXT_DIM)
                s.blit(p_s, (WIDTH - 40 - p_s.get_width(), cy + 2))
        return s

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): return

            if not is_display_time():
                self.screen.fill((0, 0, 0)); pygame.display.flip(); time.sleep(2); continue

            data = self.data_manager.get_data()
            ts = data.get("_timestamp", 0)
            if ts != self.last_data_hash:
                for v in VIEWS: self.view_surfaces[v] = self.render_base_surface(v, data)
                self.last_data_hash = ts
                lp = data.get("last_played", {})
                bw = (WIDTH - 3 * PADDING) // 2
                self.scroller_title = ScrollingText(lp.get("title", "---"), self.font_l, TEXT_COLOR, bw - 92)
                self.scroller_artist = ScrollingText(lp.get("artist", "---"), self.font_s, TEXT_DIM, bw - 92)

            now = time.time()
            if now - self.last_switch > VIEW_DURATION:
                # Creates a snapshot of the current screen, to make a smooth transition.
                self.prev_surface = self.screen.copy()
                self.fade_alpha = 255
                self.last_switch = now
                self.current_view_idx = (self.current_view_idx + 1) % len(VIEWS)

            # Drawing logic
            curr_v = VIEWS[self.current_view_idx]
            base = self.view_surfaces.get(curr_v)
            if base:
                self.screen.blit(base, (0, 0))
                rx = ((WIDTH - 3 * PADDING) // 2) + 2 * PADDING
                if self.scroller_title:
                    self.scroller_title.update(); self.scroller_title.draw(self.screen, rx + 85, PADDING + 45)
                if self.scroller_artist:
                    self.scroller_artist.update(); self.scroller_artist.draw(self.screen, rx + 85, PADDING + 75)

                # Cross-Fade Overlay
                if self.fade_alpha > 0 and self.prev_surface:
                    self.prev_surface.set_alpha(self.fade_alpha)
                    self.screen.blit(self.prev_surface, (0, 0))
                    self.fade_alpha -= FADE_SPEED

            pygame.display.flip()
            self.clock.tick(FPS)

if __name__ == "__main__":
    try: app = LastFMDisplay(); app.run()
    finally: pygame.quit()
