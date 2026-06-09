// pull-feed.ts (Run directly with: bun pull-feed.ts)

const TARGET_URL = "https://forestmars.substack.com/api/v1/posts/?limit=15";

async function getTitles() {
  console.log("🚀 Initializing edge connection via system child process...");
  console.log(`📡 Targeting API endpoint: ${TARGET_URL}`);

  try {
    // Spawn curl as a synchronous child process to let the system handle the TLS handshake
    const proc = Bun.spawnSync({
      cmd: [
        "curl",
        "-s",
        "-H",
        "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-H",
        "Accept: application/json",
        TARGET_URL,
      ],
    });

    if (proc.exitCode !== 0) {
      throw new Error(
        `System curl command failed with exit code: ${proc.exitCode}`,
      );
    }

    const rawResponse = proc.stdout.toString();

    if (!rawResponse || rawResponse.trim() === "") {
      throw new Error(
        "Received an empty response stream from the edge endpoint.",
      );
    }

    console.log("🧠 Decoding JSON array from stream payload...");
    const posts = JSON.parse(rawResponse);

    if (!Array.isArray(posts)) {
      console.log(
        "⚠️  Data boundary error: Content did not return a standard list array.",
      );
      console.log(rawResponse.substring(0, 300));
      return;
    }

    console.log("\n--- PASTE THESE BACK IN ---");
    posts.forEach((post: any, i: number) => {
      console.log(`${i + 1}. ${post.title}`);
    });
    console.log("---------------------------\n");
  } catch (error: any) {
    console.error("\n💥 Execution Failure:", error.message);
  }
}

getTitles();
