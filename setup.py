from setuptools import setup, find_packages

setup(
    name="mcp-agent-stack",
    version=open("VERSION").read().strip(),
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
