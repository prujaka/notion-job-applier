from setuptools import setup, find_packages


with open('requirements.txt', 'r') as f:
    content = f.readlines()
requirements = [x.strip() for x in content]

setup(
    name='jobapplier',
    version='0.1',
    install_requires=requirements,
    packages=find_packages()
)
