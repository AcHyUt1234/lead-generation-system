from setuptools import setup, find_packages

setup(
    name="lead-generation-system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        line.strip()
        for line in open('requirements.txt').readlines()
        if line.strip() and not line.startswith('#')
    ],
    python_requires=">=3.10",
    author="Achyut Dubey",
    description="Automated lead generation pipeline for high-pain IT sales roles",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
)