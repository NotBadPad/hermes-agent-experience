# 2026-07-08 AI 视频生成经验：参考角色 → 分镜图片 → Grok 图生视频

> 本文记录一次真实的 AI 视频生成迭代：从原始蘑菇角色视频中提取形象，改编成“小蘑菇犯困后做咖啡”的 23 秒竖屏视频，并总结直接文生视频、图生视频、关键帧、Grok、GPT 图片模型和 ffmpeg 拼接中的经验。

## 背景

目标是用原始参考视频里的可爱蘑菇角色，生成一个新的咖啡主题短片：

1. 小蘑菇看书犯困；
2. 走到咖啡机前；
3. 放入咖啡豆；
4. 磨成粉末；
5. 倒入开水并搅拌；
6. 美滋滋地享用咖啡。

最终交付视频包含原创温馨背景乐。过程中发现：**长脚本直接交给视频模型，容易出现视觉可爱但逻辑错误的片段**。更稳的方法是先用图片模型生成关键分镜，再把每张图交给视频模型动起来。

## 最终可复用结论

最稳流程：

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

不要直接把一个长分镜脚本交给视频模型一次性生成完整视频，除非视频只需要氛围、不要求动作逻辑。

## 关键踩坑

### 1. 视频模型会让角色“往杯子里吐咖啡”

问题表现：蘑菇角色靠近杯口，蒸汽或液体路径经过嘴部和杯口之间，看起来像角色在往杯子里吐液体。

原因：提示词里只写了“闻咖啡”“热气”“喝咖啡”，模型把蒸汽/液体和角色嘴部连接起来。

修法：在关键帧阶段就规避，而不是只靠视频提示词：

```text
Mushroom is behind and to the right of the mug, at least one mug-width away from the cup rim.
The mushroom mouth is not aligned with the mug opening.
Steam rises vertically from the mug only, far from the mushroom face.
No steam crosses the mouth or eyes.
```

如果已经生成了问题片段，应逐帧定位问题时间段，裁掉 unsafe 区间，或重新生成“嘴部远离杯口”的关键帧。

### 2. 咖啡豆会被模型撒到桌子上

问题表现：提示“放咖啡豆”后，模型会把豆子随机撒在桌面上，像被扔出去。

修法：明确来源、目标和禁止区域：

```text
Coffee beans are only in the wooden scoop and the large centered hopper.
A few beans are directly over the hopper opening.
No beans on the table, no flying beans, no scattered beans.
```

如果关键帧里豆子已经乱撒，必须重生成关键帧，不要指望 Grok 动画阶段自行修正。

### 3. 旧参考视频的场景会污染新视频

原始参考视频里是蘑菇做饭/炒菜。直接把关键帧交给视频模型，容易把锅、碗、菜、木勺等旧元素带入咖啡视频。

修法：

- 参考图只保留角色身份，清理旧场景；
- 提示词明确：`Use the reference only for character identity, not scene or props`；
- 明确禁止：wok、pan、food bowl、vegetables、meat、cooking spoon。

### 4. Grok 对长脚本遵循不稳定

长脚本里写了分镜、角色、负面约束、道具位置，Grok 仍可能只抓住“蘑菇 + 咖啡”的大意，忽略动作因果。

更稳的做法是：

- 一张关键帧只表达一个动作；
- 一个 Grok 片段只给一个短提示；
- 最后用 ffmpeg 拼接。

### 5. data URL 图片太大会触发 413

直接把 GPT 生成的 PNG base64 传给 Grok/sub2api，可能触发：

```text
413 Request Entity Too Large
```

修法：转成压缩 JPEG，例如 648×1152、quality 82，通常 60–100KB 足够：

```python
from PIL import Image
im = Image.open(src).convert('RGB')
im.thumbnail((648, 1152), Image.LANCZOS)
im.save(out, 'JPEG', quality=82, optimize=True)
```

### 6. 不能整段信任 8 秒视频

Grok 每段返回 8 秒，但前半段可能很好，后半段可能漂移。必须抽帧检查每段，选安全区间。

常见裁剪区间示例：

```text
S1 阅读犯困：1–5s
S2 咖啡机前：2–5.5s
S3 放豆：1–4.5s
S4 磨粉：2–5.5s
S5 倒水搅拌：1–5s
S6 享用咖啡：2–7s
```

## 推荐提示词模块

### 角色身份模块

```text
Same cute handmade needle-felt amanita mushroom mascot: fuzzy red cap with soft white spots, cream felt face/body, black bead eyes, tiny smile, rosy cheeks, small rounded arms, tactile wool fibers. One mushroom only, consistent proportions. Vertical 9:16 keyframe, dreamy macro miniature stop-motion toy aesthetic, warm cream palette, shallow depth of field. No human hands, no text, no logo, no old cooking/stir-fry props.
```

### 防吐液模块

```text
Mushroom stands behind-right of the cup, mouth far away from cup opening. Steam rises from the cup only, not from the mushroom mouth. No liquid stream from the mushroom. No spit-like shapes. Steam does not cross the mushroom face.
```

### 防豆子乱撒模块

```text
Coffee beans go directly from the wooden scoop into the coffee machine hopper. Beans stay in the scoop, hopper, or bowl only. No beans on the table. No flying beans. No scattered mess.
```

### 防旧场景污染模块

```text
Use the reference only for character identity, not scene or props. Clean coffee scene only. No wok, no pan, no food bowl, no vegetables, no meat, no soup, no cooking spoon, no old stir-fry scene.
```

## 分镜设计经验

不要让一个场景承担太多动作。最稳的是 6 个短场景：

1. **犯困**：只有书、台灯、小蘑菇，不出现咖啡道具。
2. **到咖啡机前**：咖啡机、杯子、豆碗，小蘑菇还困但期待。
3. **放豆**：木勺对准豆仓，豆子只进豆仓。
4. **磨粉**：透明粉槽/粉杯中出现咖啡粉。
5. **倒水搅拌**：水来自壶嘴，勺子在杯里产生旋涡。
6. **享用**：蘑菇在杯子侧后方微笑，不让嘴对准杯口。

如果关键帧里某个动作不明确，应先重生成图，而不是带病进入视频生成。

## ffmpeg 拼接经验

每段先统一尺寸和编码，再 concat：

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

最终必须生成 1fps contact sheet 做复检：

```bash
ffmpeg -y -i final.mp4 -vf "fps=1,scale=240:-1" /tmp/final_review/frame_%02d.jpg
```

## 背景音乐经验

没有音乐 API 时，可以本地合成简单原创 BGM：

- 100–120 BPM；
- C / Am / F / G 和弦；
- music-box/bell melody；
- soft pad + light shaker；
- 淡入淡出；
- 混音不要太大。

示例混音命令：

```bash
ffmpeg -y -i final.mp4 -i bgm.wav \
  -filter_complex "[1:a]volume=0.45,afade=t=in:st=0:d=0.8,afade=t=out:st=22.7:d=0.8[a]" \
  -map 0:v:0 -map "[a]" -c:v copy -c:a aac -b:a 128k -shortest -movflags +faststart final_bgm.mp4
```

用 `volumedetect` 检查，平均音量约 `-24 dB`、峰值约 `-9 dB` 在微信里听感较舒服。

## 已沉淀为 Hermes Skill

本次流程已沉淀为本地 Hermes skill：

```text
~/.hermes/skills/media/storyboarded-ai-video-generation/SKILL.md
```

下次生成类似视频时，应优先加载该 skill，并按“角色参考 → 分镜图 → 短视频片段 → 裁剪拼接 → 抽帧验证”的流程执行。

## 验证清单

- [ ] 使用原始参考素材提取角色，而不是生成后的派生图。
- [ ] 参考图已清理旧场景道具。
- [ ] 每个分镜只有一个动作。
- [ ] 每张关键帧都通过视觉检查。
- [ ] 关键帧压缩后再传给视频模型。
- [ ] 每段视频都抽帧检查并裁剪安全区间。
- [ ] 最终拼接后 1fps 抽帧验证。
- [ ] 无吐液、无豆子乱撒、无液体外溢、无旧场景污染。
- [ ] 最终视频加 BGM 后用 `ffprobe` 和 `volumedetect` 验证。
