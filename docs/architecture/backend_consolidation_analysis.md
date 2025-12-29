# Critical Analysis: The 3-Port Problem (Backend Consolidation)

## 1. Finding
Upon inspection of processes running on ports `8000`, `8080`, and `3001`, we discovered a critical inefficiency:

| Port | Process | Command Line | Status |
| :--- | :--- | :--- | :--- |
| **8000** | `uvicorn` | `web.backend.main:app --host 0.0.0.0 --port 8000` | **Active (API Gateway)** |
| **8080** | `uvicorn` | `web.backend.main:app --host 0.0.0.0 --port 8080` | **Redundant Replica** |
| **3001** | `uvicorn` | `web.backend.main:app --host 0.0.0.0 --port 3001` | **Redundant Replica** |

**Diagnosis**: The system is running **three identical copies** of the full backend application. This triples the memory usage (loading shared libraries, Python interpreter overhead) without providing true microservice separation, as they all run the same monolithic `web.backend.main`.

## 2. Answers to User Questions

> **Q: Does the system already have a mode to call a backend for security if needed?**
> **A:** Yes, the single backend on 8000 handles auth, security, and metrics via `apiService`.

> **Q: Does 8000:8080:3001 help api calls or overload the machine?**
> **A:** It **overloads the machine**. Since they are identical replicas on the same machine, they compete for the same CPU/RAM. Unless you have a load balancer (like Nginx) actively distributing traffic between them (which is not configured in `api.ts`), ports 8080 and 3001 are likely idle zombies consumig resources.

> **Q: Could it be unified into two (8000/8080 or 8000/3001)?**
> **A:** It should be unified into **ONE** (8000). Modern Async Python (FastAPI/Uvicorn) can handle concurrency on a single port efficiently. If "Metrics" were a separate lightweight microservice (e.g., just returning `psutil` stats), a separate port would make sense. But currently, it's a full clone.

> **Q: Does it make sense to have a backend just for metrics?**
> **A:** Only if the Main Backend is blocking the event loop with heavy inference. However, since the current "Metrics Backend" is just a clone of the "Heavy Backend", it inherits the same startup cost.

## 3. Recommendation

1.  **Terminate** processes on 3001 and 8080.
2.  **Consolidate** all traffic to 8000.
3.  **Refactor** Metrics: If isolation is needed, create a `metrics_server.py` that imports **only** `psutil` and `fastapi`, preventing it from loading the heavy ML libraries.

**Proposed Action**: Stop the redundant services immediately to free up system resources for the Neural/Quantum simulation.
