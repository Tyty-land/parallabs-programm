import numpy as np
import subprocess
import os
import sys
import matplotlib.pyplot as plt

def run_benchmark():
    sizes = [200, 400, 800, 1200, 1600, 2000]
    threads_list = [1, 2, 4, 8]
    
    results = {t: [] for t in threads_list}

    fileA = "temp_A.txt"
    fileB = "temp_B.txt"
    fileC = "temp_C.txt"

    exe_name = "main.exe" if sys.platform == "win32" else "./main"
    exe_path = os.path.join(os.path.dirname(__file__), "..", exe_name)

    if not os.path.exists(exe_path):
        print(f"Ошибка: исполняемый файл {exe_path} не найден.")
        return

    
    for N in sizes:
        print(f"\nГенерация матриц для размера {N}x{N}...")
        A = np.random.rand(N, N).astype(np.float64)
        B = np.random.rand(N, N).astype(np.float64)
        np.savetxt(fileA, A, fmt='%f')
        np.savetxt(fileB, B, fmt='%f')

        for T in threads_list:
            print(f"  Тестирование на {T} потоках...", end="", flush=True)
            try:
                result = subprocess.run(
                    [exe_path, str(N), str(T), fileA, fileB, fileC],
                    capture_output=True, text=True, check=True
                )
                cpp_time = float(result.stdout.strip())
                results[T].append(cpp_time)
                print(f" Успешно: {cpp_time:.2f} мс")
            except Exception as e:
                print(f" ошибка.")
                print(e)
                return

    for f in [fileA, fileB, fileC]:
        if os.path.exists(f):
            os.remove(f)

    print("="*70)
    
    header = "| Размер матрицы | 1 поток (мс) | 2 потока (мс) | 4 потока (мс) | 8 потоков (мс) |"
    separator = "|----------------|--------------|---------------|---------------|----------------|"
    print(header)
    print(separator)
    
    for i, N in enumerate(sizes):
        row = f"| {N} x {N:<10} |"
        for T in threads_list:
            row += f" {results[T][i]:<12.2f} |"
        print(row)
    print("="*70 + "\n")

    plt.figure(figsize=(10, 6))
    colors = {1: 'red', 2: 'orange', 4: 'green', 8: 'blue'}
    markers = {1: 'o', 2: '^', 4: 's', 8: 'D'}

    for T in threads_list:
        plt.plot(sizes, results[T], marker=markers[T], color=colors[T], 
                 linestyle='-', linewidth=2, label=f'{T} потоков')

    plt.title('Зависимость времени выполнения от размера матрицы и числа потоков OpenMP')
    plt.xlabel('Размер матрицы (N x N)')
    plt.ylabel('Время выполнения (мс)')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    
    plot_path = os.path.join(os.path.dirname(__file__), "..", "performance_plot.png")
    plt.savefig(plot_path, dpi=150)
    print(f"График успешно сохранен: {plot_path}")

if __name__ == "__main__":
    run_benchmark()