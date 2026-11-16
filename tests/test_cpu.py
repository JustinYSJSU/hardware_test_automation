"""test_cpu.py

Automated tests to validate the following:
- CPU model name
- Number of CPU(s)
- CPU temperature is in a safe range
- CPU can withstand a 30 second stress test
- CPU is not throttling
"""
import subprocess
import re

RASPBERRY_PI_CPU = {
    "model_name": "Cortex-A72",
    "cpu_count": 4
}

TEST_PC_CPU = {
    "model_name": "AMD Ryzen 7 7700X 8-Core Processor",
    "cpu_count": 16
}

class TestCPU:

    def test_cpu_model_name_and_count(self):
        """Test function to validate CPU model name
        CPU model name is based off of Raspberry PI v4 (while testing on WSL, it may instead match the CPU of the PC)
        """
        res = subprocess.run(["lscpu"], capture_output=True, text=True)
        cpu_info = {}

        for line in res.stdout.splitlines():
            if ":" not in line:
                continue

            key, value = line.split(":", 1)

            key = key.strip().lower()
            key = re.sub(r"\(s\)", "_count", key)
            key = re.sub(r"[^a-z0-9]+", "_", key)
            key = key.strip("_")

            cpu_info[key] = value.strip()
        cpu_model_name = cpu_info["model_name"]
        cpu_count = int(cpu_info["cpu_count"])
        assert cpu_model_name == RASPBERRY_PI_CPU["model_name"] and cpu_count == RASPBERRY_PI_CPU["cpu_count"]

    def test_cpu_temperature(self):
        res = subprocess.run(["vcgencmd measure_temp"], capture_output=True, text=True)
        print(res)