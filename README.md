# com.mobiletools.systemhelper_analysis

**分析机型：realme GT5 Pro（RMX3888）。分析方式：Codex + ADB + su（root 只读取证）。**

本仓库记录一个指定版本 SystemHelper 的静态代码分析、设备端权限与缓存核对、历史网络统计，以及一条不含真实个人数据的合成请求测试。分析与文稿署名 **Codex**；样本和后续卸载反馈由设备所有者提供。

## 样本与范围

| 项目 | 本次分析对象 |
|---|---|
| 包名 | `com.mobiletools.systemhelper` |
| 机型 | **realme GT5 Pro / RMX3888** |
| Android / ROM | Android 16 / `RMX3888_16.0.10.500(CN01)` |
| APK 版本 | `3.0.1-20250822`，versionCode 31 |
| APK SHA-256 | `9eb0d23aef28b4ed93806bfa9a574814805d362d935a610fb5cb4728a7ca4003` |
| 原系统位置 | `/product/priv-app/SystemHelper-oppo-20250822/SystemHelper-oppo-20250822.apk` |
| 分析日期 | 2026-11-05，UTC+8 |

## 核心发现

- **实机证据**：明文数据库中有 7 条待上报报文；其中两份 AppInfo 分别含 195、225 项，另有 184 条嵌套信号／位置记录及 16 条当前缓存。200 条记录不代表 200 个不同位置。
- **采集字段**：完整设备标识、部分完整 SIM 标识、应用前台使用时长与流量、基站、信号和经纬度。部分 SIM 字段掩码并不使整份记录匿名。
- **上传设计**：默认业务接口为 `http://dm.wo.com.cn:18080/register`；JSON 经 AES-ECB 加密，AES 密钥为该 JSON 的 MD5，RSA 公钥封装密钥。HTTP 无 TLS，不能因此把业务正文直接称为明文。
- **已发生网络收发**：目标 UID 在采集到的系统历史中发送约 2.35 MiB、接收约 2.56 MiB；统计可能混合不同业务／SDK，无法逐条证明真实报文已入库。
- **合成请求**：电脑发送一条标记为 TEST、没有真实标识和位置的加密请求，收到 HTTP 200、空正文。这不是业务入库回执。
- **卸载反馈**：设备所有者反馈，这台 realme GT5 Pro 已通过 root 卸载并正常重启。具体卸载机制未独立核验；通话、短信、双卡、5G、VoLTE 等没有本仓库的完整测试结论。

## 资料导航

- [完整分析报告](docs/analysis.md)：身份、字段、调用链、缓存、加密、权限、后台任务及证据边界。
- [GitHub 结果交叉核对](docs/github-crosscheck.md)：不同版本研究、卸载清单、包名映射和历史 issue；附固定提交链接。
- [分析方法与复现](docs/methodology.md)：Codex + ADB + su，静态工具和二进制读取注意点。
- [三种卸载入口与恢复](docs/removal.md)：无 root PC ADB、有 root ADB su、有 root Android terminal（例如 Termux）。
- [实机日志脱敏摘录](logs/README.md)：权限、AppOps、闹钟和目标 UID 网络统计；不是合成日志。
- [版权／DMCA 与分发边界](docs/publication.md)：哪些材料不分发、哪些材料需自行提取。
- [样本元数据](data/sample.json)、[脱敏汇总](data/observations.json)、[历史合成测试结果](data/synthetic-response.json)。

## 不随仓库分发，需自行提取

**原 APK、DEX／SO、完整反编译源码、完整 AndroidManifest／资源、内置证书文件、厂商固件及其它可能涉及第三方版权或 DMCA 争议的原始材料，均不随本仓库分发。复现者需从自己有权使用的设备或固件中自行提取。**

真实数据库、完整设备日志、设备／SIM 标识、坐标、网络标识，以及具体第三方应用名称与包名也不分发。公开日志只保留 SystemHelper 相关摘录，移除了其它应用记录；这与第三方软件的法律属性判断无关。

仓库中的字段名、样本哈希、方法定位、原创说明和经过筛选的实机日志用于复核结论，不替代原 APK。原始敏感材料由设备所有者在仓库外保管。

## 许可与当前状态

原创内容采用 [WTFPL v2](LICENSE)，范围见 [NOTICE](NOTICE.md)。该许可不能授权第三方作品，也不保证免于 DMCA 投诉。

本仓库最初在本地建立，交由维护者审核；没有由分析助手创建远程仓库或推送。外部资料检索截至 2026-11-05；未登录的 GitHub Code Search API 返回 401，本次结果来自公开索引及原仓库固定提交核对，不宣称穷尽 GitHub 全部命中。
