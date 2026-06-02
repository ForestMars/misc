// pull-feed.ts (Run with: bun pull-feed.ts)

const SUBSTACK_BASE = "https://antimemetics.blog";
// Substack's public API endpoint for raw post lists
const API_URL = `${SUBSTACK_BASE}/api/v1/posts/?limit=15&offset=0`;

async function getTitles() {
  console.log("🚀 Initializing connection to Substack API...");
  console.log(`📡 Target: ${API_URL}`);

  // Create a timeout controller so it never hangs silently
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    console.log("⚠️  Network request exceeded 5 seconds. Aborting.");
    controller.abort();
  }, 5000);

  try {
    console.log("🔄 Fetching payload (mimicking standard browser headers)...");
    const response = await fetch(API_URL, {
      signal: controller.signal,
      headers: {
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        Accept: "application/json",
        Referer: SUBSTACK_BASE,
      },
    });

    clearTimeout(timeoutId);
    console.log(
      `📥 Response received. Status: ${response.status} ${response.statusText}`,
    );

    if (!response.ok) {
      throw new Error(
        `Cloudflare or Substack edge blocked the request. Status: ${response.status}`,
      );
    }

    console.log("🧠 Parsing JSON payload...");
    const posts = await response.json();

    if (!Array.isArray(posts) || posts.length === 0) {
      console.log("❌ No posts found in the returned array.");
      return;
    }

    console.log("\n--- PASTE THESE BACK IN ---");
    posts.forEach((post: any, i: number) => {
      console.log(`${i + 1}. ${post.title}`);
    });
    console.log("---------------------------\n");
  } catch (error: any) {
    clearTimeout(timeoutId);
    console.error("\n💥 Execution Failed:", error.message);

    console.log(
      "\nAlternative: Substack is aggressively fingerprinting Bun's fetch.",
    );
    console.log(
      "Run this clean curl alternative instead to bypass the TLS layer entirely:\n",
    );
    console.log(
      `curl -s "${API_URL}" | bun -e 'import("fs").readFileSync(0, "utf-8").then(d => JSON.parse(d).forEach((p, i) => console.log(\`\${i+1}. \${p.title}\`)))'`,
    );
  }
}

getTitles();
