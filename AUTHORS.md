# 署名与分析方式

- 分析、证据整理与文稿：**Codex**（OpenAI AI 助手，在设备所有者指导下完成）。
- 分析方式：**Codex + ADB + su**；su 用于经设备所有者授权的 root 只读取证。
- 静态工具：JADX 1.5.6、Android SDK aapt2 / apksigner、Java keytool。
- 样本、目标手机及后续卸载测试：设备所有者／仓库维护者，匿名。
- GitHub 外部资料：逐项标注原仓库和固定提交，贡献归原作者。

“Codex”是本项目的工具与文稿署名，不表示 OpenAI 官方安全审计、认证或背书，也不主张 AI 助手独立拥有版权。维护者负责发布前审核与许可范围确认。

## 2026-11-09 新增样本

Redmi K40／HyperOS 3 来源由设备所有者提供；Codex 仅使用本地 APK 做静态分析和对比。设备无 root，按用户要求跳过日志提取与动态验证，不把“Codex + ADB + su”误写为本轮对 Redmi 的实际操作。
