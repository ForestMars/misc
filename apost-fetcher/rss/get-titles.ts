// pull-feed.ts (Run directly with: bun pull-feed.ts)
import tls from "node:tls";

const HOST = "antimemetics.blog";
const TARGET_PATH = "/api/v1/posts/?limit=15";

// A hardened modern browser cipher list to help break through the WAF fingerprinting layer
const CHROME_CIPHERS = [
  "TLS_AES_128_GCM_SHA256",
  "TLS_AES_256_GCM_SHA384",
  "TLS_CHACHA20_POLY1305_SHA256",
  "ECDHE-ECDSA-AES128-GCM-SHA256",
  "ECDHE-RSA-AES128-GCM-SHA256",
  "ECDHE-ECDSA-AES256-GCM-SHA384",
  "ECDHE-RSA-AES256-GCM-SHA384",
  "ECDHE-ECDSA-CHACHA20-POLY1305",
  "ECDHE-RSA-CHACHA20-POLY1305",
].join(":");

function fetchWithRawSocket(): Promise<string> {
  return new Promise((resolve, reject) => {
    console.log("📡 Opening raw TLS stream directly to edge servers...");

    const socket = tls.connect(
      {
        host: HOST,
        port: 443,
        servername: HOST,
        ciphers: CHROME_CIPHERS,
        minVersion: "TLSv1.2",
        maxVersion: "TLSv1.3",
        honorCipherOrder: true,
      },
      () => {
        console.log(
          "🔓 Handshake achieved. Injecting HTTP/1.1 frame manually...",
        );

        // Construct a clean, minimal browser wire frame
        const httpRequest = [
          `GET ${TARGET_PATH} HTTP/1.1`,
          `Host: ${HOST}`,
          "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
          "Accept: application/json",
          "Accept-Language: en-US,en;q=0.9",
          "Connection: close",
          "\r\n",
        ].join("\r\n");

        socket.write(httpRequest);
      },
    );

    let rawData = "";
    socket.setEncoding("utf8");

    socket.on("data", (chunk) => {
      rawData += chunk;
    });

    socket.on("end", () => {
      resolve(rawData);
    });

    socket.on("error", (err) => {
      reject(err);
    });

    // Safety guard to kill dead hangs
    socket.setTimeout(6000, () => {
      socket.destroy();
      reject(new Error("Socket connection dropped via 6s timeout layer."));
    });
  });
}

async function run() {
  try {
    const rawResponse = await fetchWithRawSocket();

    // Separate the raw HTTP headers from the JSON payload body
    const headerDelimiter = "\r\n\r\n";
    const delimiterIndex = rawResponse.indexOf(headerDelimiter);

    if (delimiterIndex === -1) {
      throw new Error("Invalid protocol boundary in socket stream.");
    }

    const body = rawResponse.substring(delimiterIndex + headerDelimiter.length);

    console.log("🧠 Decoding data payload...");
    const posts = JSON.parse(body);

    if (!Array.isArray(posts)) {
      console.log(
        "⚠️ Content layout did not return a standard post list array.",
      );
      console.log(body.substring(0, 300));
      return;
    }

    console.log("\n--- PASTE THESE BACK IN ---");
    posts.forEach((post: any, i: number) => {
      console.log(`${i + 1}. ${post.title}`);
    });
    console.log("---------------------------\n");
  } catch (error: any) {
    console.error("\n💥 Socket Level Failure:", error.message);
    console.log(
      "If this timed out, the edge has flagged your residential block's IP subnet entirely.",
    );
  }
}

run();
