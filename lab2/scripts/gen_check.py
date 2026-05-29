import numpy as np
import subprocess
import os
import sys

def run_verification(N=400, threads=4):    
    fileA = "temp_A.txt"
    fileB = "temp_B.txt"
    fileC = "temp_C.txt"
    
    exe_name = "main.exe" if sys.platform == "win32" else "./main"
    exe_path = os.path.join(os.path.dirname(__file__), "..", exe_name)

    if not os.path.exists(exe_path):
        print(f"Ошибка: исполняемый файл '{exe_path}' не найден.")
        return

    A = np.random.rand(N, N).astype(np.float64)
    B = np.random.rand(N, N).astype(np.float64)
    np.savetxt(fileA, A, fmt='%f')
    np.savetxt(fileB, B, fmt='%f')

    expected_C = np.dot(A, B)

    try:
        result = subprocess.run(
            [exe_path, str(N), str(threads), fileA, fileB, fileC],
            capture_output=True, text=True, check=True
        )
        cpp_time = float(result.stdout.strip())
        print(f"Успешно. Время OpenMP: {cpp_time:.2f} мс")
    except subprocess.CalledProcessError as e:
        print("Ошибка запуска C++.")
        print(e.stderr)
        return

    actual_C = np.loadtxt(fileC)
    is_correct = np.allclose(expected_C, actual_C, atol=1e-3)

    if is_correct:
        print("✅ Результаты совпали")
    else:
        print("❌ Результаты не совпадают.")

    for f in [fileA, fileB, fileC]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    run_verification(400, 4)