from setuptools import setup, find_packages

setup(
    name='LibraryX',  # Replace with your own package name
    version='0.1.0-alpha',  # The initial release version
    author='Jack Zhou / Eric Chen',  # Your name
    author_email='D1172271@o365.fcu.edu.tw',  # Your email
    description='A custom library for networking application final project',  # A short description
    url='https://github.com/Falsedeer/Networking-Final',  # Link to your project's repository
    packages=find_packages(),  # Automatically find all packages in your project
    install_requires=[
        # List of dependencies, for example:
        mysqlclient,
        pyYAML,
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum version requirement of the package
)
