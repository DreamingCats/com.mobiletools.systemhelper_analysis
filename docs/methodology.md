# 分析方法与复现

> 2026-11-09 补充：Redmi K40（用户提供 HyperOS 3）样本只在本地静态分析，按用户要求不提取日志、不做设备动态验证；本页 ADB／su 取证步骤与二进制复制经验来自 realme GT5 Pro。Redmi 的元数据、验证方法与比较见 [专页](redmi-20260313.md)。

## 机型、方式与授权

**机型：realme GT5 Pro（RMX3888）。分析方式：Codex + ADB + su。** 设备所有者授权读取本机 SystemHelper。Codex 用 ADB 读取包状态、AppOps、AlarmManager 和网络历史，用 su 复制应用私有配置及数据库；这些取证操作没有修改应用配置。

静态部分使用 JADX 1.5.6、aapt2、apksigner、keytool；本地 JSON／SQLite 处理使用 Python，合成协议报文构造使用 Node.js。用户后续 root 卸载和重启由用户自行完成，单独列为用户反馈；合成网络实验从电脑执行，不是手机真实数据上报。

## 自行取得样本

仓库不提供 APK、DEX、SO、资源、内置证书和完整反编译源码。复现者需自行从有权使用的设备或固件提取。先查实际路径，不要假设其它 ROM 与本机一致：

```powershell
adb shell pm path com.mobiletools.systemhelper
adb shell dumpsys package com.mobiletools.systemhelper
```

如包仍可读取，再用 `adb pull` 将上一步实际返回的 APK 路径复制到仓库外的私有目录。用户空间卸载、systemless 隐藏和物理删除的可见路径不同；包查不到时应先确认自己的操作方式或使用有权取得的原固件。

## 只读取证

```powershell
adb shell cmd appops get com.mobiletools.systemhelper
adb shell dumpsys alarm
adb shell dumpsys netstats detail
adb shell pm list packages --uid <从包状态读取的UID>
```

这些完整输出可能包含其它应用、SSID、网络标识及活动时间，默认作为私有材料处理。公开日志摘录见 [logs](../logs/README.md)。

本机 APatch 的普通 `adb shell su` 最初失败，以下方式获得 root；这是本机观察，不要求其它 root 实现支持同样参数：

```powershell
adb shell env /system/bin/su --no-pty -c 'id'
```

复制 tar / 数据库等二进制时，必须避免 su 的伪终端转换换行。此次早期有一份经过 PTY 的 tar 损坏，未用于证据；有效副本采用 `--no-pty`，并由 Python 的二进制 stdout 文件句柄保存。不要把所有旧版 PowerShell 文本重定向当作二进制安全。

```python
# 仅在自己的设备和私有输出目录中使用；真实资料不要提交仓库。
import subprocess
command = [
    'adb', 'exec-out', 'env', '/system/bin/su', '--no-pty', '-c',
    'tar -C /data/user/0/com.mobiletools.systemhelper -cf - shared_prefs databases files'
]
with open('private-app-data.tar', 'wb') as destination:
    subprocess.run(command, stdout=destination, check=True)
```

解包也应在仓库外完成。静态分析时自行提取 classes.dex；不要将完整反编译结果加入公开仓库。

## 静态和缓存核对

```text
apksigner verify --verbose --print-certs <自己提取的APK>
aapt2 dump xmltree <自己提取的APK> --file AndroidManifest.xml
jadx -d <私有反编译目录> <自己提取的APK>
```

检查 `GetSignalInfoReceiver`、`e1.f`、`e1.g`、`f1.o`、`g1.c/e/f/j/m/n` 等调用链；本样本使用混淆短名，JADX 生成行号只作本地定位。对控制流异常的方法用 simple 模式／DEX 指令对照，不把反编译伪代码当作完美源码。

仓库的 `scripts/summarize_cache.py` 只读取 SQLite，不输出具体设备标识、坐标、应用名称、包名和记录时间。`scripts/redact_logs.py` 产生选定日志的脱敏摘录；其规则针对本次格式，换设备、Android 或 ROM 后需要重新审核输出，不能作为通用匿名化保证。

## 网络实验范围

只有一条历史合成请求，详情见 [synthetic-response.json](../data/synthetic-response.json)。HTTP 200 不是业务入库证明。仓库没有自动发送器，也没有将原始真实缓存作为测试流量发送；HTTP 正文在设备代码中的加密流程不代表已捕获／解密历史实际请求。
