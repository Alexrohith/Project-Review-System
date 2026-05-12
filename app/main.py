"""
AI Project Reviewer - Main Application Entry Point

This application provides AI-powered code review, project analysis,
technical interviews, and gap analysis for software projects.
"""

import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.review import router as review_router

# Load environment variables
load_dotenv()

# Create main FastAPI application
app = FastAPI(
    title="AI Project Reviewer",
    description="AI-powered project review system with code analysis, interviews, and gap detection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the review API router
app.include_router(review_router, prefix="/api", tags=["review"])

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Project Reviewer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }


def main():
    """Main entry point to run the application."""
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))

    print(f"Starting AI Project Reviewer on port {port}")
    print(f"API Documentation available at: http://localhost:{port}/docs")

    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )


if __name__ == "__main__":
    main()
