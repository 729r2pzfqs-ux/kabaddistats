// Tailwind config used to pre-compile a static stylesheet for kabaddistats.com.
// Mirrors the theme that previously lived inline (cdn.tailwindcss.com runtime).
// The compiled output is written to ../styles.css by scripts/generate.py
// (build_css), scanning the generated HTML so only used utilities are emitted.
const path = require("path");
const ROOT = path.resolve(__dirname, "..");
module.exports = {
  content: [path.join(ROOT, "**/*.html")],
  theme: {
    extend: {
      colors: {
        'kb-orange':'#FF6B00','kb-dark':'#9A3412','kb-accent':'#FB923C',
        'kb-bg':'#fdf7f2','kb-card':'#ffffff','kb-border':'#f0e3d8',
        'kb-text':'#6b5d52','kb-ink':'#2a1c12','kb-mat':'#1d4ed8','kb-gold':'#d97706'
      },
      fontFamily: {
        heading:['"Baloo 2"','"Noto Sans Devanagari"','sans-serif'],
        body:['Inter','"Noto Sans Devanagari"','sans-serif']
      }
    }
  }
}
