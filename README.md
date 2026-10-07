# Qqsp 简体中文语言包 / Simplified Chinese localization for Qqsp

Qqsp 播放器的简体中文汉化（**版本 1.9.0**）。

* 上游项目：[ezsh/Qqsp](https://github.com/ezsh/Qqsp)（MIT License，Copyright © 2017-2018 Sonnix）
* 本仓库提供：`tools/`（Python 汉化工具链）、`src/`（相关源码摘录）、`out/`（编译好的汉化 exe 与语言包）、`analysis/`（逆向分析脚本）
* 汉化内容：**414 条词条 / 37 个上下文** + exe 内 4 类固定字符串（51 处、434 字节）

---

## 一、下载即玩（推荐）

到 [**Releases**](https://github.com/YuFuDiao/Qqsp-zh_CN/releases) 下载 **`Qqsp-1.9.0-win64-zh_CN.rar`**，解压后双击 `Qqsp.exe` 即可，**开箱就是中文界面**，不需要另行安装 Qt 运行库。

包内已包含：

```
Qqsp-1.9.0-win64/
  Qqsp.exe            已汉化（窗口标题、菜单、选项、引擎错误提示均为中文）
  Qqsp.zh_CN.qm       简体中文语言包
  Qqsp.zh-CN.qm       连字符别名（见第五节，防界面回英文）
  Qqsp.exe.bak        原始未汉化版本，想还原时改名为 Qqsp.exe 覆盖回去即可
  Qt5*.dll / plugins/ Qt 运行库，随包提供
  vc_redist.x64.exe   Visual C++ 运行库安装程序（若提示缺少 dll 时运行）
```

## 二、只替换语言包（已有 Qqsp 1.9.0）

下载 [`out/Qqsp.exe`](out/Qqsp.exe) 与 [`out/Qqsp.zh_CN.qm`](out/Qqsp.zh_CN.qm)，覆盖到 Qqsp 1.9.0 的安装目录即可：

```
Qqsp-1.9.0-win64/
  Qqsp.exe            <- 用 out/Qqsp.exe 覆盖（建议先备份原文件）
  Qqsp.zh_CN.qm       <- 新增
  Qqsp.zh-CN.qm       <- 新增（连字符别名，见第五节）
```

已验证的 SHA256：

| 文件 | 字节 | SHA256 |
|---|---|---|
| `out/Qqsp.zh_CN.qm` | 28524 | `97bdf0e8a4663eae1bb3adcd6ad6e3f4a7c28a9fe9c224d61cc1f15beed2c6b7` |
| `out/Qqsp.zh-CN.qm` | 28524 | 同上（连字符别名，逐字节相同） |
| `out/Qqsp.exe` | 666624 | `390ce5d37ac793e10d43d70c6cad037a8e7587be7889dc95a64974e16cf7eb18` |
| 原始 `Qqsp.exe`（1.9.0 未汉化） | 666624 | `7ad434c3034a1e0284871ad5991c1d747c0cbdd3c22d53201d2cacc539567e38` |

还原：用你备份的原版 `Qqsp.exe` 覆盖回去，并删掉两个 `.qm` 即可。

## 三、仓库结构

```
out/            编译产物
  Qqsp.exe          已汉化的播放器（仅 51 处、434 字节与原版不同，代码逻辑未改）
  Qqsp.zh_CN.qm     简体中文语言包
  Qqsp.zh-CN.qm     连字符别名（逐字节相同）
  Qqsp.zh_CN.ts     Qt Linguist 源文件，改词条改这个
tools/          汉化工具链（纯 Python，不需要安装 Qt）
  qm.py             .qm 读写库，输出与官方 lrelease 逐字节一致
  mk_zh.py          从 src/Qqsp.ru.qm 生成 Qqsp.zh_CN.qm（含 Qt 标准对话框词条）
  ts2qm.py          .ts -> .qm 编译器
  patch_exe2.py     从原始 exe 生成汉化 exe（幂等、带完整性校验）
  qpe.py            PE 解析 + 反汇编辅助（需要 capstone）
  patch_exe.py      早期版本的 exe 补丁（保留作对比）
  其余             cmp_qm / dump_msgs / gen_ts / qllocale / qtprobe / sweep / verify_patch / trscan
src/            源码摘录
  Qqsp.pro          上游工程文件（说明文件来源与结构）
  main.cpp 等       Qt 侧源码，用于核对 tr() 调用点
  Qqsp.en.ts / Qqsp.ru.ts / Qqsp.ru.qm   上游词条集
  qt_zh_CN.ts       Qt 官方简中词条（用于合并标准对话框翻译）
analysis/       逆向分析脚本与输出（反汇编、路径扫描等），仅供追溯
original/       放置原始 Qqsp.exe 的位置（存放的是 1.9.0 未汉化版本）
docs/           详细说明
```

## 四、重新打包

### 改词条后重新生成语言包

```powershell
python tools\mk_zh.py          # 从 src\Qqsp.ru.qm + Qt 词条生成 out\Qqsp.zh_CN.qm（414 条）
```

`mk_zh.py` 自带回环校验（写完重新解析比对），当前输出与仓库内那份**逐字节相同**。

### 从原始 exe 重新生成汉化 exe

需要 [capstone](https://pypi.org/project/capstone/)（`pip install capstone`）：

```powershell
$env:PYTHONPATH = '<capstone 所在目录>'      # 或 pip install capstone
python tools\patch_exe2.py
```

脚本默认从 `original\Qqsp.exe` 读取原始版本，输出到 `out\Qqsp.exe`。可用环境变量覆盖：

| 变量 | 含义 |
|---|---|
| `QQSP_EXE` | 原始 `Qqsp.exe` 的完整路径 |
| `QQSP_BAK` | 同上（供 `sweep.py` / `verify_patch.py` 使用） |
| `QQSP_OUT` | 输出 exe 路径 |

**可复现性已验证**：以 SHA256 为 `7ad434c3…` 的原始 exe 为输入，本工具链输出 SHA256 `390ce5d3…`，与仓库内 `out/Qqsp.exe` **逐字节一致**。

## 五、为什么要那个连字符别名 `Qqsp.zh-CN.qm`

Qqsp 按 `Qqsp.<language 的值>.qm` 查找语言包，而 `language` 默认取 `QLocale::system().name()`。在中文 Windows 上这个值是 **`zh-CN`（连字符）**，但语言包文件叫 **`zh_CN`（下划线）**——差一个字符，`QTranslator::load()` 又不会把连字符换成下划线，于是找不到语言包、界面全英文。

更麻烦的是：按游戏目录保存的 `qqsp.ini` 会在打开游戏时覆盖内存里的语言 ID，关闭时再写回全局配置，所以一个坏值会自我保留并扩散。

放一份逐字节相同的 `Qqsp.zh-CN.qm` 后，`zh-CN` 与 `zh_CN` 都能命中，配置再被写坏也不会掉回英文。副作用是「设置 → 选项 → 语言」下拉框会多出一条同名的「简体中文」（两条的 data 都是 `zh_CN`，选哪条都对）。

## 六、已知未汉化项

* **游戏剧情文本**——在 `.qsp` 文件内部，与本播放器无关；
* Oniguruma 正则库内部错误串、`std::exception`（如 `bad allocation`）——仅在致命错误时出现，属程序内部诊断信息；
* WebEngine 右键菜单——上游用 `setContextMenuPolicy(Qt::NoContextMenu)` 主动关闭，不存在该菜单。

## 七、许可

* 本仓库的汉化内容（语言包、补丁脚本、文档）以 **MIT** 发布，见 [LICENSE](LICENSE)。
* 上游 Qqsp 同为 **MIT License, Copyright © 2017-2018 Sonnix**，原文见 [LICENSE-QQSP](LICENSE-QQSP)。
* `out/Qqsp.exe` 是原版 exe 的补丁版本，属于上游作品的衍生分发，保留 Sonnix 的版权声明。
* 上游源码、`.ts`/`.qm` 词条集与 `src/` 下的源码摘录版权归 Sonnix 及 Qqsp 贡献者所有。
