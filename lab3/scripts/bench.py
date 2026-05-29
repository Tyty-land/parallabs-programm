import numpy as np
import subprocess
import os
import sys
import matplotlib.pyplot as plt

def run_benchmark():
    sizes = [200, 400, 800, 1200, 1600, 2000]
    procs_list = [1, 2, 4, 8]
    
    results = {p: [] for p in procs_list}

    fileA = "temp_A.txt"
    fileB = "temp_B.txt"
    fileC = "temp_C.txt"

    exe_name = "main.exe" if sys.platform == "win32" else "./main"
    exe_path = os.path.join(os.path.dirname(__file__), "..", exe_name)

    if not os.path.exists(exe_path):
        print(f"Ошибка: исполняемый файл {exe_path} не найден.")
        return

    mpiexec_cmd = "mpiexec"
    if sys.platform == "win32":
        default_msmpi_path = r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
        if os.path.exists(default_msmpi_path):
            mpiexec_cmd = default_msmpi_path

    
    for N in sizes:
        print(f"\nГенерация матриц для размера {N}x{N}...")
        A = np.random.rand(N, N).astype(np.float64)
        B = np.random.rand(N, N).astype(np.float64)
        np.savetxt(fileA, A, fmt='%f')
        np.savetxt(fileB, B, fmt='%f')

        for P in procs_list:
            print(f"  Тестирование на {P} процессах...", end="", flush=True)
            try:
                result = subprocess.run(
                    [mpiexec_cmd, "-n", str(P), exe_path, str(N), fileA, fileB, fileC],
                    capture_output=True, text=True, check=True
                )
                cpp_time = float(result.stdout.strip())
                results[P].append(cpp_time)
                print(f" Успешно: {cpp_time:.2f} мс")
            except Exception as e:
                print(f" ошибка.")
                print(e)
                return

    for f in [fileA, fileB, fileC]:
        if os.path.exists(f):
            os.remove(f)

    print("="*70)
    
    header = "| Размер матрицы | 1 процесс (мс) | 2 процесса (мс) | 4 процесса (мс) | 8 процессов (мс) |"
    separator = "|----------------|----------------|-----------------|-----------------|------------------|"
    print(header)
    print(separator)
    
    for i, N in enumerate(sizes):
        row = f"| {N} x {N:<10} |"
        for P in procs_list:
            row += f" {results[P][i]:<14.2f} |"
        print(row)
    print("="*70 + "\n")

    plt.figure(figsize=(10, 6))
    colors = {1: 'red', 2: 'orange', 4: 'green', 8: 'blue'}
    markers = {1: 'o', 2: '^', 4: 's', 8: 'D'}

    for P in procs_list:
        plt.plot(sizes, results[P], marker=markers[P], color=colors[P], 
                 linestyle='-', linewidth=2, label=f'{P} процессов MPI')

    plt.title('Зависимость времени выполнения от размера матрицы и числа процессов MPI')
    plt.xlabel('Размер матрицы (N x N)')
    plt.ylabel('Время выполнения (мс)')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    
    plot_path = os.path.join(os.path.dirname(__file__), "..", "performance_plot.png")
    plt.savefig(plot_path, dpi=150)
    print(f"График успешно сохранен: {plot_path}")

if __name__ == "__main__":
    run_benchmark()