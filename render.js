// Export vidéo de la pub : node render.js
// Nécessite : Node.js, Playwright (npm i playwright), Google Chrome ou Chromium, ffmpeg.
// Produit : scenes/scene1.mp4 … scene5.mp4, puis pub-artisan-relance-15s.mp4 (avec le son).
const { chromium } = require("playwright");
const { spawn, execFileSync } = require("child_process");
const fs = require("fs"), path = require("path");

const FPS = 30, SCENES = [[0, 3], [3, 6], [6, 9], [9, 12], [12, 15]];
const only = process.argv[2] ? Number(process.argv[2]) : null; // node render.js 3 => ne refait que la scène 3
const dir = __dirname, out = path.join(dir, "scenes");
fs.mkdirSync(out, { recursive: true });

function encoder(file) {
  return spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", String(FPS), "-movflags", "+faststart", file],
    { stdio: ["pipe", "inherit", "inherit"] });
}

(async () => {
  const exe = ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"].find(fs.existsSync);
  const browser = await chromium.launch({ executablePath: exe, args: ["--allow-file-access-from-files"] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on("pageerror", e => console.error("Erreur dans la page :", e.message));
  await page.goto("file://" + path.join(dir, "pub-artisan-relance.html") + "?render=1");
  await page.evaluate(() => window.fontsReady);
  await page.waitForTimeout(300);

  for (let s = 0; s < SCENES.length; s++) {
    if (only && only !== s + 1) continue;
    const [a, b] = SCENES[s], tmp = path.join(out, `scene${s + 1}.tmp.mp4`), fin = path.join(out, `scene${s + 1}.mp4`);
    const ff = encoder(tmp);
    const done = new Promise((ok, ko) => ff.on("close", c => c === 0 ? ok() : ko(new Error("ffmpeg " + c))));
    for (let f = Math.round(a * FPS); f < Math.round(b * FPS); f++) {
      const b64 = await page.evaluate(t => { renderFrame(t); return document.getElementById("c").toDataURL("image/jpeg", 0.92).split(",")[1]; }, f / FPS);
      if (!ff.stdin.write(Buffer.from(b64, "base64"))) await new Promise(r => ff.stdin.once("drain", r));
    }
    ff.stdin.end(); await done;
    fs.renameSync(tmp, fin);
    console.log(`Scène ${s + 1} rendue`);
  }
  await browser.close();

  // Assemblage sans ré-encodage, puis ajout du son (normalisé à -14 LUFS)
  const list = path.join(out, "liste.txt");
  fs.writeFileSync(list, SCENES.map((_, i) => `file 'scene${i + 1}.mp4'`).join("\n"));
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", list, "-c", "copy", path.join(out, "image.mp4")]);
  execFileSync("ffmpeg", ["-y", "-loglevel", "error", "-i", path.join(out, "image.mp4"), "-i", path.join(dir, "bande-son.wav"),
    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
    "-shortest", "-movflags", "+faststart", path.join(dir, "pub-artisan-relance-15s.mp4")]);
  console.log("Terminé : pub-artisan-relance-15s.mp4");
})().catch(e => { console.error(e); process.exit(1); });
