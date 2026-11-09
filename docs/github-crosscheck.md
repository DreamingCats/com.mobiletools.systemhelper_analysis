# GitHub 包名检索：结果分类与交叉核对

> 本页外部资料检索仍截至 2026-11-05。2026-11-09 新增 [Redmi K40 本地样本对比](redmi-20260313.md)，不将前次外部研究、不同日期版本或 realme 实机结果视为 Redmi 新样本实测。

检索日期：2026-11-05。与本项目对照的实机是 **realme GT5 Pro（RMX3888）**，样本 `3.0.1-20250822`；分析方式为 **Codex + ADB + su**。

## 检索覆盖与证据权重

尝试 GitHub 官方 Code Search API，精确查询 `"com.mobiletools.systemhelper"`，未认证接口返回 **401 Requires authentication**；网页代码搜索也没有提供可读取的完整结果集。随后利用公开网页索引定位仓库，并直接读取 GitHub 原仓库文件、Git tree 与提交信息。没有冒充已执行完整的登录代码搜索，也不把搜索摘要当作代码证据。

本轮核对 8 个仓库、16 个固定提交文件和 2 个 issue，清单见 [github-sources.json](../data/github-sources.json)。仓库固定提交可复核；issue 正文仍可被作者编辑，记录了检索时的 created_at／updated_at。没有读取或公开 issue 作者的完整设备属性转储。

较多命中属于包名列表、工具配置、转述和派生精简清单；它们不是同等数量的独立逆向审计。“出现在源码仓库”也不等于该仓库是 APK 开发者。

## 两份较深入研究

### LING71671/systemhelper-privapp-audit

[原始分析（固定提交）](https://github.com/LING71671/systemhelper-privapp-audit/blob/f611e23b56329b2d82dcae38e1d432f2261d6334/docs/analysis.md#L10)。对象为小米设备的 `3.0.1-20250311`，SHA-256 为 `5267008ede808c467988df588915791d21a6f1f3fbe219c57b125a235000df4f`；与本项目样本不同。

其字段／厂商开关判断与本次观察总体相符，但默认定位周期为 1 小时，本机为 30 分钟。该项目以无 root 条件观测；本项目额外读取了私有缓存。短时无新增流量不能用于否认本机历史收发，版本默认值也不能互相替代。UID 的不同本身不构成矛盾。

### Liu8Can/HyperOS-Security-Analysis

[SystemHelper 分析（固定提交）](https://github.com/Liu8Can/HyperOS-Security-Analysis/blob/9210a223e7db4256139ae46c2f91f9b303e5f581/docs/02_systemhelper_telemetry_analysis.md#L5)。文中设备为 Redmi K80 系列／Android 15，展示载荷的 ClientVersion 为 `3.0.1-20241118`，不能视为本次 realme APK 的同版本证据。

需要限定：该文未发现应用前台时长，不代表本版本没有；本机缓存有 AppInfo 和非零 runTime。HTTP 无 TLS 不等于正文未加密；本样本可确认 AES／RSA 封装。该文对协议标准归属和卸载通信安全的表述，本仓库没有足够证据照搬。

本项目只审计 SystemHelper，不把外部报告中的其它包、音视频功能或主观动机并入结论。不同样本和方法可能解释差异，不能据此断言外部所有观察都错误。

## 清单、映射与历史记录

| 来源 | 实际命中 | 能支持的结论与限制 |
|---|---|---|
| [UAD-NG 当前固定条目](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/41ed5fc76b465d0f52f16f10b07250a2ae445e68/resources/assets/uad_lists.json#L2068) | Oem / Recommended，简述双卡和 App Info，依赖字段为空 | 社区处置建议；空依赖列表不证明所有 ROM 无依赖 |
| [旧 UAD 固定条目](https://github.com/0x192/universal-android-debloater/blob/11f27c671cba278d71296cdef4c5a5dba06add5e/resources/assets/uad_lists.json#L13044) | 也标为 Recommended，说明很短 | 与后继项目有继承关系，不能当成完全独立审计 |
| [ReduceMIUI](https://github.com/DavidPisces/ReduceMIUI/blob/e2369942bb6309de4a9ae0337f6c0b938cbff59e/common/%E5%8C%85%E5%90%8D%E7%B2%BE%E7%AE%80.prop#L254) | 包名精简配置中出现 | 至少该版本配置列出目标包；不建议直接执行整个模块代替单包处置 |
| [meizu-removed-app](https://github.com/alfaslash/meizu-removed-app/blob/905848eb647a91fedf3bdb91e18052c311fbe10e/apps.yml#L82) | 应用清单映射 | 只有标签级信息，没有本 APK 哈希／代码／流量证据 |
| [emra](https://github.com/hosizoraru/emra/blob/ee0fa822ef8934ef85cede2ff89c80ca7a00bdad/app_name_pad.json#L83) | 包名到 SystemHelper 的名称映射 | 工具识别信息，不是隐私审计或卸载验证 |
| [Xiami-Redmi-Note-No-More-Bloatware-](https://github.com/Emmanuel1017/Xiami-Redmi-Note-No-More-Bloatware-/blob/49cea7babffac1604cf22cc1736646fe48e2f4f2/README.md#L70) | README 的精简列表 | 项目作者的处置范围，不推广到本机以外的通信兼容性 |
| [UAD issue #858](https://github.com/0x192/universal-android-debloater/issues/858) | 2023 年 MIUI 国行列表及目标包单独小节 | 是历史包存在与社区经验线索；不是全 ROM 兼容性证明 |
| [bkerler/edl issue #548](https://github.com/bkerler/edl/issues/548) | 2024 年提交的 vivo 属性 `ro.vivo.unicom.dm.name` 指向此包 | 支持 vivo ROM 配置曾关联联通 DM 名称；不能单凭属性证明 APK 已安装或当时发生上传 |

issue #858 的搜索摘要容易混入相邻条目。原文中 `com.miui.packageinstaller` 及 `com.android.connectivity.resources` 的 bootloop 提示不属于 `com.mobiletools.systemhelper`；目标包自己的小节是 Recommended。不能从拼接摘要得出 SystemHelper 导致 bootloop。

本轮没有取得可独立校验哈希的 OPPO／vivo／魅族各型号完整样本集合；列表和属性不支持“所有该品牌设备都预装同一实现”的结论。

## 对本项目结论的影响

- 历史清单支持它不是近期才出现的单一品牌组件；业务归属仍主要由本机签名元数据、内置公钥标识、URL 和 ROM 集成引用支持。
- 本机逐应用统计和位置缓存是独立实机证据，不能被别的设备的缺失观察覆盖。
- 自定义 JSON／加密上报接口不足以证明完整实现了 OMA-DM 或 TR-069 标准。
- 默认周期、厂商授权开关、背景限制和卸载结果均应按样本、ROM 和实测分别报告。
- 社区 Recommended 与本机重启正常都增加处置可行性的证据，但没有替代通话、短信、双卡、5G、VoLTE 等逐项验证。

## 引用与许可证

外部材料仅链接、定位与原创评论，未将原报告、源码和清单整体复制进本仓库。UAD／ReduceMIUI 的仓库元数据标识 GPL-3.0，Liu8Can 项目标识 MIT，emra 标识 WTFPL；其余部分仓库未提供 GitHub 可识别的许可证。以各固定版本的实际 LICENSE 为准，不能假定“GitHub 公开”就能整体改用本仓库 WTFPL。
