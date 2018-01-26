from setuptools import setup

setup(
    name='aws-arn',
    version='0.1.0',
    description='Create properly formatted AWS ARNs according to service rules',
    packages=["aws_arn"],
    package_data={
        "aws_arn": ["config.json"]
    },
    entry_points={
        'console_scripts': [
            'aws-arn = aws_arn:main',
        ],
    },
    author='Ben Kehoe',
    author_email='bkehoe@irobot.com',
    project_urls={
        "https://github.com/benkehoe/aws-arn",
    },
    license='Apache Software License 2.0',
    classifiers=(
        'Development Status :: 2 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: Apache Software License',
    ),
    keywords='aws arn',
)