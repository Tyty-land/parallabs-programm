#include <iostream>
#include <vector>
#include <fstream>
#include <chrono>
#include <string>
#include <mpi.h>

using namespace std;

// Чтение матрицы (Главный процесс)
bool readMatrix(const string& filename, vector<double>& matrix, int N) {
    ifstream file(filename);
    if (!file.is_open()) return false;
    for (int i = 0; i < N * N; ++i) {
        file >> matrix[i];
    }
    return true;
}

// Запись матрицы (Главный процесс)
bool writeMatrix(const string& filename, const vector<double>& matrix, int N) {
    ofstream file(filename);
    if (!file.is_open()) return false;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            file << matrix[i * N + j] << " ";
        }
        file << "\n";
    }
    return true;
}

int main(int argc, char* argv[]) {
    // Инициализация среды MPI
    MPI_Init(&argc, &argv);

    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank); // Получаем номер текущего процесса (ранг)
    MPI_Comm_size(MPI_COMM_WORLD, &size); // Получаем общее количество процессов

    if (argc != 5) {
        if (rank == 0) {
            cerr << "Usage: " << argv[0] << " <N> <fileA> <fileB> <fileC>\n";
        }
        MPI_Finalize();
        return 1;
    }

    int N = stoi(argv[1]);
    string fileA = argv[2];
    string fileB = argv[3];
    string fileC = argv[4];

    // Проверяем делимость размера матрицы на количество процессов
    if (N % size != 0) {
        if (rank == 0) {
            cerr << "Error: Matrix size " << N << " must be divisible by the number of processes " << size << ".\n";
        }
        MPI_Finalize();
        return 1;
    }

    int rows_per_proc = N / size; // Сколько строк на процесс

    vector<double> full_A;
    vector<double> full_C;
    
    vector<double> B(N * N);

    vector<double> local_A(rows_per_proc * N);
    vector<double> local_C(rows_per_proc * N, 0.0);

    if (rank == 0) {
        full_A.resize(N * N);
        full_C.resize(N * N);
        if (!readMatrix(fileA, full_A, N) || !readMatrix(fileB, B, N)) {
            cerr << "Error reading input files on root process.\n";
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
    }

    // Синхронизируем процессы перед началом замера времени
    MPI_Barrier(MPI_COMM_WORLD);
    double start_time = MPI_Wtime();

    MPI_Bcast(B.data(), N * N, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    MPI_Scatter(full_A.data(), rows_per_proc * N, MPI_DOUBLE, 
                local_A.data(), rows_per_proc * N, MPI_DOUBLE, 
                0, MPI_COMM_WORLD);

    for (int i = 0; i < rows_per_proc; ++i) {
        for (int k = 0; k < N; ++k) {
            double r = local_A[i * N + k];
            for (int j = 0; j < N; ++j) {
                local_C[i * N + j] += r * B[k * N + j];
            }
        }
    }

    MPI_Gather(local_C.data(), rows_per_proc * N, MPI_DOUBLE, 
               full_C.data(), rows_per_proc * N, MPI_DOUBLE, 
               0, MPI_COMM_WORLD);

    // Синхронизируем процессы после вычислений
    MPI_Barrier(MPI_COMM_WORLD);
    double end_time = MPI_Wtime();

    if (rank == 0) {
        if (!writeMatrix(fileC, full_C, N)) {
            cerr << "Error writing output file.\n";
            MPI_Abort(MPI_COMM_WORLD, 1);
        }
        cout << (end_time - start_time) * 1000.0 << endl;
    }

    MPI_Finalize();
    return 0;
}