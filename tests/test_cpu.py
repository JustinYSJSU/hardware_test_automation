"""test_cpu.py

Automated tests to validate the following:
- CPU model name, Number of CPU(s)
- CPU temperature is in a safe range
- CPU can withstand a 30 second stress test
- CPU is not throttling
"""
import subprocess
import re
import threading
import time

RASPBERRY_PI_CPU = {
    "model_name": "Cortex-A72",
    "cpu_count": 4
}

TEST_PC_CPU = {
    "model_name": "AMD Ryzen 7 7700X 8-Core Processor",
    "cpu_count": 16
}

CPU_TEMP_MIN = 30.0
CPU_TEMP_MAX = 85.0

PASSING_STRESS_TEST = 0

class TestCPU:

    def get_cpu_temperature(self):
        """Helper function to retrieve current CPU temperature
        """
        res = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)

        cpu_temp = re.search(r"temp=([\d.]+)'C", res.stdout)
        assert cpu_temp is not None 

        cpu_temp_value = float(cpu_temp.group(1))
        return cpu_temp_value
    
    def get_cpu_throttling(self):
        """Helper function to retrieve CPU throttling status
        """
        res = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True)
        
        throttled_status = int(res.stdout.strip().split("=")[1], 16)

        return throttled_status

    def monitor_cpu(self, stop_event, results):
        """Helper function to monitor CPU temperature and thorttling status
        during stress test
        """
        while not stop_event.is_set():
            # Collect CPU temperature
            temp = self.get_cpu_temperature()
            results["temperatures"].append(temp)

            # Collect CPU throttling status
            throttling = self.get_cpu_throttling()
            results["throttling"].append(throttling)

            time.sleep(1)

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
        """Test function to validate CPU temperature
        Use vcgencmd to retrieve CPU temperature, then validate 
        it is in a safe range (30 < x < 85 degrees C)
        """
        res = subprocess.run(["vcgencmd", "measure_temp"], capture_output=True, text=True)

        cpu_temp = re.search(r"temp=([\d.]+)'C", res.stdout)
        assert cpu_temp is not None 

        cpu_temp_value = float(cpu_temp.group(1))

        assert CPU_TEMP_MIN < cpu_temp_value < CPU_TEMP_MAX

    def test_cpu_throttling(self):
        """Test function to valdiate CPU is
        not thorttling
        """
        res = subprocess.run(["vcgencmd", "get_throttled"], capture_output=True, text=True)
        
        throttled_status = int(res.stdout.strip().split("=")[1], 16)
        
    def test_cpu_stress(self):
        """Test function to valdiate the CPU 
        can withstand and pass a 30 second stree-test
        """
        stop_event = threading.Event()

        results = {
                "temperatures": [],
                "throttling": []
        }

        monitor_thread = threading.Thread(
            target=self.monitor_cpu,
            args=(stop_event, results)
        )

        monitor_thread.start()

        try:    
            res = subprocess.run(["stress-ng", "--cpu", "4", "--timeout", "30s", "--metrics-brief"], capture_output=True, text=True)
        finally:
            stop_event.set()
            monitor_thread.join()

        assert res.returncode == PASSING_STRESS_TEST, "CPU stress test failed"
        assert max_temp < self.MAX_CPU_TEMP, "CPU temperature exceeded limit"

        print(res.stdout)