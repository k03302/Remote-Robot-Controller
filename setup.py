from setuptools import setup, find_packages
from mobile_robot_controller.info import __package_name__, __version__

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requires = f.read().splitlines()
with open('test_requirements.txt', 'r', encoding='utf-8') as f:
    test_requires = f.read().splitlines()


setup(
    name=__package_name__,
    version=__version__,
    long_description=readme,
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    package_data={'': ['*.yaml', '*.yml']},
    install_requires=requires,
    setup_requires=['pytest-runner'],
    tests_require=test_requires,
    python_requires='>3.6',
    classifiers=[
        'Environment :: Console',
        'Operating System :: POSIX :: LINUX',
        'Programming Language :: Python :: 3.6'
    ]
)