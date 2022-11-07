from setuptools import setup, find_packages

setup(
    name="backupmanager",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'hello = backupmanager.command:main'
        ]
    },
    install_requires=['fastapi', 'structlog', 'google-cloud-compute', 'rich'],
    extras_require={
        'dev': ['pytest', 'mypy', 'flake8']
    },
)
