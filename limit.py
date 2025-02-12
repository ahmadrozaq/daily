import os
import psutil
import time
import multiprocessing
import daemon

def limit_cpu_usage(pid: int, max_cpu_percent: float, interval: float = 1.0):
    """
    Membatasi penggunaan CPU dari proses tertentu.
    
    :param pid: Process ID yang ingin dibatasi
    :param max_cpu_percent: Batas maksimum penggunaan CPU dalam persen
    :param interval: Interval waktu untuk mengecek dan mengatur CPU usage
    """
    process = psutil.Process(pid)
    
    while True:
        cpu_usage = process.cpu_percent(interval=interval)
        if cpu_usage > max_cpu_percent:
            time.sleep(interval * (cpu_usage / max_cpu_percent - 1))

def limit_cpu_cores(pid: int, max_cores: int):
    """
    Membatasi jumlah core CPU yang digunakan oleh proses tertentu.
    
    :param pid: Process ID yang ingin dibatasi
    :param max_cores: Jumlah maksimum core yang bisa digunakan
    """
    process = psutil.Process(pid)
    available_cores = list(range(multiprocessing.cpu_count()))[:max_cores]
    process.cpu_affinity(available_cores)
    print(f"PID {pid} dibatasi menggunakan core: {available_cores}")

def run_as_service():
    """
    Menjalankan pembatasan CPU sebagai background service.
    """
    max_cpu_percent = 80  # Batas penggunaan CPU dalam persen
    max_cores = 54  # Batas jumlah core yang bisa digunakan
    pid = next(p.info['pid'] for p in psutil.process_iter(attrs=['name']) if p.info['name'] == 'backup_daily')  # Ambil PID dari proses saat ini
    
    print(f"Membatasi penggunaan CPU menjadi {max_cpu_percent}% untuk PID {pid}")
    print(f"Membatasi jumlah core menjadi {max_cores} untuk PID {pid}")
    
    limit_cpu_cores(pid, max_cores)
    limit_cpu_usage(pid, max_cpu_percent)

if __name__ == "__main__":
    with daemon.DaemonContext():
        run_as_service()
