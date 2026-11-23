"""
Runner script to launch Open Source Issue Scout + Fix Coach
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Open Source Issue Scout + Fix Coach Dashboard...")
    print("Open your browser at: http://localhost:8000")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
