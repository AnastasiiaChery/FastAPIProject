from setuptools import setup

setup(
    name="ai-pr-autopilot",
    version="0.1.0",
    description="AI-powered PR generator using multi-agent pipeline",
    py_modules=["main"],
    install_requires=["anthropic>=0.25.0"],
    entry_points={
        "console_scripts": [
            "ai-pr=main:main",   # ← makes `ai-pr "..."` work globally
        ],
    },
    python_requires=">=3.9",
)