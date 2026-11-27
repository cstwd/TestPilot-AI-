# 本机评测复现

从实验工作树根目录运行。使用主仓库的项目解释器，已有 Wasmtime 编译缓存可复制到实验工作树的 `.runtime/wasm-cache`。每次新实验建议使用新工作树或新的原始数据目录。程序通过每轮文件恢复已完成的作业。将存量权重路径设置为 `TP05_GGUF`，缺省指向同一运行目录下历史下载的本地文件，并核对固定 SHA-256。安装已有 Ollama 服务和 NVIDIA Vulkan 设备选择遵循 `raw/vulkan-01/launch.json`。根目录的项目解释器示例依相对位置自行调整。

用预登记清单核对样例与算子。

```powershell
$py = '..\..\.venv\Scripts\python.exe'
& $py -m eval.phase05.audit
& $py -m pytest tests/test_mutation_generator.py eval/phase05/test_manifest.py -q
& $py -m eval.phase05.measure reference
```

通过两个专用终端启动本地服务。模型健康通过并保存连续推理后，27B 使用端口 11753。A 组访问 11754 上的本地现存小模型。

```powershell
& $py -m eval.phase05.runtime --attempt vulkan-01 --vulkan
& $py -m eval.phase05.runtime --attempt small-01 --small-only
```

运行评测。单独的反馈进程等待 C 组写下实际变异结果。它与 C 组测量可同时运行。A 和 B 组在任何需要时独立运行。控制同时运行的 WASI 作业数以适应 Windows 可用内存。

```powershell
& $py -m eval.phase05.understand
& $py -m eval.phase05.generate A
& $py -m eval.phase05.generate C
& $py -m eval.phase05.measure A
& $py -m eval.phase05.measure B --workers 2
& $py -m eval.phase05.measure C
& $py -m eval.phase05.feedback
& $py -m eval.phase05.measure D --workers 2
```

结束时在对应服务队列目录创建 `STOP`，监督器仅关闭该实验启动的进程。汇总包括全清单一致性、源码摘要、测试摘要和杀死原因的重算。

```powershell
& $py -m eval.phase05.overview
& $py -m eval.phase05.aggregate
& $py -m eval.phase05.report
& 'E:\Miniconda3\envs\dap\python.exe' -m eval.phase05.chart
```

图表环境使用现成的 Matplotlib 3.10.9，主项目依赖不需要额外安装绘图库。脚本会生成 PNG 和 SVG。
