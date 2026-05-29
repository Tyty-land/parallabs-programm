import numpy as np
import subprocess
import os
import sys
import matplotlib.pyplot as plt

def run_benchmark():
    sizes = [200, 400, 600, 800, 1000, 1200, 1500, 2000]
    times = []

    fileA = "temp_A.txt"
    fileB = "temp_B.txt"
    fileC = "temp_C.txt"

    exe_name = "main.exe" if sys.platform == "win32" else "./main"
    exe_path = os.path.join(os.path.dirname(__file__), "..", exe_name)

    if not os.path.exists(exe_path):
        print(f"Ошибка: исполняемый файл {exe_path} не найден.")
        return

    print("Начало тестирования...")
    
    for N in sizes:
        print(f"Тестирование размера {N}x{N}...", end="", flush=True)
        
        A = np.random.rand(N, N).astype(np.float64)
        B = np.random.rand(N, N).astype(np.float64)
        np.savetxt(fileA, A, fmt='%f')
        np.savetxt(fileB, B, fmt='%f')

        try:
            result = subprocess.run(
                [exe_path, str(N), fileA, fileB, fileC],
                capture_output=True, text=True, check=True
            )
            cpp_time = float(result.stdout.strip())
            times.append(cpp_time)
            print(f" успешно. Время: {cpp_time:.2f} мс")
        except Exception as e:
            print(f" ошибка")
            print(e)
            return

    for f in [fileA, fileB, fileC]:
        if os.path.exists(f):
            os.remove(f)

    # Markdown таблица
    print("="*40)
    print("| Размер матрицы (N x N) | Время C++ (мс) |")
    print("|------------------------|----------------|")
    for N, t in zip(sizes, times):
        print(f"| {N} x {N:<14} | {t:<14.2f} |")
    print("="*40 + "\n")

    # Построение графика 
    plt.figure(figsize=(10, 6))
    
    plt.plot(sizes, times, 'o-', color='blue', label='фактическое время')
    
    scale_factor = times[-1] / (sizes[-1]**3) * 4.0
    theoretical_times = [scale_factor * (N**3) for N in sizes]
    plt.plot(sizes, theoretical_times, '--', color='red', label='теоретическая сложность O(n^3)')

    plt.title('зависимость времени выполнения от размера матрицы')
    plt.xlabel('размер матрицы (N x N)')
    plt.ylabel('время (мс)')
    plt.grid(True)
    plt.legend()
    
    plot_path = os.path.join(os.path.dirname(__file__), "..", "performance_plot.png")
    plt.savefig(plot_path, dpi=150)
    print(f"График успешно сохранен: {plot_path}")

if __name__ == "__main__":
    run_benchmark()