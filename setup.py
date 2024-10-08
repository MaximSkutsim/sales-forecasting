from setuptools import find_packages, setup

setup(
    name="stock_management",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy>=1.24.3",
        "pandas>=2.0.2",
        "scikit-learn>=1.2.2",
        "fastapi>=0.95.2",
        "uvicorn>=0.22.0",
        "python-multipart>=0.0.6",
        "pydantic>=1.10.7",
        "clearml>=1.10.3",
        "fire>=0.5.0",
        "tqdm>=4.65.0",
        "python-dateutil>=2.8.2",
        "requests>=2.31.0",
    ],
    python_requires=">=3.8",
    author="Skutin Maxim",
    author_email="mskutsin921@gmail.com",
    description="Система прогнозирования спроса и управления запасами",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.comMaximSkutsim/sales-forecasting",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
