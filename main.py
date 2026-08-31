from matplotlib.figure import Figure
import tkinter as tk
import customtkinter as ctk
"""
CipherDit Receiver — Professional Wireless Morse Decoder
Change PORT to match your Arduino COM port.
Run: python cipherdit_receiver.py
"""

import re, time, threading, random, serial
from collections import deque
import tkinter as tk
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as ticker

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
PORT             = "COM7"
BAUD             = 115200
MAX_RSSI_HISTORY = 300
SIGNAL_BARS      = 28
WAVE_REPEAT      = 8

# ─────────────────────────────────────────────
# MORSE CODE
# ─────────────────────────────────────────────
MORSE_CODE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',   'E': '.',
    'F': '..-.',  'G': '--.',   'H': '....',  'I': '..',    'J': '.---',
    'K': '-.-',   'L': '.-..',  'M': '--',    'N': '-.',    'O': '---',
    'P': '.--.',  'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',  'Y': '-.--',
    'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
    '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
    '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-',
    '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.',
    '$': '...-..-', '@': '.--.-.'
}

# ─────────────────────────────────────────────
# CIPHER
# ─────────────────────────────────────────────
CIPHER = {
    'Q':'A','W':'B','X':'C','Y':'D','Z':'E','J':'F','K':'G','V':'H',
    'U':'I','T':'J','S':'K','R':'L','P':'M','O':'N','N':'O','M':'P',
    'L':'Q','I':'R','H':'S','G':'T','F':'U','E':'V','D':'W','C':'X',
    'B':'Y','A':'Z',
    '9':'0','8':'1','7':'2','6':'3','5':'4','4':'5','3':'6','2':'7','1':'8','0':'9'
}
def decipher(ch):
    return CIPHER.get(ch.upper(), ch)

# ─────────────────────────────────────────────
# STRESS CODES  (decoded text substring → alert level)
# ─────────────────────────────────────────────
STRESS_CODES = {
    "SOS": {
        "level": 3,
        "label": "🚨  SOS — DISTRESS SIGNAL DETECTED",
        "bg":    "#1a0000",
        "border":"FF3C5A",
        "text":  "FF3C5A",
        "app_bg":"#200000",
        "title": "SOS — CIPHERDIT ALERT",
    },
    "XXX": {
        "level": 2,
        "label": "⚠  XXX — URGENT / IMMINENT DANGER",
        "bg":    "#1a0f00",
        "border":"FF8800",
        "text":  "FF8800",
        "app_bg":"#1f1000",
        "title": "XXX ALERT — CIPHERDIT",
    },
    "TTT": {
        "level": 1,
        "label": "ℹ  TTT — SAFETY ADVISORY / WARNING",
        "bg":    "#001a0f",
        "border":"00FF88",
        "text":  "00FF88",
        "app_bg":"#001510",
        "title": "TTT ADVISORY — CIPHERDIT",
    },
}

# ─────────────────────────────────────────────
# THEME (normal state)
# ─────────────────────────────────────────────
# Light application theme with bright green/blue accents
BG      = "#f3fbff"   # very light bluish background
PANEL   = "#ffffff"   # white panels
BORDER  = "#d0eef7"   # pale blue border
GLOW    = "#00ff66"   # bright green accent
GLOW2   = "#00bfff"   # bright blue accent
DANGER  = "#ff3c5a"   # red for alerts
WARN    = "#ffb84d"   # warm warning
TEXT    = "#072029"   # dark teal text for readability
TEXTDIM = "#2b6b7a"   # dim blue-green text
FMO     = "Courier New"

ctk.set_appearance_mode("light")

# ─────────────────────────────────────────────
# WINDOW
# ─────────────────────────────────────────────
app = ctk.CTk()
app.title("CipherDit  //  Covert Morse Receiver")
app.geometry("1120x780")
app.minsize(920, 660)
app.configure(fg_color=BG)

# ─────────────────────────────────────────────
# TITLE BAR
# ─────────────────────────────────────────────
tb = ctk.CTkFrame(app, fg_color=PANEL, corner_radius=0, height=62)
tb.pack(fill="x", side="top")
tb.pack_propagate(False)

title_lbl = ctk.CTkLabel(tb, text="◈  CIPHERDIT",
    font=(FMO,24,"bold"), text_color=GLOW)
title_lbl.pack(side="left", padx=22, pady=10)

sub_lbl = ctk.CTkLabel(tb, text="COVERT MORSE RECEIVER  //  2.4GHz NRF24L01+",
    font=(FMO,11), text_color=TEXTDIM)
sub_lbl.pack(side="left")

enc_mode = ctk.StringVar(value="Cipher ON")
ctk.CTkSegmentedButton(
    tb, values=["Cipher ON","Cipher OFF"], variable=enc_mode,
    font=(FMO,11), fg_color=PANEL, selected_color="#0f3340",
    selected_hover_color="#1a4a58", unselected_color=PANEL,
    text_color=GLOW, width=200,
).pack(side="right", padx=20)

status_txt = ctk.CTkLabel(tb, text="OFFLINE", font=(FMO,11), text_color=DANGER)
status_txt.pack(side="right", padx=(0,6))
sdot_cv = tk.Canvas(tb, width=14, height=14, bg=PANEL, highlightthickness=0)
sdot_cv.pack(side="right", padx=(0,4), pady=24)
sdot = sdot_cv.create_oval(2,2,12,12, fill=DANGER, outline="")

# ─────────────────────────────────────────────
# ALERT BANNER (hidden by default)
# ─────────────────────────────────────────────
alert_bar = ctk.CTkFrame(app, fg_color="#1a0000", corner_radius=0, height=52)
# NOT packed yet — shown only on alert

alert_inner = ctk.CTkFrame(alert_bar, fg_color="transparent")
alert_inner.pack(fill="both", expand=True, padx=12, pady=6)
alert_inner.columnconfigure(0, weight=1)

alert_lbl = ctk.CTkLabel(alert_inner, text="",
    font=(FMO,14,"bold"), text_color=DANGER, anchor="w")
alert_lbl.grid(row=0, column=0, sticky="w")

ack_btn = ctk.CTkButton(
    alert_inner, text="✓  ACKNOWLEDGE & CLEAR",
    font=(FMO,11,"bold"), width=200, height=34,
    fg_color="#2a0000", hover_color="#3a0000",
    border_color=DANGER, border_width=1,
    text_color=DANGER, corner_radius=4,
    command=lambda: acknowledge_alert()
)
ack_btn.grid(row=0, column=1, sticky="e", padx=(10,0))

# ─────────────────────────────────────────────
# MAIN LAYOUT
# ─────────────────────────────────────────────
main = ctk.CTkFrame(app, fg_color=BG)
main.pack(fill="both", expand=True, padx=14, pady=10)
main.columnconfigure(0, weight=3)
main.columnconfigure(1, weight=2)
main.rowconfigure(0, weight=1)

left = ctk.CTkFrame(main, fg_color=BG)
left.grid(row=0, column=0, sticky="nsew", padx=(0,8))
left.columnconfigure(0, weight=1)
left.rowconfigure(3, weight=1)
left.rowconfigure(7, weight=2)

right = ctk.CTkFrame(main, fg_color=BG)
right.grid(row=0, column=1, sticky="nsew")
right.columnconfigure(0, weight=1)
right.rowconfigure(1, weight=1)

ALL_FRAMES = []   # register for theme changes

def sec_lbl(p, txt, row):
    l = ctk.CTkLabel(p, text=f"▸ {txt}", font=(FMO,10),
                     text_color=TEXTDIM, anchor="w")
    l.grid(row=row, column=0, sticky="w", padx=4, pady=(8,2))
    return l

def sec_box(p, h, row, color=TEXT):
    b = ctk.CTkTextbox(p, height=h, font=(FMO,13), fg_color=PANEL,
                        text_color=color, border_color=BORDER, border_width=1,
                        corner_radius=4, wrap="word", scrollbar_button_color=BORDER)
    b.grid(row=row, column=0, sticky="nsew", padx=4, pady=2)
    ALL_FRAMES.append(b)
    return b

# ─────────────────────────────────────────────
# SIGNAL BAR
# ─────────────────────────────────────────────
sec_lbl(left, "SIGNAL INTENSITY", 0)

sig_outer = ctk.CTkFrame(left, fg_color=PANEL, border_color=BORDER,
                          border_width=1, corner_radius=4, height=38)
sig_outer.grid(row=1, column=0, sticky="ew", padx=4, pady=2)
sig_outer.pack_propagate(False)
sig_outer.columnconfigure(1, weight=1)

ctk.CTkLabel(sig_outer, text="SIGNAL:", font=(FMO,11), text_color=TEXTDIM,
             width=70).grid(row=0, column=0, padx=(10,4), pady=8, sticky="w")

sig_cv = tk.Canvas(sig_outer, height=22, bg=PANEL, highlightthickness=0)
sig_cv.grid(row=0, column=1, sticky="ew", padx=4, pady=8)

sig_dbm = ctk.CTkLabel(sig_outer, text="-100 dBm", font=(FMO,10),
                         text_color=TEXTDIM, width=72)
sig_dbm.grid(row=0, column=2, padx=(4,10), pady=8, sticky="e")

seg_rects    = []
_cur_rssi    = -100
_letter_bump = 0   # extra bump level when a letter arrives

def build_segs(event=None):
    global seg_rects
    sig_cv.delete("all")
    seg_rects = []
    w = sig_cv.winfo_width()
    if w < 10:
        return
    gap   = 3
    sw    = max(4, (w - gap*(SIGNAL_BARS-1)) // SIGNAL_BARS)
    for i in range(SIGNAL_BARS):
        x1 = i*(sw+gap)
        x2 = x1+sw
        r  = sig_cv.create_rectangle(x1,2,x2,20, fill="#0d1f26", outline="")
        seg_rects.append(r)
    _draw_segs(_cur_rssi)

sig_cv.bind("<Configure>", build_segs)

def _rssi_pct(rssi):
    return max(0.0, min(1.0, (rssi+100)/80.0))

def _seg_color(i, lit_count):
    frac = (i+1)/SIGNAL_BARS
    noise = random.random()
    if frac < 0.5:
        return GLOW if noise > 0.18 else "#009988"
    elif frac < 0.75:
        return "#ffcc00" if noise > 0.22 else "#cc9900"
    else:
        return DANGER if noise > 0.28 else "#cc1a30"

def _draw_segs(rssi, extra=0):
    if not seg_rects:
        return
    pct  = _rssi_pct(rssi)
    lit  = int(pct * SIGNAL_BARS) + extra + random.randint(-1,1)
    lit  = max(0, min(SIGNAL_BARS, lit))
    for i, r in enumerate(seg_rects):
        sig_cv.itemconfig(r, fill=_seg_color(i,lit) if i<lit else "#0d1f26")
    sig_dbm.configure(text=f"{rssi} dBm")

def animate_sig():
    global _letter_bump
    _draw_segs(_cur_rssi, _letter_bump)
    if _letter_bump > 0:
        _letter_bump = max(0, _letter_bump - 1)
    app.after(110, animate_sig)

def letter_bump():
    """Call when a letter arrives to spike the bar."""
    global _letter_bump
    _letter_bump = random.randint(4, 8)

# ─────────────────────────────────────────────
# GRAPH
# ─────────────────────────────────────────────
sec_lbl(left, "SIGNAL WAVEFORM", 2)

gframe = ctk.CTkFrame(left, fg_color=PANEL, border_color=BORDER,
                       border_width=1, corner_radius=4)
gframe.grid(row=3, column=0, sticky="nsew", padx=4, pady=2)

fig = Figure(facecolor=PANEL)
ax  = fig.add_subplot(111)
ax.set_facecolor("#000000")
ax.set_ylim(-0.1, 1.2)
ax.set_xlim(0,MAX_RSSI_HISTORY)
ax.tick_params(colors=TEXTDIM, labelsize=8)
ax.set_ylabel("level", color=TEXTDIM, fontsize=9)
ax.set_xlabel("samples →", color=TEXTDIM, fontsize=8)
for sp in ax.spines.values():
    sp.set_edgecolor(BORDER)
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
# square grid both axes
ax.grid(True, color="#3a3a3a", linewidth=0.6, linestyle='--')
# make x/y tick labels use dim text color
ax.tick_params(axis='x', colors=TEXTDIM)
ax.tick_params(axis='y', colors=TEXTDIM)
fig.tight_layout(pad=0.9)

wave_data  = deque([0.0]*MAX_RSSI_HISTORY, maxlen=MAX_RSSI_HISTORY)
analog_data = deque([0.0]*MAX_RSSI_HISTORY, maxlen=MAX_RSSI_HISTORY)
xdata      = list(range(MAX_RSSI_HISTORY))
line_rssi, = ax.plot(xdata, list(wave_data), color=GLOW, linewidth=1.8, alpha=0.95, drawstyle="steps-post")
analog_line, = ax.plot(xdata, list(analog_data), color="#ff6b6b", linewidth=1.1, alpha=0.9)
fill_rssi  = ax.fill_between(xdata, list(wave_data), 0, color=GLOW, alpha=0.07, step="post")

cgraph = FigureCanvasTkAgg(fig, master=gframe)
cgraph.get_tk_widget().pack(fill="both", expand=True)
cgraph.draw()

def refresh_graph():
    global fill_rssi
    yd = list(wave_data)
    line_rssi.set_ydata(yd)
    # update analog noisy trace
    ad = list(analog_data)
    try:
        analog_line.set_ydata(ad)
    except Exception:
        pass
    fill_rssi.remove()
    fill_rssi = ax.fill_between(xdata, yd, 0, color=GLOW, alpha=0.07, step="post")
    cgraph.draw_idle()

def push_wave(level, repeat=WAVE_REPEAT):
    for _ in range(repeat):
        wave_data.append(level)
        # produce an analog/noisy sample that follows the digital level
        # use previous analog value to smooth transitions
        prev = analog_data[-1] if len(analog_data) else 0.0
        # noise magnitude slightly larger for high state to show variance
        noise = random.uniform(-0.15, 0.12) if level >= 0.5 else random.uniform(-0.06, 0.06)
        target = float(level) + noise
        # exponential smoothing towards target for realistic transitions
        analog = prev * 0.75 + target * 0.25
        analog_data.append(analog)

def feed_wave_from_text(text):
    for ch in text:
        ch_upper = ch.upper()
        if ch_upper in MORSE_CODE:
            # Convert letter to Morse code and push dot/dash pulses
            morse = MORSE_CODE[ch_upper]
            for symbol in morse:
                if symbol == '.':
                    # Dot: short high pulse
                    push_wave(1.0, repeat=WAVE_REPEAT)
                    push_wave(0.0, repeat=WAVE_REPEAT // 2)
                elif symbol == '-':
                    # Dash: long high pulse (3x dot duration)
                    push_wave(1.0, repeat=WAVE_REPEAT * 3)
                    push_wave(0.0, repeat=WAVE_REPEAT // 2)
            # Gap between letters
            push_wave(0.0, repeat=WAVE_REPEAT)
        elif ch.isspace():
            # Longer gap for spaces between words
            push_wave(0.0, repeat=WAVE_REPEAT * 2)
        else:
            # Unknown characters just stay low
            push_wave(0.0, repeat=WAVE_REPEAT // 2)

# ─────────────────────────────────────────────
# RAW BOX
# ─────────────────────────────────────────────
sec_lbl(left, "ENCRYPTED INCOMING  (raw cipher)", 4)
raw_box = sec_box(left, 80, 5)

# ─────────────────────────────────────────────
# PLAIN BOX
# ─────────────────────────────────────────────
sec_lbl(left, "DECRYPTED MESSAGE", 6)
plain_box = ctk.CTkTextbox(
    left, height=140, font=(FMO,22,"bold"),
    fg_color=PANEL, text_color=GLOW,
    border_color=GLOW, border_width=1,
    corner_radius=4, wrap="word",
    scrollbar_button_color=BORDER,
)
plain_box.grid(row=7, column=0, sticky="nsew", padx=4, pady=2)

# ─────────────────────────────────────────────
# STATS
# ─────────────────────────────────────────────
sec_lbl(right, "LINK STATISTICS", 0)
sf = ctk.CTkFrame(right, fg_color=PANEL, border_color=BORDER, border_width=1, corner_radius=4)
sf.grid(row=1, column=0, sticky="nsew", padx=4, pady=2)
sf.columnconfigure(0, weight=1)

def stat_row(p, lbl, row):
    ctk.CTkLabel(p, text=lbl, font=(FMO,10), text_color=TEXTDIM, anchor="w"
                 ).grid(row=row*2, column=0, sticky="w", padx=14, pady=(10,0))
    v = ctk.CTkLabel(p, text="—", font=(FMO,16,"bold"), text_color=GLOW, anchor="w")
    v.grid(row=row*2+1, column=0, sticky="w", padx=14, pady=(0,4))
    return v

v_rssi  = stat_row(sf, "RSSI (dBm)",         0)
v_chars = stat_row(sf, "CHARS RECEIVED",     1)
v_dec   = stat_row(sf, "CHARS DECRYPTED",    2)
v_rate  = stat_row(sf, "MSG RATE (msg/min)", 3)
v_up    = stat_row(sf, "UPTIME",             4)
v_port  = stat_row(sf, "PORT / BAUD",        5)

# stress code indicator (normal state hidden)
stress_frm = ctk.CTkFrame(right, fg_color="#0a0a0a", border_color=TEXTDIM,
                            border_width=1, corner_radius=4, height=50)
stress_frm.grid(row=2, column=0, sticky="ew", padx=4, pady=(8,4))
stress_frm.pack_propagate(False)
stress_lbl = ctk.CTkLabel(stress_frm, text="● NO ALERT",
                            font=(FMO,13,"bold"), text_color=TEXTDIM)
stress_lbl.pack(expand=True)

# buttons
br = ctk.CTkFrame(right, fg_color=BG)
br.grid(row=3, column=0, sticky="ew", padx=4, pady=4)
br.columnconfigure(0, weight=1); br.columnconfigure(1, weight=1)

def mk_btn(txt, cmd, col):
    ctk.CTkButton(br, text=txt, command=cmd, font=(FMO,11),
                  fg_color=PANEL, hover_color="#1a3340",
                  border_color=BORDER, border_width=1,
                  text_color=GLOW, corner_radius=4, height=32
                  ).grid(row=0, column=col, sticky="ew", padx=4)

def clear_all():
    raw_box.delete("1.0","end")
    plain_box.delete("1.0","end")
    st["chars"]=0; st["dec"]=0

def copy_msg():
    app.clipboard_clear()
    app.clipboard_append(plain_box.get("1.0","end").strip())

mk_btn("⌫  CLEAR",    clear_all, 0)
mk_btn("⎘  COPY MSG", copy_msg,  1)

sec_lbl(right, "EVENT LOG", 4)
log_box = sec_box(right, 110, 5, TEXTDIM)

# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
st            = {"chars":0,"dec":0,"rssi":-100,"msgs":deque(maxlen=60)}
t0            = time.time()
current_alert = None   # None or key from STRESS_CODES
blink_job     = None
blink_on      = False

def check_stress_codes_text(text):
    clean = re.sub(r"\s+", "", text).upper()
    tail = clean[-10:]
    for code in sorted(STRESS_CODES, key=lambda k: STRESS_CODES[k]["level"], reverse=True):
        if code in tail:
            if current_alert != code:
                trigger_alert(code)
            return

# ─────────────────────────────────────────────
# LETTER HANDLER
# ─────────────────────────────────────────────
def add_letter(ch):
    plain_box.insert("end", ch.upper())
    plain_box.see("end")
    letter_bump()
    check_stress_codes_text(plain_box.get("1.0", "end"))

def check_stress_codes():
    """Check last 10 chars of decoded text for any stress code substring."""
    check_stress_codes_text(plain_box.get("1.0", "end"))

# ─────────────────────────────────────────────
# ALERT SYSTEM
# ─────────────────────────────────────────────
def trigger_alert(code):
    global current_alert, blink_job, blink_on
    current_alert = code
    cfg = STRESS_CODES[code]

    log_event(f"🚨 STRESS CODE [{code}] DETECTED — Level {cfg['level']}")
    app.title(cfg["title"])

    # show alert banner
    alert_bar.configure(fg_color=cfg["bg"])
    alert_lbl.configure(text=cfg["label"], text_color=f"#{cfg['text']}")
    ack_btn.configure(fg_color=cfg["bg"], border_color=f"#{cfg['border']}",
                      text_color=f"#{cfg['text']}", hover_color=f"#{cfg['border']}22")
    alert_bar.pack(fill="x", after=tb)

    # recolor whole interface
    _apply_alert_theme(cfg)

    # start blinking stress indicator
    if blink_job:
        app.after_cancel(blink_job)
    _blink_stress(cfg)

def _apply_alert_theme(cfg):
    col_bg     = cfg["app_bg"]
    col_border = f"#{cfg['border']}"
    col_text   = f"#{cfg['text']}"

    app.configure(fg_color=col_bg)
    main.configure(fg_color=col_bg)
    left.configure(fg_color=col_bg)
    right.configure(fg_color=col_bg)
    tb.configure(fg_color=cfg["bg"])
    title_lbl.configure(text_color=col_text)

    stress_frm.configure(fg_color=cfg["bg"], border_color=col_border)
    stress_lbl.configure(text=cfg["label"], text_color=col_text)

    plain_box.configure(text_color=col_text, border_color=col_border)
    raw_box.configure(text_color=col_text, border_color=col_border)
    sig_outer.configure(border_color=col_border)

def _blink_stress(cfg):
    global blink_job, blink_on
    if current_alert != list(STRESS_CODES.keys())[list(STRESS_CODES.values()).index(cfg)] \
       if cfg in STRESS_CODES.values() else True:
        pass
    blink_on = not blink_on
    col = f"#{cfg['text']}" if blink_on else f"#{cfg['border']}55"
    stress_lbl.configure(text_color=col)
    alert_lbl.configure(text_color=col)
    speed = 300 if cfg["level"]==3 else 500 if cfg["level"]==2 else 800
    blink_job = app.after(speed, lambda: _blink_stress(cfg))

def acknowledge_alert():
    global current_alert, blink_job, blink_on
    if blink_job:
        app.after_cancel(blink_job)
        blink_job = None

    prev = current_alert
    current_alert = None
    blink_on = False

    log_event(f"✓ Alert [{prev}] acknowledged by operator")
    app.title("CipherDit  //  Covert Morse Receiver")

    # hide banner
    alert_bar.pack_forget()

    # restore normal theme
    app.configure(fg_color=BG)
    main.configure(fg_color=BG)
    left.configure(fg_color=BG)
    right.configure(fg_color=BG)
    tb.configure(fg_color=PANEL)
    title_lbl.configure(text_color=GLOW)

    stress_frm.configure(fg_color="#0a0a0a", border_color=TEXTDIM)
    stress_lbl.configure(text="● NO ALERT", text_color=TEXTDIM)

    plain_box.configure(text_color=GLOW, border_color=GLOW)
    raw_box.configure(text_color=TEXT, border_color=BORDER)
    sig_outer.configure(border_color=BORDER)

# ─────────────────────────────────────────────
# STATS TICKER
# ─────────────────────────────────────────────
def tick():
    e = int(time.time()-t0)
    h,r = divmod(e,3600); m,s = divmod(r,60)
    rate = len([x for x in st["msgs"] if time.time()-x<60])
    v_rssi.configure(text=f"{st['rssi']} dBm")
    v_chars.configure(text=str(st["chars"]))
    v_dec.configure(text=str(st["dec"]))
    v_rate.configure(text=str(rate))
    v_up.configure(text=f"{h:02d}:{m:02d}:{s:02d}")
    app.after(1000, tick)

def log_event(msg):
    t = time.strftime("%H:%M:%S")
    app.after(0, lambda: (
        log_box.insert("end", f"[{t}] {msg}\n"),
        log_box.see("end")
    ))

# ─────────────────────────────────────────────
# SERIAL
# ─────────────────────────────────────────────
ser = None

def connect_serial():
    global ser
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        app.after(0, lambda: (
            status_txt.configure(text=f"LIVE  {PORT}", text_color=GLOW),
            sdot_cv.itemconfig(sdot, fill=GLOW),
            v_port.configure(text=f"{PORT}  /  {BAUD}"),
        ))
        log_event(f"Connected → {PORT} @ {BAUD}")
    except Exception as e:
        app.after(0, lambda: (
            status_txt.configure(text="OFFLINE", text_color=DANGER),
            sdot_cv.itemconfig(sdot, fill=DANGER),
        ))
        log_event(f"FAILED: {e}")

def read_loop():
    global _cur_rssi
    while True:
        try:
            if ser and ser.in_waiting:
                raw = ser.readline().decode(errors="ignore").strip()
                if not raw:
                    time.sleep(0.005)
                    continue

                st["msgs"].append(time.time())

                if raw.upper().startswith("RX READY"):
                    st["chars"] += len(raw)
                    app.after(0, lambda r=raw: (
                        raw_box.insert("end", r),
                        raw_box.see("end"),
                    ))
                    continue

                # RSSI line
                m = re.search(r"RSSI\s*[:=]\s*([-\d]+)", raw, re.I)
                if m:
                    rssi = max(-100, min(-20, int(m.group(1))))
                    st["rssi"] = rssi
                    _cur_rssi  = rssi
                    continue

                # Space marker
                if raw.strip() in ("SPACE"," ","_"):
                    continue

                st["chars"] += len(raw)
                app.after(0, lambda r=raw: (
                    raw_box.insert("end", r),
                    raw_box.see("end"),
                ))

                dec = "".join(
                    decipher(c) if c.isalnum() else c for c in raw
                ) if enc_mode.get()=="Cipher ON" else raw

                st["dec"] += len(dec.strip())

                feed_wave_from_text(raw)
                app.after(0, refresh_graph)
                app.after(0, lambda t=raw: check_stress_codes_text(t))
                app.after(0, lambda t=dec: check_stress_codes_text(t))

                for ch in dec.strip():
                    if ch.isalpha():
                        app.after(0, lambda c=ch: add_letter(c))
                    else:
                        app.after(0, lambda c=ch: (
                            plain_box.insert("end", c),
                            plain_box.see("end"),
                        ))
            else:
                time.sleep(0.01)

        except Exception as e:
            log_event(f"Serial error: {e}")
            app.after(0, lambda: (
                status_txt.configure(text="DISCONNECTED", text_color=DANGER),
                sdot_cv.itemconfig(sdot, fill=DANGER),
            ))
            time.sleep(2)
            connect_serial()

# ─────────────────────────────────────────────
# BOOT
# ─────────────────────────────────────────────
connect_serial()
if ser:
    threading.Thread(target=read_loop, daemon=True).start()

tick()
animate_sig()
app.after(500, build_segs)
log_event("CipherDit receiver started")
log_event("Stress codes: SOS=Level3(Red)  XXX=Level2(Orange)  TTT=Level1(Green)")
app.mainloop()
