# Nano Banana Prompting Guide

Extracted from [Google Cloud 官方指南](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana).

## Prompt 公式

### 文字生图 (Text-to-Image)

```
[主体] + [动作] + [场景/背景] + [构图] + [风格]
```

**示例**：
> A striking fashion model wearing a tailored brown dress, sleek boots, and holding a structured handbag. Posing with a confident stance, slightly turned. A seamless deep cherry red studio backdrop. Medium-full shot, center-framed. Fashion magazine editorial, shot on medium-format analog film, pronounced grain, high saturation, cinematic lighting.

### 多参考图生成 (Multimodal)

```
[参考图说明] + [关系指令] + [新场景]
```

**示例**：
> Using the attached napkin sketch as the structure and the attached fabric sample as the texture, transform this into a high-fidelity 3D armchair render. Place it in a sun-drenched, minimalist living room.

### 图片编辑 (Editing)

语义遮罩（inpainting）：用文字指定要修改的区域。明确说明哪些部分保持不变。

**示例**：
> Remove the man from the photo.  
> Change the background to a tropical beach, keep the person exactly the same.

### 实时信息生成

模型支持 Web 搜索获取实时数据来生成图片。

```
[搜索/数据请求] + [分析任务] + [视觉化方式]
```

### 文字渲染

- 用引号包裹目标文字：`"Happy Birthday"`
- 指定字体风格：`bold, white, sans-serif font` 或 `Century Gothic 12px font`
- 支持 10+ 语言翻译

## 高级技巧

### 灯光
- 三点柔光箱布局
- 明暗对比 (Chiaroscuro)
- 黄金时段逆光

### 镜头与焦距
- 相机型号：GoPro（沉浸感）、Fujifilm（色彩）、一次性相机（复古）
- 镜头：低角度浅景深 f/1.8、广角、微距
- 景深控制

### 色彩与质感
- 胶片模拟：`1980s color film, slightly grainy`
- 电影调色：`Cinematic color grading with muted teal tones`
- 材质细节：`navy blue tweed`、`ornate elven plate armor etched with silver leaf patterns`

## 模型规格

| 特性 | Nano Banana 2 | Nano Banana Pro |
|------|--------------|-----------------|
| 模型 ID | gemini-3.1-flash-image | gemini-3-pro-image |
| 输入 tokens | 131,072 | 65,536 |
| 输出 tokens | 32,768 | 32,768 |
| 分辨率 | 0.5K-4K | 1K-4K |
| 宽高比 | 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9, 1:4, 4:1, 1:8, 8:1 | 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9 |
| 参考图上限 | 14 张 | 14 张 |
| 角色一致性 | 5 人 | 5 人 |
| 实时搜索 | 支持 | 支持 |

## 常见问题

- **没有返回图片？** 让 prompt 更明确地描述要生成的画面，避免纯问答式提问
- **文字渲染不准？** 用引号包裹文字，指定字体和大小
- **角色不一致？** 在同一会话中多轮对话，保持上下文连续性
