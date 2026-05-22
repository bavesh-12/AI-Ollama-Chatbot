import uvicorn

if __name__ == "__main__":
    print("🚀 Starting AI Chat Interface...")
    print("📱 Open: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop")
    print()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)