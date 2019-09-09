from setuptools import setup

setup(
    name="api-acceptance-tests",
    packages=['api-acceptance-tests'],
    version="0.1",
    description='Python framework for Reward Gateway API testing',
    long_description_content_type='text/markdown',
    license='Apache 2.0',
    author='Robin Miklinski',
    url='',
    download_url='',
    install_requires=['nose', 'requests>=2.11.1', 'jsonpath-rw', 'lxml', 'unicodecsv', 'pytest'],
)