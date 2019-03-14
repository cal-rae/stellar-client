from setuptools import setup

setup(
    name='stellar_client',
    version='0.1',
    description='Client for querying the New Sun Road Stellar API',
    url='http://github.com/cal-rae/stellar-client',
    author='leejt489',
    author_email='leejt489@users.noreply.github.com',
    license='MIT',
    packages=['stellar_client'],
    zip_safe=False,
    install_requires=[
        'pandas',
        'pytz',
        'requests'
    ]
)
