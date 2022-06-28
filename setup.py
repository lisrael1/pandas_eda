import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pandas_eda",
    version="0.3",
    author="Lior Israeli",
    author_email="israelilior@gmail.com",
    description="streamlit app to display table and main content for each column",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lisrael1/pandas_eda",
    project_urls={
        "Bug Tracker": "https://github.com/lisrael1/pandas_eda/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"": ["*.xlsx"]},
    install_requires=[['tqdm', 'pandas', 'streamlit', 'numpy', 'faker']],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src", exclude=['*_tests', '*_examples'], ),
    python_requires=">=3.6",
)

