#include <iostream>
#include <vector>
#include <fstream>
#include <chrono>
#include <string>
#include <cuda_runtime.h>

using namespace std;

// Функция-ядро, которая будет выполняться параллельно на тысячах ядер видеокарты
__global__ void matrixMulKernel(double* d_A, double* d_B, double* d_C, int N) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < N && col < N) {
        double sum = 0.0;
        for (int k = 0; k < N; ++k) {
            sum += d_A[row * N + k] * d_B[k * N + col];
        }
        d_C[row * N + col] = sum;
    }
}

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
        cerr << "Usage: " << argv[0] << " <N> <block_size> <fileA> <fileB> <fileC>\n";
        return 1;
    }

    int N = stoi(argv[1]);
    int block_size = stoi(argv[2]);
    string fileA = argv[3];
    string fileB = argv[4];
    string fileC = argv[5];

    vector<double> h_A(N * N);
    vector<double> h_B(N * N);
    vector<double> h_C(N * N);

    if (!readMatrix(fileA, h_A, N) || !readMatrix(fileB, h_B, N)) {
        cerr << "Error reading input files.\n";
        return 1;
    }

    size_t size = N * N * sizeof(double);
    double *d_A, *d_B, *d_C;

    cudaMalloc(&d_A, size);
    cudaMalloc(&d_B, size);
    cudaMalloc(&d_C, size);

    cudaMemcpy(d_A, h_A.data(), size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B.data(), size, cudaMemcpyHostToDevice);

    dim3 threadsPerBlock(block_size, block_size);
    dim3 numBlocks((N + block_size - 1) / block_size, (N + block_size - 1) / block_size);

    cudaDeviceSynchronize();
    auto start = chrono::high_resolution_clock::now();

    matrixMulKernel<<<numBlocks, threadsPerBlock>>>(d_A, d_B, d_C, N);

    cudaDeviceSynchronize();
    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double, milli> duration = end - start;

    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        cerr << "CUDA Error: " << cudaGetErrorString(err) << endl;
        cudaFree(d_A); cudaFree(d_B); cudaFree(d_C);
        return 1;
    }

    cudaMemcpy(h_C.data(), d_C, size, cudaMemcpyDeviceToHost);

    if (!writeMatrix(fileC, h_C, N)) {
        cerr << "Error writing output file.\n";
        return 1;
    }

    cudaFree(d_A); cudaFree(d_B); cudaFree(d_C);
    cout << duration.count() << endl;
    return 0;
}