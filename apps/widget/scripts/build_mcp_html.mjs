import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const packageDir = dirname(dirname(fileURLToPath(import.meta.url)));
const distDir = join(packageDir, "dist");
const indexPath = join(distDir, "index.html");
const outputPath = join(distDir, "widget.html");

let html = readFileSync(indexPath, "utf8");

html = html.replace(
  /<script([^>]*)src="([^"]+\.js)"([^>]*)><\/script>/g,
  (_match, before, src, after) => {
    const assetPath = join(distDir, src.replace(/^\.\//, ""));
    const code = readFileSync(assetPath, "utf8").replaceAll("</script", "<\\/script");
    return `<script${before}${after}>${code}</script>`;
  },
);

html = html.replace(
  /<link([^>]*?)rel="stylesheet"([^>]*?)href="([^"]+\.css)"([^>]*?)>/g,
  (_match, before, middle, href, after) => {
    const assetPath = join(distDir, href.replace(/^\.\//, ""));
    const css = readFileSync(assetPath, "utf8").replaceAll("</style", "<\\/style");
    return `<style${before}${middle}${after}>${css}</style>`;
  },
);

writeFileSync(outputPath, html);
