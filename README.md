# 初见 Codex 自定义宠物

这是一个可以导入 Codex Desktop 的自定义宠物包。角色形象是古风 Q 版小人，适配 Codex 当前的宠物 spritesheet 格式。

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

如果 Codex 没有立刻切换宠物，请重启 Codex，或进入 `设置 -> 外观 -> 自定义宠物` 手动选择“初见”。

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

## Codex 格式说明

Codex 自定义宠物使用一张固定尺寸 spritesheet：

- 总尺寸：`1536 x 1872`
- 网格：`8` 列 x `9` 行
- 单帧：`192 x 208`
- 状态行：`idle`、`running-right`、`running-left`、`waving`、`jumping`、`failed`、`waiting`、`running`、`review`

## 备注

当前宠物包面向 Codex Desktop 的本地自定义宠物功能。Codex 版本更新后，如果自定义宠物格式发生变化，可能需要重新生成 spritesheet。
