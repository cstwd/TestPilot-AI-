"""Sample admission headroom for the Windows 27B deployment."""
import ctypes
import os
from pathlib import Path

MIN_PHYSICAL_GIB = 2.0
MIN_COMMIT_GIB = 2.0
MIN_GPU_MIB = 512


class VideoMemory(ctypes.Structure):
    _fields_ = [("version", ctypes.c_uint32), ("total", ctypes.c_ulonglong),
                ("reserved", ctypes.c_ulonglong), ("free", ctypes.c_ulonglong),
                ("used", ctypes.c_ulonglong)]


class Resources:
    def __init__(self):
        self.nvml = ctypes.CDLL(str(Path(os.environ["SystemRoot"]) / "System32" / "nvml.dll"))
        self.device = ctypes.c_void_p()
        if self.nvml.nvmlInit_v2() or self.nvml.nvmlDeviceGetHandleByIndex_v2(0, ctypes.byref(self.device)):
            raise OSError("NVML 无法初始化")
        self.last_cpu = None

    def sample(self):
        fields = (ctypes.c_ulonglong * 8)()
        ctypes.cast(fields, ctypes.POINTER(ctypes.c_uint32))[0] = 64
        memory = VideoMemory(ctypes.sizeof(VideoMemory) | (2 << 24))
        if (not ctypes.windll.kernel32.GlobalMemoryStatusEx(fields) or
                self.nvml.nvmlDeviceGetMemoryInfo_v2(self.device, ctypes.byref(memory))):
            raise OSError("硬件资源采样失败")
        idle,kernel,user = (ctypes.c_ulonglong() for _ in range(3))
        cpu_pct = None
        if ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle),ctypes.byref(kernel),ctypes.byref(user)):
            cpu = (idle.value, kernel.value+user.value)
            if self.last_cpu and cpu[1]>self.last_cpu[1]:
                cpu_pct = 100*(1-(cpu[0]-self.last_cpu[0])/(cpu[1]-self.last_cpu[1]))
            self.last_cpu = cpu
        return {"physical_total_gib": fields[1]/2**30, "physical_free_gib": fields[2]/2**30,
                "physical_used_gib": (fields[1]-fields[2])/2**30,
                "commit_limit_gib": fields[3]/2**30, "commit_free_gib": fields[4]/2**30,
                "commit_used_gib": (fields[3]-fields[4])/2**30,
                "gpu_used_mib": memory.used/2**20, "gpu_free_mib": memory.free/2**20,"cpu_pct":cpu_pct}


def headroom(sample):
    return (sample["physical_free_gib"] >= MIN_PHYSICAL_GIB
            and sample["commit_free_gib"] >= MIN_COMMIT_GIB
            and sample["gpu_free_mib"] >= MIN_GPU_MIB)
