#include <iostream>
#include <vector>
#include <fstream>
#include <chrono>
#include <string>
#include <omp.h>

using namespace std;

bool readMatrix(const string& filename, vector<double>& matrix, int N) {
    ifstream file(filename);
    if (!file.is_open()) return false;
    for (int i = 0; i < N * N; ++i) {
        file >> matrix[i];
    }
    return true;
}

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
    if (argc != 6) {
        cerr << "Usage: " << argv[0] << " <N> <num_threads> <fileA> <fileB> <fileC>\n";
        return 1;
    }

    int N = stoi(argv[1]);
    int num_threads = stoi(argv[2]);
    string fileA = argv[3];
    string fileB = argv[4];
    string fileC = argv[5];

    vector<double> A(N * N);
    vector<double> B(N * N);
    vector<double> C(N * N, 0.0);

    if (!readMatrix(fileA, A, N) || !readMatrix(fileB, B, N)) {
        cerr << "Error reading input files.\n";
        return 1;
    }

    // Устанавливаем количество потоков для OpenMP
    omp_set_num_threads(num_threads);

    auto start = chrono::high_resolution_clock::now();

    // Параллелим внешний цикл i с помощью OpenMP
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < N; ++i) {
        for (int k = 0; k < N; ++k) {
            double r = A[i * N + k];
            for (int j = 0; j < N; ++j) {
                C[i * N + j] += r * B[k * N + j];
            }
        }
    }

    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double, milli> duration = end - start;

    if (!writeMatrix(fileC, C, N)) {
        cerr << "Error writing output file.\n";
        return 1;
    }

    cout << duration.count() << endl;

    return 0;
}