# Edit Guide

## Sequence

1. Concatenate speed-matched `S00...SNN` in numeric order.
2. Replace every source audio track with matching `audio0...audioN`.
3. Mix `bgm.mp3` below narration.
4. Burn validated `subtitles/subtitles.srt` into the final video.

## Rules

- S00 is the repeated cover frame segment.
- The last shot is the user-provided outro.
- Do not add post-production text, titles, arrows, boxes, logos, or UI labels.
- Preserve clear narration above BGM.

## Export

- Resolution:
- FPS: 30
- Video codec: H.264
- Audio codec: AAC
- Final path: materials/output/final_video_subtitled.mp4
