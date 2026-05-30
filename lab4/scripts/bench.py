import numpy as np
import subprocess
import os
import sys
import matplotlib.pyplot as plt

def run_benchmark():
    sizes = [200, 400, 800, 1200, 1600, 2000]
    block_sizes = [8, 16, 32] # Блоки: 8x8, 16x16, 32x32 потоков
    
    results = {b: [] for b in block_sizes}

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

        for B_size in block_sizes:
            print(f"  Тестирование с блоком {B_size}x{B_size}...", end="", flush=True)
            try:
                result = subprocess.run(
                    [exe_path, str(N), str(B_size), fileA, fileB, fileC],
                    capture_output=True, text=True, check=True
                )
                gpu_time = float(result.stdout.strip())
                results[B_size].append(gpu_time)
                print(f" Успешно: {gpu_time:.2f} мс")
            except Exception as e:
                print(f" ошибка.")
                print(e)
                return

    for f in [fileA, fileB, fileC]:
        if os.path.exists(f):
            os.remove(f)

    print("="*80)
    print("| Размер матрицы | Блок 8x8 (мс) | Блок 16x16 (мс) | Блок 32x32 (мс) |")
    print("|----------------|---------------|-----------------|-----------------|")
    for i, N in enumerate(sizes):
        print(f"| {N} x {N:<10} | {results[8][i]:<13.2f} | {results[16][i]:<15.2f} | {results[32][i]:<15.2f} |")
    print("="*80 + "\\n")

    plt.figure(figsize=(10, 6))
    colors = {8: 'red', 16: 'green', 32: 'blue'}
    markers = {8: 'o', 16: 's', 32: 'D'}

    for B_size in block_sizes:
        plt.plot(sizes, results[B_size], marker=markers[B_size], color=colors[B_size], 
                 linestyle='-', linewidth=2, label=f'Блок {B_size}x{B_size} потоков')

    plt.title('Зависимость времени выполнения от размера матрицы и конфигурации блока CUDA')
    plt.xlabel('Размер матрицы (N x N)')
    plt.ylabel('Время выполнения на GPU (мс)')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    
    plot_path = os.path.join(os.path.dirname(__file__), "..", "performance_plot.png")
    plt.savefig(plot_path, dpi=150)
    print(f"График успешно сохранен: {plot_path}")

if __name__ == "__main__":
    run_benchmark()