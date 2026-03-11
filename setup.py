"""
Setup script for sentinel-py package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sentinel-py",
    version="0.1.0",
    author="Mars",
    author_email="",
    description="Python version of Alibaba Sentinel - Flow control, circuit breaking and system protection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/marsbot-ai/sentinel-py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    keywords="sentinel flow-control circuit-breaker system-protection microservices",
    project_urls={
        "Bug Reports": "https://github.com/marsbot-ai/sentinel-py/issues",
        "Source": "https://github.com/marsbot-ai/sentinel-py",
    },
)
