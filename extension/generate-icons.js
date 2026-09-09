const fs = require("fs");
const path = require("path");

// Minimal valid 1x1 PNG byte sequence
const minimalPng = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "base64"
);

const iconDir = path.join(__dirname, "icons");
if (!fs.existsSync(iconDir)) fs.mkdirSync(iconDir, { recursive: true });

for (const size of [16, 48, 128]) {
  fs.writeFileSync(path.join(iconDir, `icon${size}.png`), minimalPng);
}

console.log("Icons generated successfully.");
