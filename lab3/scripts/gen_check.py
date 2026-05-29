import numpy as np
import subprocess
import os
import sys

def run_verification(N=400, procs=4):
      
    fileA = "temp_A.txt"
    fileB = "temp_B.txt"
    fileC = "temp_C.txt"
    
    exe_name = "main.exe" if sys.platform == "win32" else "./main"
    exe_path = os.path.join(os.path.dirname(__file__), "..", exe_name)

    if not os.path.exists(exe_path):
        print(f"Ошибка: исполняемый файл '{exe_path}' не найден.")
        return

    mpiexec_cmd = "mpiexec"
    if sys.platform == "win32":
        default_msmpi_path = r"C:\Program Files\Microsoft MPI\Bin\mpiexec.exe"
        if os.path.exists(default_msmpi_path):
            mpiexec_cmd = default_msmpi_path

    A = np.random.rand(N, N).astype(np.float64)
    B = np.random.rand(N, N).astype(np.float64)
    np.savetxt(fileA, A, fmt='%f')
    np.savetxt(fileB, B, fmt='%f')

    expected_C = np.dot(A, B)

    try:
        # Запуск через определенный нами mpiexec
        result = subprocess.run(
            [mpiexec_cmd, "-n", str(procs), exe_path, str(N), fileA, fileB, fileC],
            capture_output=True, text=True, check=True
        )
        mpi_time = float(result.stdout.strip())
        print(f"Успешно. Время MPI: {mpi_time:.2f} мс")
    except subprocess.CalledProcessError as e:
        print("Ошибка запуска MPI!")
        print(e.stderr)
        return

    actual_C = np.loadtxt(fileC)
    is_correct = np.allclose(expected_C, actual_C, atol=1e-3)

    if is_correct:
        print("✅ Результаты MPI совпадают.")
    else:
        print("❌ Результаты MPI не совпадают.")

    for f in [fileA, fileB, fileC]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    run_verification(400, 4)