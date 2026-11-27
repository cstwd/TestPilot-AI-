"""Render T01/T02 from captured data, keeping system load and model correctness distinct."""
import json
from statistics import mean,median
from .audit import RAW, REPORT
from .corpus import SPEC

def data(p):
    return json.loads(p.read_bytes())

def rows(p):
    return [json.loads(line) for line in p.read_bytes().splitlines() if line.strip()]

def write(name,lines):
    (REPORT/name).write_text("\n".join(lines)+"\n",encoding="utf8")

def main():
    meta=data(RAW/"audit.json")
    g=meta["gguf"]
    m=g["metadata"]
    h=meta["hardware"]
    vk=RAW/"vulkan-01"
    live=rows(vk/"stability.jsonl")
    peak=[r for r in rows(vk/"memory.jsonl") if r["at"]<=live[-1]["at"]]
    cuda=[r for r in rows((RAW/"native-01")/"memory.jsonl")]
    w=lambda x: f"{x:.2f}"
    write("T01_ENVIRONMENT.md",["# T01 模型文件和本地环境","",
        f"实验工作树基于 307d4bd。校验时间 {meta['time']}，读取本地文件 `{meta['file']}`，大小 {meta['size']:,} 字节。",
        f"SHA-256 为 `{meta['sha256']}`。与发布修订 `{meta['pin']}` 的 LFS 摘要和长度一致。本阶段使用已有权重。",
        "[原始逐字节校验与 GGUF 元数据](raw/audit.json) · [固定发布文件](https://huggingface.co/Jfish123/Qwen3.8-27B-16GB-GGUF/tree/33a91d0e6fa53bf04accf398fde7b8ee1a1c9294)","",
        "| 项目 | 实查值 |","| --- | --- |",
        f"| 文件与量化 | GGUF v{g['version']}，{g['tensors']} 个张量，文件类型码 {m['general.file_type']}（IQ3_XXS），发布文件标记 UD，量化作者 {m.get('general.quantized_by')} |",
        f"| 名称与架构 | {m['general.name']}，架构字段 `{m['general.architecture']}`，GGUF 中 {m['qwen35.block_count']} 个块；后端日志记录未用于本轮普通解码的预测头张量 |",
        f"| Tokenizer | {m['tokenizer.ggml.model']}，预分词器 {m['tokenizer.ggml.pre']}，词表 {m['tokenizer.ggml.tokens']['count']:,} |",
        f"| 环境 | {meta['windows']}，Python {meta['python']} |",f"| GPU／驱动 | {meta['gpu'].splitlines()[-1]} |",
        f"| 物理内存 | {h['ram_total_gib']:.2f} GiB，审计时可用 {h['ram_available_gib']:.2f} GiB，提交余量 {h['commit_available_gib']:.2f} GiB |","",
        "旧 Ollama 加载日志显示 CUDA_Host 缓冲区分配失败。本轮直接使用已安装的 llama-server，通过内存映射及全层卸载成功加载相同文件。CUDA 在首个请求中遇到 PTX JIT 内存分配错误，未取得有效输出。改为显式选择 Vulkan1（RTX 5080 Laptop）后，连续推理成功。实验参数、stderr 与失败数据同时保留。未更改驱动、分页文件或系统配置。",
        "[后端版本](raw/backend-version.txt) · [设备清单](raw/vulkan-devices.txt) · [CUDA 实测](raw/native-01/server.log) · [Vulkan 启动参数](raw/vulkan-01/launch.json) · [本机服务使用说明](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)"])
    ok=[r for r in live if r['success']]
    rates=[r["timings"]["predicted_per_second"] for r in ok]
    sample=data(vk/"ready.json")
    write("T01_PERFORMANCE.md",["# T01 本机推理性能","",
       f"使用 Vulkan1、8192 token 上下文、一个推理槽。进程启动到健康检查通过 {sample['load_wall_s']:.3f} 秒。GGUF 已做全文件校验，操作系统文件缓存可能已热。关闭空请求预热，因此第一次流式调用计入首次着色器和提示处理的成本。",
       f"连续完整响应 {len(ok)}/{len(live)}，算术内容正确 {sum(r.get('correct',False) for r in live)}/{len(live)}。稳定性得分 {100*len(ok)/10:.1f}/100。首轮可见 token 延迟 {ok[0]['ttft_visible_s']:.3f} 秒，后九轮中位数 {median(r['ttft_visible_s'] for r in ok[1:]):.3f} 秒。十轮后端报告的输出速度算术均值 {mean(rates):.2f} token/s，后九轮均值 {mean(rates[1:]):.2f} token/s。",
       f"从启动前到第十条响应结束，以 0.5 秒间隔采样。显存峰值 {max(r['vram_used_mib'] for r in peak):.1f} MiB，整机物理内存峰值 {max(r['ram_used_gib'] for r in peak):.2f} GiB。显存为 NVML 整卡已用量，内存为整机占用。CUDA 失败尝试单独采得显存峰值 {max(r['vram_used_mib'] for r in cuda):.1f} MiB、整机物理内存峰值 {max(r['ram_used_gib'] for r in cuda):.2f} GiB。","",
       "| 轮次 | 可见首 token 秒 | 输出 token | 后端 token/s | 总秒数 | 完整 / 正确 |","| ---: | ---: | ---: | ---: | ---: | --- |",
       *[f"| {r['round']} | {r['ttft_visible_s']:.3f} | {r['usage']['completion_tokens']} | {r['timings']['predicted_per_second']:.2f} | {r['wall_s']:.3f} | {r['success']} / {r['correct']} |" for r in ok],"",
       "[逐请求提示、流式原文与计时](raw/vulkan-01/stability.jsonl) · [逐采样内存数据](raw/vulkan-01/memory.jsonl) · [就绪记录](raw/vulkan-01/ready.json)"])
    results=[data(RAW/"understanding"/(name+".json")) for name in SPEC]
    keys=list(results[0]["scores"])
    totals=[sum(r["scores"][k] for r in results) for k in keys]
    write("T02_SOURCE_UNDERSTANDING.md",["# T02 源码理解","",
       f"十个项目、七项逐字段评分，实得 {sum(totals)}/70（{100*sum(totals)/70:.2f}%）。四个项目含两个真实 Python 文件。模型只接收带行号源码及问题。预登记答案、完整模型输出和 WASI 对行为参考值的核验分别可查。","",
       "| 项目 | 函数 | 参数 | 实际返回 | 分支 | 边界 | 异常 | 缺陷位置 | 总分 |",
       "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
       *[f"| [{r['name']}](raw/understanding/{r['name']}.json) | "+" | ".join(str(r["scores"][k]) for k in keys)+f" | {sum(r['scores'].values())}/7 |" for r in results],
       "| 合计 | "+" | ".join(str(i) for i in totals)+f" | {sum(totals)}/70 |","",
       "人工复核发现，十个参数答案都采用带字段名的对象；其名称、类型和默认值表达正确，但与指定的三元素数组格式不同，依照冻结规则该项均计 0。分页样例将边界输入返回值写为契约期望的 1，源码实测为 2；空列表回退样例将 None 输入判断为 TypeError，实际走回退分支。税率和每页数量常量曾被报告为函数。定位项包含四处文档冲突和六个无冲突样例。","",
       "[冻结题集与规则](../../eval/phase05/frozen.json) · [十个实际行为参考作业](raw/references) · [评测程序](../../eval/phase05/understand.py)"])

if __name__=="__main__":
    main()
