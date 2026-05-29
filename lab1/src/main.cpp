#include <iostream>
#include <vector>
#include <fstream>
#include <chrono>
#include <string>

using namespace std;

// Чтение матриц
bool readMatrix(const string& filename, vector<double>& matrix, int N) {
    ifstream file(filename);
    if (!file.is_open()) return false;
    for (int i = 0; i < N * N; ++i) {
        file >> matrix[i];
    }
    return true;
}

// Запись
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
    // Проверка аргументов командной строки
    if (argc != 5) {
        cerr << "Usage: " << argv[0] << " <N> <fileA> <fileB> <fileC>\n";
        return 1;
    }

    int N = stoi(argv[1]);
    string fileA = argv[2];
    string fileB = argv[3];
    string fileC = argv[4];

    vector<double> A(N * N);
    vector<double> B(N * N);
    vector<double> C(N * N, 0.0);

    if (!readMatrix(fileA, A, N) || !readMatrix(fileB, B, N)) {
        cerr << "Error reading input files.\n";
        return 1;
    }

    auto start = chrono::high_resolution_clock::now();

    // Порядок циклов i-k-j
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