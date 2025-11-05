const JavaScriptObfuscator = require("javascript-obfuscator");
const fs = require("fs");
const path = require("path");

function obfuscateDirectory(dir) {
  if (!fs.existsSync(dir)) {
    console.log(`Directory not found: ${dir}`);
    return;
  }

  const files = fs.readdirSync(dir);

  files.forEach((file) => {
    const filePath = path.join(dir, file);

    if (filePath.includes(":") || filePath.includes("?")) {
      console.log(`Skipped (invalid path): ${filePath}`);
      return;
    }

    // Skip source map files
    if (file.endsWith(".js.map") || file.endsWith(".map")) {
      console.log(`Skipped (source map): ${filePath}`);
      return;
    }

    let stat;
    try {
      stat = fs.statSync(filePath);
    } catch (error) {
      console.log(`Skipped (cannot access): ${filePath}`);
      return;
    }

    if (stat.isDirectory()) {
      obfuscateDirectory(filePath);
    } else if (file.endsWith(".js") && stat.isFile()) {
      try {
        const code = fs.readFileSync(filePath, "utf8");

        // Skip if file is too small or empty
        if (code.length < 10) {
          console.log(`Skipped (too small): ${filePath}`);
          return;
        }

        const obfuscated = JavaScriptObfuscator.obfuscate(code, {
          compact: true,
          controlFlowFlattening: true,
          controlFlowFlatteningThreshold: 0.75,
          deadCodeInjection: true,
          deadCodeInjectionThreshold: 0.4,
          debugProtection: false,
          debugProtectionInterval: 0,
          disableConsoleOutput: true,
          identifierNamesGenerator: "hexadecimal",
          log: false,
          numbersToExpressions: true,
          renameGlobals: false,
          rotateStringArray: true,
          selfDefending: true,
          shuffleStringArray: true,
          simplify: true,
          splitStrings: true,
          splitStringsChunkLength: 10,
          stringArray: true,
          stringArrayEncoding: ["rc4"],
          stringArrayIndexShift: true,
          stringArrayRotate: true,
          stringArrayShuffle: true,
          stringArrayWrappersCount: 2,
          stringArrayWrappersChainedCalls: true,
          stringArrayWrappersParametersMaxCount: 4,
          stringArrayWrappersType: "function",
          stringArrayThreshold: 0.75,
          transformObjectKeys: true,
          unicodeEscapeSequence: false,
        });

        fs.writeFileSync(filePath, obfuscated.getObfuscatedCode());
        console.log(`✓ Obfuscated: ${filePath}`);
      } catch (error) {
        console.error(`✗ Failed to obfuscate ${filePath}:`, error.message);
      }
    }
  });
}

console.log("Starting obfuscation process...");
console.log("");

// Obfuscate the .next/static directory (client-side JavaScript)
const staticDir = path.join(__dirname, "../.next/static");
if (fs.existsSync(staticDir)) {
  console.log("Obfuscating .next/static directory...");
  obfuscateDirectory(staticDir);
} else {
  console.log(
    'Static directory not found. Make sure to run "next build" first.'
  );
}

console.log("");
console.log("Obfuscation complete!");
