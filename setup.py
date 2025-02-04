import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mark-report-rginestou",
    version="0.1.0",
    author="Alex Yucra",
    author_email="xalextrack@gmail.com",
    description="Relatorio elegante em markdown para PDF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alexyucra/MarkdownReport",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",    
    ],
    install_requires=[
        'weasyprint',
        'pyinotify',
        'playwright',
        'go',
        'chromedriver-autoinstaller',
        'selenium',
        'requests',
        'beautifulsoup4',
        'pandas',
        'numpy',
    ],
)
