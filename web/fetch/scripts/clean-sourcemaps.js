const fs = require("fs");
const path = require("path");

function cleanSourceMaps(dir) {
  if (!fs.existsSync(dir)) {
    console.log(`Directory not found: ${dir}`);
    return;
  }

  const files = fs.readdirSync(dir);

  files.forEach((file) => {
    const filePath = path.join(dir, file);

    let stat;
    try {
      stat = fs.statSync(filePath);
    } catch (error) {
      console.log(`Skipped (cannot access): ${filePath}`);
      return;
    }

    if (stat.isDirectory()) {
      cleanSourceMaps(filePath);
    } else if (file.endsWith(".js.map")) {
      try {
        const sourceMap = JSON.parse(fs.readFileSync(filePath, "utf8"));

        // Clean the sources array to remove webpack pseudo-paths
        if (sourceMap.sources && Array.isArray(sourceMap.sources)) {
          sourceMap.sources = sourceMap.sources.map((source) => {
            let cleaned = source
              .replace(/^webpack:\/_N_E\//, "") // Remove webpack:/_N_E/ prefix
              .replace(/^_N_E\//, "") // Remove _N_E/ prefix
              .replace(/\?[a-z0-9]+$/, "") // Remove query params like ?adc8
              .replace(/^webpack:\/\//, "") // Remove other webpack prefixes
              .replace(/^webpack:/, ""); // Remove webpack: prefix

            // Remove absolute paths (e.g., /home/user/... -> node_modules/...)
            cleaned = cleaned.replace(/^.*\/(node_modules\/.*)$/, "$1");

            // Remove node_modules entirely (hide framework internals)
            if (cleaned.includes("node_modules")) return "";

            return cleaned;
          });

          fs.writeFileSync(filePath, JSON.stringify(sourceMap));
          console.log(`✓ Cleaned: ${filePath}`);
        }
      } catch (error) {
        console.error(`✗ Failed to clean ${filePath}:`, error.message);
      }
    }
  });
}

console.log("Starting source map cleanup process...");
console.log("");

// Clean source maps in the .next/static directory
const staticDir = path.join(__dirname, "../.next/static");
if (fs.existsSync(staticDir)) {
  console.log("Cleaning source maps in .next/static directory...");
  cleanSourceMaps(staticDir);
} else {
  console.log(
    'Static directory not found. Make sure to run "next build" first.'
  );
}

console.log("");
console.log("Source map cleanup complete!");
