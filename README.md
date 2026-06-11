# 初见 Codex 自定义宠物

这是一个可以导入 Codex Desktop 的自定义宠物包。角色是古风 Q 版小人「初见」，已适配 Codex 当前的桌宠 spritesheet 格式。

## 预览

![spritesheet preview](preview/spritesheet-preview.png)

## 一键安装

在 Windows PowerShell 中运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

安装脚本会：

- 复制 `pet/pet.json` 和 `pet/spritesheet.webp` 到 `%USERPROFILE%\.codex\pets\chujian`
- 将 `%USERPROFILE%\.codex\config.toml` 中的 `selected-avatar-id` 设置为 `custom:chujian`

如果 Codex 没有立刻切换宠物，请重启 Codex，或进入 `设置 -> 外观 -> 自定义宠物` 手动选择「初见」。

## 手动安装

1. 创建目录：

```text
%USERPROFILE%\.codex\pets\chujian
```

2. 复制以下文件：

```text
pet/pet.json -> %USERPROFILE%\.codex\pets\chujian\pet.json
pet/spritesheet.webp -> %USERPROFILE%\.codex\pets\chujian\spritesheet.webp
```

3. 在 `%USERPROFILE%\.codex\config.toml` 的 `[desktop]` 段中设置：

```toml
selected-avatar-id = "custom:chujian"
```

## 状态动作

优化版 spritesheet 覆盖 Codex 的 9 行状态：

| 行 | 状态 | 动作设计 |
|---|---|---|
| 0 | `idle` | 安静站立，轻微呼吸 |
| 1 | `running-right` | 纸蛇向右滑动，带小星光 |
| 2 | `running-left` | 纸蛇向左滑动，带小星光 |
| 3 | `waving` | 挥手问候 |
| 4 | `jumping` | 开心跳起，星光反馈 |
| 5 | `failed` | 休息/阻塞气泡 |
| 6 | `waiting` | 提灯等待，带提示气泡 |
| 7 | `running` | 工作中，带思考星光 |
| 8 | `review` | 卷轴完成，带勾选提示 |

## Codex 格式

- 总尺寸：`1536 x 1872`
- 网格：`8` 列 x `9` 行
- 单帧：`192 x 208`
- 支持格式：`webp` 或 `png`

## 文件结构

```text
pet/
  pet.json
  spritesheet.webp
preview/
  spritesheet-preview.png
source-assets/
  pet-sheet.png
install.ps1
uninstall.ps1
```
