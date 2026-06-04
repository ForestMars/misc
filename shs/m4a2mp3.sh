for file in *.m4a; do
    ffmpeg -i "$file" -acodec libmp3lame -ab 128k "${file%.m4a}.mp3"
done
