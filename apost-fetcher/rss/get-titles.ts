// pull-feed.ts (Run with: bun pull-feed.ts or node pull-feed.js)

const FEED_URL = "https://antimemetics.blog/feed.xml"; // Adjust filename if it's rss.xml or atom.xml

async function getTitles() {
  try {
    const response = await fetch(FEED_URL, {
      headers: { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" }
    });
    
    if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
    
    const text = await response.text();
    
    // Clean regex match for <title> tags inside <item> or <entry> blocks
    const itemRegex = /<(item|entry)>([\s\S]*?)<\/\1>/g;
    const titleRegex = /<title>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/title>/;
    
    const titles = [];
    let match;
    
    while ((match = itemRegex.exec(text)) !== null) {
      const itemContent = match[2];
      const titleMatch = itemContent.match(titleRegex);
      if (titleMatch && titleMatch[1]) {
        titles.push(titleMatch[1].trim());
      }
    }

    if (titles.length === 0) {
      // Fallback: if no items/entries found, just grab any title tags present
      const genericTitleRegex = /<title>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/title>/g;
      let genMatch;
      while ((genMatch = genericTitleRegex.exec(text)) !== null) {
        titles.push(genMatch[1].trim());
      }
      // Remove the first one if it's just the main blog title
      if (titles.length > 1) titles.shift();
    }

    console.log("\n--- PASTE THESE BACK IN ---");
    titles.forEach((title, i) => console.log(`${i + 1}. ${title}`));
    console.log("---------------------------\n");

  } catch (error) {
    console.error("Failed to pull feed directly:", error.message);
    console.log("\nAlternative curl command if the platform is blocking headers:");
    console.log(`curl -s ${FEED_URL} | grep -oE '<title>[^<]+' | sed 's/<title>//'`);
  }
}

getTitles();
