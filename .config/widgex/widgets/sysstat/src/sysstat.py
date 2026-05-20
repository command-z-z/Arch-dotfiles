#!/usr/bin/env python3
import json, subprocess, psutil

# CPU
cpu_pct = psutil.cpu_percent(interval=0.5)
freq = psutil.cpu_freq()
cpu_freq_str = f"{freq.current / 1000:.1f} GHz" if freq else "—"

cpu_temp_str = "—"
try:
    temps = psutil.sensors_temperatures()
    pkg = [t for t in temps.get("coretemp", []) if "Package" in t.label]
    if pkg:
        cpu_temp_str = f"{pkg[0].current:.0f}°C"
except Exception:
    pass

# GPU (NVIDIA)
gpu_pct = 0.0
gpu_mem_str = "—"
gpu_temp_str = "—"
try:
    r = subprocess.run(
        ["nvidia-smi",
         "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
         "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=3
    )
    if r.returncode == 0:
        p = [x.strip() for x in r.stdout.strip().split(",")]
        gpu_pct = float(p[0])
        used_gb = float(p[1]) / 1024
        total_gb = float(p[2]) / 1024
        gpu_mem_str = f"{used_gb:.1f}/{total_gb:.0f} GB"
        gpu_temp_str = f"{p[3]}°C"
except Exception:
    pass

# Memory
mem = psutil.virtual_memory()

# Disk
disk = psutil.disk_usage("/")

print(json.dumps({
    "cpu_pct":    f"{cpu_pct:.1f}",
    "cpu_detail": f"{cpu_freq_str}  ·  {cpu_temp_str}",
    "gpu_pct":    f"{gpu_pct:.1f}",
    "gpu_detail": f"{gpu_mem_str}  ·  {gpu_temp_str}",
    "mem_pct":    f"{mem.percent:.1f}",
    "mem_detail": f"{mem.used/1024**3:.1f} / {mem.total/1024**3:.1f} GB",
    "disk_pct":   f"{disk.percent:.1f}",
    "disk_detail":f"{disk.used/1024**3:.1f} / {disk.total/1024**3:.1f} GB",
}))
