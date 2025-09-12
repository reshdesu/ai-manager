from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-context-manager",
    version="1.0.0",
    author="AI Context Manager Team",
    author_email="ai-context-manager@example.com",
    description="Intelligent AI context management system for any project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-context-manager/ai-context-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-context=ai_context_manager.cli:main",
            "ai-context-init=ai_context_manager.cli:init_command",
            "ai-context-maintain=ai_context_manager.cli:maintain_command",
        ],
    },
    include_package_data=True,
    package_data={
        "ai_context_manager": ["templates/*/*.json"],
    },
)
