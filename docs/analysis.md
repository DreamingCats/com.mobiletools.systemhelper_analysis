# SystemHelper 3.0.1：独立静态分析、实机日志与待上报数据核对

> 范围：本页保留 **realme GT5 Pro / 3.0.1-20250822** 的原始分析与实机证据。2026-11-09 新增的 **Redmi K40 / 3.0.1-20260313** 仅静态分析，参见 [Redmi 专页](redmi-20260313.md)；不要把本页日志、缓存、流量和卸载结果套用到 Redmi。

> 后续验证：设备所有者反馈，realme GT5 Pro 已通过 root 卸载并正常重启。具体卸载方式未独立核验，通信功能尚未逐项验证；详见 [卸载与恢复](removal.md)。

**分析方式：Codex + ADB + su（root 只读取证）；分析与文稿：Codex。**

分析日期：2026-11-05，北京时间。对象：realme GT5 Pro / RMX3888，Android 16（API 36），ROM `RMX3888_16.0.10.500(CN01)`，安全补丁 2026-08-01。

## 1. 已确认的主要结论

- **实机已采集敏感信息**：从本地明文 SQLite 取出 7 条待上报报文与 16 条信号采集缓存，包含完整 IMEI、部分完整 IMSI/ICCID、应用使用统计、双卡流量、基站及经纬度。不是仅凭权限或 API 名字推断。
- 7 条待上报报文内有 195 / 225 项 AppInfo，以及 46 / 48 / 48 / 42 条 SigInfo。总计导出 **200 条信号/位置记录**（184 条嵌套历史记录 + 16 条当前缓存）；同一时刻不同 SIM 可重复记录位置，不能说有 200 个不同位置。
- 目标应用 UID 的系统网络历史中，2026-10-23 22:00 至 2026-11-05 18:00 起始的两小时统计桶，累计发送 **2,460,119 bytes（约 2.35 MiB）**、接收 **2,680,335 bytes（约 2.56 MiB）**。这是整个 UID 的流量，可能混合联通上报和百度 SDK 请求，不能据此还原请求正文或目标服务器。
- 没有找到现存应用 logcat 中的历史 HTTP 回执。不能确定上述哪条真实数据已被云端接收，也不能恢复全部历史上传内容。
- 按用户要求，由电脑发送了一条不含真实个人数据的 TEST 合成加密请求，默认接口返回 HTTP 200、空正文。此结果证明当前链路能得到成功状态响应，**不证明业务校验或入库成功**。
- 取证时应用确实是 privileged system app；共享 UID 下只发现它自己。Codex 取证阶段未禁用、卸载、安装模块、重启或修改应用配置；之后设备所有者反馈已 root 卸载、重启正常。Codex 没有主动触发手机真实采集／上报。

## 2. APK 身份、签名与结构

本地样本和手机 `/product/priv-app/SystemHelper-oppo-20250822/SystemHelper-oppo-20250822.apk` 都是 3,744,059 bytes，SHA-256 均为：

`9eb0d23aef28b4ed93806bfa9a574814805d362d935a610fb5cb4728a7ca4003`

`apksigner verify --verbose --print-certs` 验证通过：v2=true；v1/v3/v3.1=false；未提供独立 v4 `.idsig`。只有一个签名者，DN `CN=NewDM, OU=RI, O=CU, L=BJ, ST=BJ, C=86`，RSA-2048。

签名证书 SHA-256：`874b8ca2297f53a373b1b935c134cb0eb1ff7381e54491b88c643a6b9c46db77`。

另有 `assets/pub.cer`，Owner/Issuer 都为 `CN=UNICOM, OU=UNICOM, O=UNICOM, L=BJ, ST=BJ, C=CN`，**RSA-1024**，用途是加密请求 AES 密钥。它与 APK 签名证书不是同一证书。其 SHA-256 为 `810c0122ba6af7a4b6a5921fdbbbf9197fb2e0b2e82de0c5aa40d28f1b7c6501`。

NewDM 签名信息、UNICOM 公钥、`dm.wo.com.cn` 地址，以及 ROM 权限 XML 中“CU auto register / cu test request”的集成注释，共同支持“联通设备自注册/统计业务组件”的判断。ROM 集成方是 realme/OPlus。自报证书 DN 不能独立证明实际承包开发公司、法定证书持有主体或每个渠道的发布者；没有证据把它归为 Google 开发。

Manifest：包名 `com.mobiletools.systemhelper`，versionCode=31，minSdk=31，targetSdk=33，`sharedUserId=com.mobiletools.systemhelper.uid`，不是 `android.uid.system`；`allowBackup=false`，`usesCleartextTraffic=true`。只有一个 `classes.dex`，另有 ARM64 `libindoor.so` 与 `liblocSDK8b.so`。未在反编译 Java 中发现 DexClassLoader / InMemoryDexClassLoader / PathClassLoader 引用；不据此保证 native 层不存在其它动态行为。

完整 Manifest、反编译源码、证书文件与 APK 不随仓库分发，需从有权使用的设备或固件自行提取。公开身份与证书元数据见 [sample.json](../data/sample.json)。

## 3. 日志与实际留存数据

本机已有的 UID logcat、root 全缓冲区 UID logcat 和业务标签 logcat 均为空。主要日志包装函数由默认关闭的开关控制，但少数代码直接使用 Android Log，因此不能把“当前缓冲区无日志”写成“从未记录过日志”。

原始 SQLite 在设备所有者授权下通过 su 复制。两库完整性检查均为 ok，分别有 7 条待上报记录和 16 条信号缓存；采集时没有冻结应用。7 条报文中有两份 AppInfo（195／225 项，分别有 36／51 项非零前台时长）、四份 SigInfo（46／48／48／42 条）及一份周期注册报文。加上 16 条独立缓存，共 200 条信号／位置记录，双卡可能重复位置。

原始设备／SIM 标识、位置、应用名称和包名、原始数据库及完整日志不分发。公开实机日志见 [logs](../logs/README.md)，只保留目标应用相关摘录，并有来源行号和脱敏规则。应用明细全部排除，只公开计数。

缓存通常由未发送、发送条件不满足或失败产生，不能当作云端已收到的历史清单；自增序号也不是成功上传次数。脱敏汇总见 [observations.json](../data/observations.json)。

## 4. 采集字段与限制

### 4.1 设备注册顶层字段

`Manuf`, `Model`, `HWVersion`, `SWVersion`, `OS`, `OSVersion`, `IMEI1`, `ICCID1`, `IMSI1`, `MNC1`, `NetworkType1`, `TAC1`, `CID1`, `PCI1`, `VolteEnabled1`, `5GEnabled1`, `VoNREnable1`, `IMEI2`, `ICCID2`, `IMSI2`, `MNC2`, `NetworkType2`, `TAC2`, `CID2`, `PCI2`, `VolteEnabled2`, `5GEnabled2`, `VoNREnable2`, `DataSlot`, `AccType`, `IPv6`, `SubType`, `DeviceType`, `RegType`, `SpecVersion`, `ClientVersion`, `Time`，以及 `AppInfo`、`SigInfo`。`SubType` 下有 `RAM`、`ROM`、`FREE`。基本设备标识调用链：`f1.g.b()`（realme 分支）→ `f1.a.b()/p()/q()` 等采集方法 → `f1.o.k()/l()` 排序与处理 → `e1.b.b()` JSON。

证据：`f1/g.java:9`, `f1/a.java:446`, `f1/a.java:239`, `e1/b.java:132`。

**掩码不是全面匿名化**：本机缓存中 IMEI1/2 都是完整数字；一组 IMSI/ICCID 有星号，另一组完整；一组 TAC/CID 呈 64 位十六进制摘要。代码对非联通前缀的 SIM 做部分掩码/基站 SHA-256，联通前缀为 46001/46006/46009/46010。仍有其它可关联标识；不能宣称匿名。证据：`f1/o.java:278`, `g1/l.java:242`, `g1/i.java:16`。

### 4.2 应用安装及使用统计

`getInstalledApplications(0)` 用于补全 UID/应用标签；输出主体来自 `queryAndAggregateUsageStats(now-86400000, now)` 的返回项，按前台时间排序。没有看到 Top-N 截断，也没有按 `FLAG_SYSTEM` 全面排除系统应用。随后仅按包名前缀排除 `com.android`，所以厂商/运营商等系统包仍可能进入报文。不能把这个列表等同于当前全部已安装应用的完整快照。

每项字段：`appLabel`、`pkgName`、`Time`、`runTime`、`tx1`、`rx1`、`tx2`、`rx2`、`totalData1`、`totalData2`、`totalDataWiFi`。前台时间取整数分钟；双卡流量为整数 KB，Wi-Fi 总流量为整数 MB，零值可能是舍入或无数据。没有上传访问内容、聊天正文或网站历史的这条代码链证据。

应用流量按 UID 汇总，同 UID 的包可能共用统计；此代码仅捕获部分 RemoteException，权限错误并不保证优雅降级。UsageStats 的统计边界还受到系统聚合桶规则影响。

证据：`e1/f.java:172`, `e1/f.java:189`, `f1/o.java:41`, `g1/b.java:55`。

### 4.3 定位、基站与信号

信号字段：`Time`, `IMEI`, `ICCID`, `ClientVersion`, `MNC`, `IMSI`, `TAC`, `CID`, `PCI`, `NetworkType`, `ARFCN`, `Bands`, `Bandwidth`, `CQITableIndex`, `CQIIndex`, `RSRP`, `RSRQ`, `SINR`, `CSIRSRP`, `CSIRSRQ`, `CSISINR`, `Uspeed`, `Dspeed`, `CallDisconnectCause`, `DataFailCause`, `EPSFallback`, `LONGITUDE`, `LATITUDE`, `ALTITUDE`, `SPEED`, `BEARING`。

`GetSignalInfoReceiver.onReceive()` 设百度定位客户端 `Hight_Accuracy`、坐标系 `bd09ll`、`p(0)`（SDK 内部 scanSpan=0），由外部 AlarmManager 大约每 30 分钟重新触发。不能据此说 GPS 始终持续高频运行，也不能保证每 30 分钟有一个成功定位。成功回调后按双卡读取 TelephonyManager 的标识、ServiceState/CellIdentity、SignalStrength，组装 `g1.n.a()`，写 `signalhelper`。仅网络运营商码以 460 开头时进入该缓存分支，涵盖中国移动/联通/电信等，并非只针对联通 SIM。

**字段语义缺陷**：`e1.d.a()` 把网络连接状态 `Mobile/WiFi/Disconnected` 写入 `n.H`，而 `g1.n.a()` 将它序列化为 `BEARING`。因此实机报文的 BEARING 不能当作运动方向。部分 SPEED、Uspeed/Dspeed、CSI、故障字段实机为空；Android 不可用值也可能被直接转成字符串，不能把所有非空值当成有效测量值。

证据：`com/mobiletools/systemhelper/control/GetSignalInfoReceiver.java:46`, `com/mobiletools/systemhelper/control/GetSignalInfoReceiver.java:147`, `e1/d.java:140`, `g1/n.java:142`。

## 5. 从采集到上传的调用链

```text
AppInfoRegisterReceiver → e1.b.a(context,"A") → f1.o.d/k/l
  → e1.f（UsageStats/NetworkStats）→ f1.o.a 回调 → e1.c（IPv6）→ e1.g

GetSignalInfoReceiver → 百度定位回调 + e1.d（双卡基站/信号）
  → g1.n.a() JSON → g1.m.c() 明文 signalhelper
SignalInfoRegisterReceiver → e1.b.a(context,"R") → f1.o.d()
  → 取全部 signal 组成 SigInfo → 立即清空 signal 表 → e1.c → e1.g

开机/周期/SIM 相关注册 → e1.b.a(context,"F/B/S/T") → f1.o → e1.c/e1.g

e1.g：检查权限开关/中国网络/连接条件
  ├─满足条件：JSON → MD5(JSON) 作为 AES 密钥 → RSA 包装密钥 → HTTP POST
  │   └─当前发送被代码视为成功后：e1.e 取一条历史缓存重发
  └─不发送或失败：g1.e.b() 保存原始 JSON 到 systemhelper.dmregister
```

网络条件：Wi-Fi 且中国网络判断通过，或使用被代码识别为联通的移动数据且非漫游。缓存不是单纯“服务器拒绝日志”；离线、发送条件不满足也会产生缓存。

**不能用缓存缺失证明成功**：`f1.o.d()` 在网络发送前就清空 signal 表；历史缓存 `g1.e.c()` 用 moveToLast 取一条并在发送前删除（方法日志名虽叫 queryOldestRecord，代码并不是取最旧），重发失败没有看到重新入队。主缓存插入前的削减逻辑使其通常最多约 11 条，signal 表通常最多 100 条。这也解释历史并不完整。

证据：`e1/g.java:59`, `e1/e.java:64`, `g1/e.java:85`, `g1/m.java:49`。JADX 默认输出在 `f1.o.d()` 有不正确的控制流结构，已使用 simple 模式对照：本地 simple 模式输出（不随仓库分发），其中线程启动与清库顺序更清楚。

## 6. 协议、加密与服务端控制

当前未保存 serverAddress 覆盖项，默认业务地址为 `http://dm.wo.com.cn:18080/register`。

```text
POST /register?ver=5.0&model=<URL编码型号>&manuf=<URL编码厂商>&sign=<URL编码Base64的RSA密文>
Content-Type: application/encrypted-json
Content-Length: <AES密文字节数>

Body = AES-128-ECB-PKCS5Padding(UTF8(JSON), key=MD5(UTF8(JSON)))
sign = RSA-ECB-PKCS1Padding(pub.cer 公钥, 上述16字节AES密钥)
```

AES 密钥不是随机生成，也没有看到长期落盘；它是**该条明文 JSON 的 MD5 摘要**。RSA 加密的是 AES 密钥，不是完整 JSON；参数名 sign 在这里不是数字签名。业务 Body 是二进制 AES 密文，HTTP 请求行里的厂商、型号和其它参数仍可见。不能把它说成“真实 JSON 全部明文 HTTP 传输”，也不能把它等同于具备 TLS 的认证、保密与完整性保护。

安全评价：ECB 不隐藏重复块结构；相同 JSON 的 AES Body 是确定性的；未见业务 MAC/AEAD 或设备私钥签名；HTTP 响应没有 TLS 身份保护。RSA-1024 已弱于现代常用配置。缺少独立随机密钥和完整性保护是设计缺陷，但此次没有演示从密文恢复未知真实数据，不宣称已解密历史抓包。

`g1.f.b()` 的 HTTP 分支把 200 视为成功；外层 e1.g/e1.e 还把 416 视作可接受。没有读取业务响应正文的代码，因此这条主上报链未发现“解析服务端响应以执行远程指令”的流程。百度 SDK 自身另有服务端配置解析，不能与主上报混为一谈。HTTPS 分支使用 HttpsURLConnection 默认行为；它并非默认业务 URL。

本地配置/Binder 可以改地址、周期、日志开关。**额外发现**：RegisterHelperService 被 exported=true 导出，却没有挂声明的 signature 权限；onBind/onTransact 未见调用方权限或签名校验。其 c(String) 写 serverAddress，a(int) 改间隔，d(boolean) 改日志，e() 删除配置。这是静态发现的本地 IPC 暴露风险；未安装测试应用去验证本 ROM 的调用可达性，也没有改过这些值。

证据：`g1/c.java:63`, `g1/c.java:24`, `g1/j.java:21`, `e1/g.java:35`, `g1/f.java:24`, `com/mobiletools/systemhelper/service/RegisterHelperService.java:39`, `com/mobiletools/systemhelper/service/a.java:23`。

## 7. 网络地址清单

以下是 Java 静态字符串清单，不是实机连接清单；百度 SDK 中有按功能条件才会使用的接口，不能认定每个都访问过。

| URL | 源文件（JADX） |
|---|---|
| `http://dm.wo.com.cn:18080/register` | `g1\d.java` |
| `http://ofloc.map.baidu.com/offline_loc` | `i\d.java` |
| `https://api.map.baidu.com/sdkcs/verify` | `a1\b.java` |
| `https://daup.map.baidu.com/cltr/rcvr` | `n\d.java` |
| `https://itsdata.map.baidu.com/long-conn-gps/sdk.php` | `b\j.java` |
| `https://loc.map.baidu.com/cc.php` | `b\j.java` |
| `https://loc.map.baidu.com/cfgs/indoorloc/indoorroadnet` | `n\d.java` |
| `https://loc.map.baidu.com/cfgs/loc/commcfgs` | `n\d.java` |
| `https://loc.map.baidu.com/check_indoor_data_update` | `n\d.java` |
| `https://loc.map.baidu.com/gpsz` | `c\a.java` |
| `https://loc.map.baidu.com/indoorlocbuildinginfo.php` | `d\a.java` |
| `https://loc.map.baidu.com/sdk.php` | `n\d.java` |
| `https://loc.map.baidu.com/sdk_ep.php` | `n\d.java` |
| `https://ofloc.map.baidu.com/LocBrokerService/do_loc_map_match` | `n\d.java` |
| `https://ofloc.map.baidu.com/PlanarStartService/detect_parking_exits` | `n\d.java` |
| `https://ofloc.map.baidu.com/locnu` | `b\x.java` |
| `https://ofloc.map.baidu.com/offline_loc` | `i\b.java, i\c.java, i\f.java` |
| `https://parking.baidu.com/parking/api/parkingdata/getcarportlistforlocation?` | `n\d.java` |

另有 SDK 的 `http://%s/%s` 模板；SO 内可见的 android.googlesource.com 是编译器来源字符串，不应算成采集服务器。该表来自本地静态字符串提取；不随仓库附带原反编译代码或 SO。主业务固定地址只看到联通这一个，动态覆盖通过本地 serverAddress，不排除 SDK native 层生成或配置的额外地址。

## 8. 实机权限、后台调度与不同 ROM 的边界

UID/appId 已脱敏，SYSTEM + PRIVILEGED + PRODUCT。`dumpsys package` 的 shared user 部分只包含本包；并不是系统 UID，也没有因本次分析而获得手机 root。

| 能力/权限 | 本机证据 | 结论范围 |
|---|---|---|
| READ_PRIVILEGED_PHONE_STATE | granted=true，ROM 特权白名单引用 | IMEI/IMSI/ICCID 实际存在于数据库，读取不是理论能力 |
| READ_PHONE_STATE / READ_PRECISE_PHONE_STATE | granted=true | 实际基站/信号/通信状态采集有数据支持 |
| FINE/COARSE/BACKGROUND_LOCATION | granted=true，AppOps allow，近期访问 | 实际后台位置采集有本地记录 |
| PACKAGE_USAGE_STATS | granted=true；GET_USAGE_STATS=default 且有 rejectTime | 不能把 default 当成恒定拒绝；历史 AppInfo 证明它曾获得统计结果，当前调用是否被 ROM 另行限制未做主动调用测试 |
| QUERY_ALL_PACKAGES | granted=true | 结合 UsageStats 生成列表，不等于每次上传全部安装包 |
| SCHEDULE_EXACT_ALARM | granted=true，实际注册四类任务 | 实际有唤醒执行记录，系统可能调整触发时间 |
| INTERNET/网络状态/Wi-Fi 状态等 | granted=true，UID 历史流量 | 确认发生过网络收发，不能直接归属每条接口 |
| READ_EXTERNAL_STORAGE | dumpsys granted=true，但 LEGACY_STORAGE 等为 ignore | Android 16 下不能据此认为可任意读取全部媒体/文件 |

ROM 权限引用位于 `/system_ext/etc/permissions/privapp-permissions-oplus-common.xml:901`，注释指向 CU auto register。它在与 APK 不同分区的配置中，而 AOSP 文档通常要求同分区授权；本 ROM 的最终 granted 状态才是此次实际结果，不能单凭该 XML 断言授权来源与标准 AOSP 完全一致。参考 [AOSP 特权权限白名单](https://source.android.google.cn/docs/core/permissions/perms-allowlist?hl=en)。

定时默认值（g1.d + g1.a + g1.l）：AppInfo 24 h、Schedule 24 h、SignalInfo 12 h、GetSignalInfo 30 min；前三者在进程初始化后的首轮可加入 0—24 h 随机偏移。通过 SharedPreferences 可覆盖；实机配置未看到周期覆盖项。使用一次性 ELAPSED_REALTIME_WAKEUP 的 setExactAndAllowWhileIdle，并在接收时排下一次，不是 setRepeating。实机 AlarmManager 显示了 ROM 批处理/窗口调整，不能保证精确准点。

当前 AlarmManager 统计窗口约 12.85 天：总 523 次唤醒，其中 GetSignalInfo 474、SignalInfo 23、Schedule 12、AppInfo 12、OnBoot 1、SIM 1。保存了当前四类 pending alarm；没有运行中的 Service 也不等于定时任务未运行。jobscheduler 输出未发现该包当前已注册任务，主要执行证据是 AlarmManager。

realme 的采集开关只检查 device_provisioned=1；vivo 分支还检查 operator_service_improve_plan。取证时本机两项设置均为 1，不能从“用户改进计划”的字段名推断 realme 代码确实用该开关阻断采集。其它 Android/ROM 的特权白名单、默认授权、AppOps、运营商权限和 OEM 限制都必须各自实测，不能推广本机结果。

## 9. 合成请求测试：实际 HTTP 响应

2026-11-05，电脑通过既有环境网络配置，向默认业务 URL 发送一条标记为 TEST 的合成报文。使用本样本的 MD5→AES-ECB、RSA 公钥封装格式；没有使用真实手机数据库中的任何标识、应用明细或位置。请求 AES Body 为 240 bytes，没有重试或跟随跳转。

响应为 HTTP 200 OK、Content-Length: 0、空正文，耗时约 0.132 秒。响应包含网关追踪头，但其值未公开。不能据此区分前置网关和业务后端处理，也不能证明通过业务校验或入库，更不能倒推过去真实记录的上传结果。

此为既有实验记录：[结果](../data/synthetic-response.json)、[合成明文](../examples/synthetic-payload.json)。本仓库未提供自动向生产端点发送请求的脚本，未包含厂商公钥文件。该实验不是未知真实密文解密或鉴权绕过验证。

## 10. 依赖与卸载后的证据范围

本样本代码主要实现设备注册、应用统计、信号和位置采集；未发现它实现基带、电话账户、短信 Provider 或核心 IMS 服务。共享 UID 下只发现它自己，已检查的 ROM 配置目录中找到的是特权授权引用。没有全量审计其它 ROM APK/framework/native 的调用方，因此“未发现硬依赖”不等于“证明所有场景都没有依赖”。

设备所有者后续反馈：**这台 realme GT5 Pro 已通过 root 卸载 SystemHelper，重启正常。** 具体卸载机制未独立核验，通话、短信、双卡数据、5G、VoLTE、VoWiFi、运营商激活、OTA 均没有本项目逐项验证记录。

按要求列出的三个卸载入口、恢复方法和验证范围见 [removal.md](removal.md)。原始 APK 目录的 systemless 隐藏与用户 0 卸载是不同机制；本公开仓库不附带第三方模块安装器或厂商二进制。

## 可复核材料与限制

- 分析机型为 realme GT5 Pro（RMX3888），分析方式为 Codex + ADB + su；见 [方法](methodology.md)。
- 字段与方法定位基于本地 JADX 1.5.6 输出；反编译行号并非厂商源代码行号，也不保证其它版本的混淆类名一致。
- 全包 JADX 报告 6 个错误；关键 DeviceManager 流程额外用 simple 模式检查，实际字段与本机数据库交叉核对。没有宣称完整还原 native SDK。
- 公开 [日志](../logs/README.md) 是真实提取结果的筛选与脱敏摘录，原始材料保留在仓库外；[汇总](../data/observations.json) 不是原始日志。
- 原始 APK、完整反编译结果、完整资源与证书等可能涉及版权／DMCA 的材料不随仓库分发，需自行依法提取，见 [发布说明](publication.md)。

有设备标识、应用使用与带时间位置可关联的实机证据；本地明文缓存与自定义 HTTP 加密存在隐私及安全设计问题。但没有全部历史请求正文与服务端日志，不能把采集、缓存、网络收发和服务端成功入库混同。
