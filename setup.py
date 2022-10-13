import setuptools

setuptools.setup(
    name='baseballator',
    version='0.1.1',
    url='https://github.com/dolyasergey/baseballator_project',
    author='Sergio Dolia',
    author_email='sergei.s.dolia@gmail.com',
    description='Baseball Simulator based on probabilitites',
    long_description=open('README.md').read(),
    packages=setuptools.find_packages(),
    package_dir={'': '/Users/dolyasergey/My Files/Sport Stats/baseball/baseballator_project/baseballator'},
    install_requires=[],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True,
    package_data={'' :['data/*']},
)