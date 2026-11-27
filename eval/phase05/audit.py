"""Read the local GGUF, verify its pinned LFS digest and record fresh hardware measurements."""
import ctypes as C
from datetime import datetime, timezone
from hashlib import file_digest
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / "eval/phase05"
REPORT = ROOT / "reports/phase05"
RAW = REPORT / "raw"
RAW.mkdir(parents=True, exist_ok=True)
EXPECTED = "8e9d04d41fd6bd47787aad7919ae8594a3d7488d4adc859f6fb00ef07416526c"
MODEL = "Qwen3.8-27B-UD-IQ3_XXS-fixed.gguf"
WEIGHT = Path(os.getenv("TP05_GGUF", str(ROOT.parent / "tp-model-001" / MODEL)))
OLLAMA = Path(shutil.which("ollama") or "ollama.exe")
BIN = OLLAMA.parent / "lib/ollama"
BACKEND = BIN / "llama-server.exe"
BASE = "http://127.0.0.1:11753"
SMALL = "http://127.0.0.1:11754"
ALIAS = "qwen38-27b-iq3xxs"
SMALL_MODEL = "qwen2.5-coder:0.5b"


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    tmp.replace(path)


def record(path, data):
    with path.open("a", encoding="utf8") as f:
        f.write(json.dumps({"at": stamp(), **data}, ensure_ascii=False) + "\n")


def hardware():
    ram = (C.c_ulonglong * 8)()
    C.cast(ram, C.POINTER(C.c_uint32))[0] = 64
    if not C.windll.kernel32.GlobalMemoryStatusEx(ram):
        raise OSError("GlobalMemoryStatusEx")
    return dict(ram_total_gib=ram[1]/2**30, ram_available_gib=ram[2]/2**30,
                ram_used_gib=(ram[1]-ram[2])/2**30, commit_available_gib=ram[4]/2**30)


class NvMemory(C.Structure):
    _fields_ = [("version",C.c_uint32), ("total",C.c_ulonglong), ("reserved",C.c_ulonglong),
                ("free",C.c_ulonglong), ("used",C.c_ulonglong)]


class Monitor:
    def __init__(self):
        self.dll = C.CDLL(str(Path(os.environ["SystemRoot"]) / "System32/nvml.dll"))
        self.handle = C.c_void_p()
        if self.dll.nvmlInit_v2() or self.dll.nvmlDeviceGetHandleByIndex_v2(0,C.byref(self.handle)):
            raise OSError("NVML init")

    def sample(self):
        mem = NvMemory(C.sizeof(NvMemory) | 2 << 24)
        if self.dll.nvmlDeviceGetMemoryInfo_v2(self.handle,C.byref(mem)):
            raise OSError("NVML sample")
        return {**hardware(), "vram_used_mib":mem.used/2**20, "vram_free_mib":mem.free/2**20}


def gguf(f):
    def unpack(fmt):
        return struct.unpack("<"+fmt, f.read(struct.calcsize("<"+fmt)))[0]
    def string():
        return f.read(unpack("Q")).decode("utf8")
    formats = {0:"B",1:"b",2:"H",3:"h",4:"I",5:"i",6:"f",7:"?",10:"Q",11:"q",12:"d"}
    def value(kind):
        if kind == 8:
            return string()
        if kind != 9:
            return unpack(formats[kind])
        dtype, length = unpack("I"), unpack("Q")
        if dtype == 8:
            for _ in range(length):
                size = unpack("Q")
                f.seek(size,1)
        else:
            f.seek(struct.calcsize("<"+formats[dtype])*length,1)
        return {"item_type":dtype, "count":length}
    if f.read(4) != b"GGUF":
        raise ValueError("GGUF magic mismatch")
    version, tensors, fields = unpack("I"), unpack("Q"), unpack("Q")
    if version != 3:
        raise ValueError("Unsupported GGUF version")
    info = {}
    for _ in range(fields):
        key = string()
        item = value(unpack("I"))
        if key.startswith(("general.", "tokenizer.ggml.", "qwen35.")):
            info[key] = item
    return {"format":"GGUF", "version":version, "tensors":tensors, "metadata":info}


def gpu_env():
    cuda = BIN / "cuda_v13"
    return dict(os.environ, GGML_BACKEND_PATH=str(cuda / "ggml-cuda.dll"),
                PATH=os.pathsep.join([str(cuda),str(BIN),os.environ["PATH"]]))


def audit():
    with WEIGHT.open("rb") as f:
        meta = gguf(f)
        f.seek(0)
        actual = file_digest(f,"sha256").hexdigest()
    devices = subprocess.run([BACKEND,"--list-devices"],env=gpu_env(),capture_output=True,errors="replace",text=True)
    info = dict(time=stamp(),file=str(WEIGHT),size=WEIGHT.stat().st_size,sha256=actual,
                expected_sha256=EXPECTED, pin="33a91d0e6fa53bf04accf398fde7b8ee1a1c9294",
                complete=actual==EXPECTED and WEIGHT.stat().st_size==10934860608,
                windows=platform.platform(), python=platform.python_version(), hardware=Monitor().sample(),
                gpu=subprocess.check_output(["nvidia-smi","--query-gpu=name,driver_version,memory.total,memory.free",
                                             "--format=csv"],text=True).strip(),
                backend=str(BACKEND),devices=(devices.stdout+devices.stderr).strip(),gguf=meta)
    save(RAW/"audit.json",info)
    print(info["complete"],actual,info["gpu"],info["hardware"],info["devices"])
    if not info["complete"]:
        raise SystemExit(2)


if __name__ == "__main__":
    audit()
