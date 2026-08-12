# 2026-07-08 AI Video Generation Experience: Reference Character → Storyboard Images → Grok Image-to-Video

> This document records a real AI video generation iteration: extracting a character from an original mushroom character video, adapting it into a 23-second vertical video of "little mushroom gets sleepy and makes coffee," and summarizing experiences with direct text-to-video, image-to-video, keyframes, Grok, GPT image models, and ffmpeg concatenation.

## Background

The goal was to use the cute mushroom character from the original reference video to generate a new coffee-themed short film:

1. Little mushroom gets sleepy reading a book;
2. Walks to the coffee machine;
3. Puts coffee beans in;
4. Grinds them into powder;
5. Pours hot water and stirs;
6. Happily enjoys the coffee.

The final delivered video includes original cozy background music. During the process, it was discovered that: **giving a long script directly to video models tends to produce visually cute but logically incorrect segments**. A more stable method is to first use image models to generate key storyboard frames, then animate each image with video models.

## Final Reusable Conclusion

Most stable workflow:

```text
原始视频抽帧
→ 选干净角色参考帧
→ 清理角色参考图
→ 写分镜脚本和约束
→ GPT 图片模型生成每个场景关键帧
→ 逐张检查/重生成问题关键帧
→ 压缩关键帧，避免请求过大
→ Grok image-to-video 每张图生成一个短片段
→ 抽帧检查每段，裁剪安全区间
→ ffmpeg 拼接
→ 最终 1fps 抽帧复检
→ 加背景音乐
```

Don't directly give a long storyboard script to video models to generate the complete video in one go, unless the video only needs atmosphere, not action logic.

## Key Pitfalls

### 1. Video Models Make Character "Spit Coffee into Cup"

Problem: Mushroom character approaches cup opening, steam or liquid path passes between mouth and cup rim, looks like character is spitting liquid into cup.

Cause: Prompt only wrote "smell coffee," "steam," "drink coffee," model connected steam/liquid with character mouth.

Fix: Avoid at keyframe stage, not just rely on video prompts:

```text
Mushroom is behind and to the right of the mug, at least one mug-width away from the cup rim.
The mushroom mouth is not aligned with the mug opening.
Steam rises vertically from the mug only, far from the mushroom face.
No steam crosses the mouth or eyes.
```

If problem segment already generated, frame-locate the problematic time period, cut out unsafe intervals, or regenerate keyframes with "mouth away from cup opening."

### 2. Coffee Beans Scattered on Table by Model

Problem: After prompting "put coffee beans," model randomly scatters beans on table like they were thrown.

Fix: Clearly state source, target, and prohibited areas:

```text
Coffee beans are only in the wooden scoop and the large centered hopper.
A few beans are directly over the hopper opening.
No beans on the table, no flying beans, no scattered beans.
```

If beans are already scattered in keyframe, must regenerate keyframe, don't expect Grok animation phase to self-correct.

### 3. Old Reference Video Scene Contaminates New Video

Original reference video showed mushroom cooking/stir-frying. Directly giving keyframes to video model easily brings in old elements like wok, bowl, dishes, wooden spoon into coffee video.

Fix:

- Reference image only keeps character identity, clean up old scene;
- Prompt explicitly: `Use the reference only for character identity, not scene or props`;
- Explicitly prohibit: wok, pan, food bowl, vegetables, meat, cooking spoon.

### 4. Grok Unstable Following of Long Scripts

Even with scene breakdowns, characters, negative constraints, and prop positions in long scripts, Grok may only grasp the general idea of "mushroom + coffee," ignoring action causality.

More stable approach:

- One keyframe expresses only one action;
- One Grok clip only gets one short prompt;
- Finally concatenate with ffmpeg.

### 5. Data URL Images Too Large Trigger 413

Directly passing GPT-generated PNG base64 to Grok/sub2api may trigger:

```text
413 Request Entity Too Large
```

Fix: Convert to compressed JPEG, e.g., 648×1152, quality 82, usually 60–100KB is sufficient:

```python
from PIL import Image
im = Image.open(src).convert('RGB')
im.thumbnail((648, 1152), Image.LANCZOS)
im.save(out, 'JPEG', quality=82, optimize=True)
```

### 6. Don't Trust 8-Second Clips Entirely

Grok returns 8 seconds per segment, but first half may be good while second half drifts. Must extract frames to check each segment and select safe intervals.

Common crop interval examples:

```text
S1 阅读犯困：1–5s
S2 咖啡机前：2–5.5s
S3 放豆：1–4.5s
S4 磨粉：2–5.5s
S5 倒水搅拌：1–5s
S6 享用咖啡：2–7s
```

## Recommended Prompt Modules

### Character Identity Module

```text
Same cute handmade needle-felt amanita mushroom mascot: fuzzy red cap with soft white spots, cream felt face/body, black bead eyes, tiny smile, rosy cheeks, small rounded arms, tactile wool fibers. One mushroom only, consistent proportions. Vertical 9:16 keyframe, dreamy macro miniature stop-motion toy aesthetic, warm cream palette, shallow depth of field. No human hands, no text, no logo, no old cooking/stir-fry props.
```

### Anti-Spit Module

```text
Mushroom stands behind-right of the cup, mouth far away from cup opening. Steam rises from the cup only, not from the mushroom mouth. No liquid stream from the mushroom. No spit-like shapes. Steam does not cross the mushroom face.
```

### Anti-Bean-Scatter Module

```text
Coffee beans go directly from the wooden scoop into the coffee machine hopper. Beans stay in the scoop, hopper, or bowl only. No beans on the table. No flying beans. No scattered mess.
```

### Anti-Old-Scene-Contamination Module

```text
Use the reference only for character identity, not scene or props. Clean coffee scene only. No wok, no pan, no food bowl, no vegetables, no meat, no soup, no cooking spoon, no old stir-fry scene.
```

## Storyboard Design Experience

Don't make one scene bear too many actions. Most stable is 6 short scenes:

1. **Sleepy**: Only book, desk lamp, little mushroom, no coffee props appear.
2. **At coffee machine**: Coffee machine, cup, bean bowl, little mushroom still sleepy but expectant.
3. **Putting beans**: Wooden scoop aligned with hopper, beans only go into hopper.
4. **Grinding**: Coffee grounds appear in a transparent grounds cup.
5. **Pouring and stirring**: Water comes from kettle spout, spoon creates vortex in cup.
6. **Enjoying**: Mushroom smiles behind and to the side of cup, don't align mouth with cup opening.

If an action is unclear in keyframe, should regenerate image first rather than carrying the problem into video generation.

## ffmpeg Concatenation Experience

First unify dimensions and encoding for each segment, then concat:

```bash
ffmpeg -y -ss 1 -to 5 -i scene1.mp4 \
  -vf "scale=400:736:force_original_aspect_ratio=decrease,pad=400:736:(ow-iw)/2:(oh-ih)/2,format=yuv420p" \
  -af "aresample=async=1" \
  -c:v libx264 -preset veryfast -crf 20 -c:a aac p1.mp4

cat > list.txt <<'EOF'
file '/tmp/parts/p1.mp4'
file '/tmp/parts/p2.mp4'
file '/tmp/parts/p3.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i list.txt -c copy -movflags +faststart final.mp4
```

Finally must generate 1fps contact sheet for re-verification:

```bash
ffmpeg -y -i final.mp4 -vf "fps=1,scale=240:-1" /tmp/final_review/frame_%02d.jpg
```

## Background Music Experience

When no music API is available, can locally synthesize simple original BGM:

- 100–120 BPM;
- C / Am / F / G chords;
- music-box/bell melody;
- soft pad + light shaker;
- fade in/out;
- Don't mix too loud.

Example mix command:

```bash
ffmpeg -y -i final.mp4 -i bgm.wav \
  -filter_complex "[1:a]volume=0.45,afade=t=in:st=0:d=0.8,afade=t=out:st=22.7:d=0.8[a]" \
  -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart final_bgm.mp4
```

Use `volumedetect` to check, average volume around `-24 dB`, peak around `-9 dB` is comfortable for listening in WeChat.

## Turn the workflow into a Hermes skill

This workflow has been saved as a local Hermes skill:

```text
~/.hermes/skills/media/storyboarded-ai-video-generation/SKILL.md
```

Next time generating similar videos, should prioritize loading that skill and following the "character reference → storyboard images → short video clips → crop and concatenate → frame verification" workflow.

## Verification Checklist

- [ ] Use original reference material to extract character, not derived images from generation.
- [ ] Reference image has old scene props cleaned.
- [ ] Each storyboard has only one action.
- [ ] Each keyframe passes visual inspection.
- [ ] Keyframes compressed before passing to video model.
- [ ] Each video clip frame-extracted and cropped to safe intervals.
- [ ] Final concatenation 1fps frame verification.
- [ ] No spitting, no bean scattering, no liquid overflow, no old scene contamination.
- [ ] Final video with BGM verified with `ffprobe` and `volumedetect`.
