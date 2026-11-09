# 本机日志：真实摘录与脱敏

> 日志范围保持不变：本目录全部摘录来自 **realme GT5 Pro、2026-11-05**。2026-11-09 的 Redmi K40 样本按用户要求跳过日志提取，没有 Redmi 日志或新设备记录混入。

**机型：realme GT5 Pro（RMX3888）；方式：Codex + ADB + su；采集日：2026-11-05。**

这些文本来自本机原始取证输出，采集发生在设备所有者卸载之前。因此 package 摘录中的 installed=true 与之后“用户卸载、重启正常”的反馈不矛盾。

| 文件 | 原始来源 | 处理 |
|---|---|---|
| [package.redacted.txt](package.redacted.txt) | dumpsys package | 选取目标包权限、版本、特权及用户状态；移除包查询关系与其它应用 |
| [appops.redacted.txt](appops.redacted.txt) | cmd appops get | 选取定位、Wi-Fi、使用统计等操作；具体相对时间脱敏 |
| [alarms.redacted.txt](alarms.redacted.txt) | dumpsys alarm | 只选取目标包当前任务与目标包唤醒统计 |
| [netstats.redacted.txt](netstats.redacted.txt) | dumpsys netstats detail | 只保留目标 UID 的 tag=0x0 历史；SSID、subscriberId、UID 与统计桶时间脱敏 |
| [rom-references.redacted.txt](rom-references.redacted.txt) | ROM 配置目录检索 | 仅目标包特权白名单命中位置 |
| [app-logcat-root.empty.txt](app-logcat-root.empty.txt) | root 全缓冲区、按 UID 过滤的 logcat | 原始输出就是 0 bytes；空文件不表示曾有日志后被清空 |

[manifest.json](manifest.json) 保存来源文件名、选中行号、脱敏项目和网络字节汇总。原始文件没有随仓库分发，行号用于维护者对照自己的私有原件；公开文本不是全量原始日志。

## 排除项目

其它应用的所有日志段、具体应用包名和名称、应用使用明细均不进入此目录。设备／SIM 标识、经纬度、SSID／BSSID、用户 IP、设备序列号和精确活动时间也不公开。UID／对象标识用占位符替换；没有修改权限授予结果、任务部件、唤醒次数和收发字节数来支持结论。

可用 `scripts/redact_logs.py --input <私有目录> --output <新输出目录>` 复现本次摘录逻辑；规则针对本次输出格式，不保证适用于所有 Android／ROM。此脚本不读 SQLite 应用明细；应用统计只在 data/observations.json 中保留计数。

网络 tag=0x0 的汇总为上行 2,460,119 bytes、下行 2,680,335 bytes；有标签统计未再次相加，避免重复计算。统计属于整个目标 UID，不能确定每次目的地、请求正文或业务成功状态。
