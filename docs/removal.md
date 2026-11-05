# 三种卸载入口与恢复

**本次分析机型为 realme GT5 Pro（RMX3888）。** 用户反馈已 root 卸载并正常重启；未提供逐项通信测试结果，也未独立核验其采用的卸载机制。

以下三种入口都使用包管理器做 **用户 0 卸载**。root 只改变命令执行身份，不会自动把 `pm uninstall --user 0` 变成系统分区 APK 的物理删除。系统原包仍在时可以 install-existing；如果原包已被物理删除或被模块隐藏，需要先恢复原包可见性。

## 1. 无 root，PC ADB 卸载

在电脑终端执行：

```powershell
adb shell pm uninstall --user 0 com.mobiletools.systemhelper
```

恢复：

```powershell
adb shell cmd package install-existing --user 0 com.mobiletools.systemhelper
adb shell pm default-state --user 0 com.mobiletools.systemhelper
```

## 2. 有 root，ADB su 卸载

本机验证可用的 APatch su 入口为 env /system/bin/su。下列卸载命令没有由 Codex 对该手机执行：

```powershell
adb shell env /system/bin/su --no-pty -c 'pm uninstall --user 0 com.mobiletools.systemhelper'
```

恢复：

```powershell
adb shell env /system/bin/su --no-pty -c 'cmd package install-existing --user 0 com.mobiletools.systemhelper'
adb shell env /system/bin/su --no-pty -c 'pm default-state --user 0 com.mobiletools.systemhelper'
```

其它 root 实现中，如果 `su -c` 本身可用，也可通过它执行同样的 pm 命令；不应照搬本机 APatch 专有参数。

## 3. 有 root，Android terminal（例如 Termux）卸载

在手机终端中执行，并在 root 管理器中按自己的意愿授权该终端：

```sh
su -c 'pm uninstall --user 0 com.mobiletools.systemhelper'
```

恢复：

```sh
su -c 'cmd package install-existing --user 0 com.mobiletools.systemhelper'
su -c 'pm default-state --user 0 com.mobiletools.systemhelper'
```

本机 APatch 如果终端中普通 su 不可用，可按其实际配置尝试：

```sh
env /system/bin/su --no-pty -c 'pm uninstall --user 0 com.mobiletools.systemhelper'
```

该备用入口已在本机 ADB shell 获得 root，不等于已在每个 Android 终端应用中实测。

## 数据、验证与范围

- 返回 `Success` 表示包管理器报告操作成功；检查用户 0 的安装状态。`pm list packages -u` 可包含已对用户卸载的系统包，不能仅凭该列表仍有包名判断失败。
- 未加 `-k` 的卸载通常会清除该用户应用数据；加 `-k` 表示保留数据与缓存，不代表清除了待上报队列。恢复安装状态不保证恢复已删数据。
- 如希望先观察，可用 `pm disable-user --user 0 com.mobiletools.systemhelper`；恢复用 `pm default-state --user 0 com.mobiletools.systemhelper`。在 PC 中前置 `adb shell`，需要 root 时用对应 su 入口。
- 测试开机、双卡呼入／呼出、短信收发、移动数据、5G、VoLTE、Wi-Fi；其它用户、工作资料、运营商激活和后续 OTA 另行验证。
- 本次用户“重启正常”的反馈只支持本机当次启动结果，不保证所有通信功能或其它机型、ROM。
- 不建议为阻止采集直接改写／删除只读系统分区；若采用 systemless 模块，恢复应先禁用／移除模块再重启。此仓库不附带待测试模块或第三方安装器。

依据：[Android 包管理命令实现](https://android.googlesource.com/platform/frameworks/base/+/android11-release/services/core/java/com/android/server/pm/PackageManagerShellCommand.java)、[APatch 模块机制](https://apatch.dev/apm-guide.html)。
