const esbuild = require("esbuild");
const fs = require("fs");
const path = require("path");

async function build() {
  const distDir = path.join(__dirname, "dist");
  if (!fs.existsSync(distDir)) {
    fs.mkdirSync(distDir, { recursive: true });
  }

  // Bundle TypeScript entry points
  await esbuild.build({
    entryPoints: {
      "content/content": path.join(__dirname, "content", "content.ts"),
      "background/service-worker": path.join(__dirname, "background", "service-worker.ts"),
      "popup/popup": path.join(__dirname, "popup", "popup.ts"),
      "options/options": path.join(__dirname, "options", "options.ts"),
    },
    bundle: true,
    outdir: distDir,
    target: "es2022",
    format: "esm",
    sourcemap: true,
  });

  // Copy manifest.json
  fs.copyFileSync(path.join(__dirname, "manifest.json"), path.join(distDir, "manifest.json"));

  // Copy HTML & CSS files
  for (const dir of ["popup", "options"]) {
    const srcDir = path.join(__dirname, dir);
    const destDir = path.join(distDir, dir);
    if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true });

    for (const file of fs.readdirSync(srcDir)) {
      if (file.endsWith(".html") || file.endsWith(".css")) {
        fs.copyFileSync(path.join(srcDir, file), path.join(destDir, file));
      }
    }
  }

  // Create icons folder with SVG/PNG icons
  const iconDir = path.join(distDir, "icons");
  if (!fs.existsSync(iconDir)) fs.mkdirSync(iconDir, { recursive: true });

  console.log("Extension build completed successfully in ./dist!");
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});
