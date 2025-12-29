#include <stdio.h>
#include <cuda.h>
#include <cuda_runtime.h>

int main() {
    CUresult res;
    CUdevice dev;
    CUcontext ctx;
    int devCount = 0;

    printf("Initializing CUDA Driver API...\n");
    res = cuInit(0);
    if (res != CUDA_SUCCESS) {
        printf("❌ cuInit failed with error: %d\n", res);
        const char* errStr;
        cuGetErrorString(res, &errStr);
        printf("Error string: %s\n", errStr);
        return 1;
    }
    printf("✅ cuInit successful\n");

    res = cuDeviceGetCount(&devCount);
    if (res != CUDA_SUCCESS) {
        printf("❌ cuDeviceGetCount failed: %d\n", res);
        return 1;
    }
    printf("Device count: %d\n", devCount);

    if (devCount > 0) {
        res = cuDeviceGet(&dev, 0);
        if (res != CUDA_SUCCESS) {
            printf("❌ cuDeviceGet failed: %d\n", res);
            return 1;
        }

        char name[128];
        cuDeviceGetName(name, 128, dev);
        printf("Device 0: %s\n", name);

        // Try Runtime API
        printf("\nTesting Runtime API...\n");
        cudaError_t rRes = cudaGetDeviceCount(&devCount);
        if (rRes != cudaSuccess) {
            printf("❌ cudaGetDeviceCount failed: %s\n", cudaGetErrorString(rRes));
        } else {
            printf("✅ Runtime API sees %d devices\n", devCount);
        }
    }

    return 0;
}
