(async () => {
  const video = document.querySelector("video");

  if (!video) {
    console.log("No video element found.");
    return;
  }

  console.log("Found video element.");

  // Capture the stream directly from the video element
  const stream = video.captureStream();

  const recorder = new MediaRecorder(stream, {
    mimeType: "video/webm;codecs=vp9,opus"
  });

  const chunks = [];

  recorder.ondataavailable = e => {
    if (e.data.size > 0) {
      chunks.push(e.data);
    }
  };

  recorder.onstop = () => {
    const blob = new Blob(chunks, {
      type: "video/webm"
    });

    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = `instagram-story-${Date.now()}.webm`;
    a.click();

    URL.revokeObjectURL(url);

    console.log("Saved recording.");
  };

  recorder.start();

  console.log("Recording started.");

  // Ensure playback
  await video.play();

  // Stop automatically when story ends
  video.onended = () => {
    recorder.stop();
    console.log("Story ended.");
  };

  // Manual stop fallback
  window.stopIGCapture = () => {
    recorder.stop();
    console.log("Stopped manually.");
  };
})();