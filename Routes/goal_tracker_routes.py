from fastapi import FastAPI


# Create the FastAPI application instance
app = FastAPI(
    title="Employee API",
    description="A simple API for managing employee records.",
    version="1.0.0"
)

# A basic (synchronous) route to confirm the app is running
@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee API"}