# LEXY 营销短视频 AI 工业化生产 Pipeline

莱克电气 品牌部 —— 面向抖音 / 视频号 / TikTok（@homeupgradehub00）营销短视频的 AI 辅助生产流水线。
目标：把单条短视频产出周期从 **7 天压缩到 2 天**，月产能从 4 条提升到 12 条，产品失真返工率控制在 5% 以内。

## AI 工具与模型栈

| 环节 | 工具 / 模型 | 说明 |
|---|---|---|
| 选题与脚本 | 大语言模型（本地 Ollama/Qwen + WorkBuddy Agent） | 按 hook 模板生成 3 秒钩子脚本与分镜 |
| 分镜与画面 | ComfyUI（本地部署） | 节点画布编排，见 `workflows/` |
| 图像生成 | Stable Diffusion XL 系列底模 | 竖屏 768×1344，小资中产人设风格 |
| 视频生成 | MiniMax H3 视频模型 | 图生视频，本地 RTX 4090 16GB 推理 |
| 音频/字幕 | ffmpeg + Whisper 字幕 | 统一封装，前 3 秒 hook 校验 |
| 质量控制 | 8-Gate 人工 + 脚本 QC | `scripts/spec_check.py` 自动校验分辨率/规格 |

硬件：单卡 RTX 4090 Laptop 16GB；ComfyUI 官方版本 + ffmpeg 官方构建。

## 8-Gate 质量体系（v3.1）

```
Gate1 选题脚本 → Gate2 分镜表 → Gate3 角色/场景一致性设定 → Gate4 产品参考物料（≥3 角度）
   → Gate5 画布生成 → Gate6 视觉 QC → Gate7 剪辑包装 → Gate8 产品保真终检
```

每个 Gate 保留人工可编辑 hook；任一 Gate 不达标即回退重做，不带着缺陷进入下一阶段。
**Gate 8（产品保真）红线：只允许使用真实产品照片作为参考，禁止用 AI 生成画面充当产品参考图。**

## 目录结构

```
├── docs/
│   ├── 8-gate-sop.md            # 8-Gate 全流程 SOP
│   ├── product-reference-spec.md # 产品参考物料规范（≥3 角度/结构描述）
│   └── prompt-style-guide.md     # 风格与人设规范
├── workflows/
│   ├── consistency-22-nodes.json # 一致性版画布（22 节点，角色/场景/产品一致）
│   └── turbo-fast-25-nodes.json  # Turbo 快采版画布（25 节点，批量候选快速筛选）
├── prompts/
│   ├── script-templates.md       # 脚本/分镜提示词模板
│   └── negative-library.md       # 负面提示词库（产品变形/廉价感/穷苦人设等）
├── scripts/
│   └── spec_check.py             # 出片规格自动校验（分辨率/时长/帧率/黑边）
├── trilogy/                      # 「夏日三部曲」项目档案
└── requirements.txt
```

## 快速开始

1. 安装 ComfyUI（官方版）并放入 `workflows/*.json`（拖入画布即可加载）
2. 准备 Gate4 产品参考物料：真实产品照片 ≥3 角度，见 `docs/product-reference-spec.md`
3. 按 `docs/8-gate-sop.md` 逐 Gate 执行，每 Gate 留痕
4. 出片后运行规格校验：

```bash
python scripts/spec_check.py --input ./renders/ --width 768 --height 1344
```

## 版本记录

| 版本 | 日期 | 说明 |
|---|---|---|
| v1.0 | 2026-10-07 | 仓库初始化：8-Gate SOP v3.1 + 两套基线画布 + 质检脚本 |

> 本仓库为品牌部 AI 应用课题（公司专项工作小组）配套工程资产，公共基线版本以此为准。
