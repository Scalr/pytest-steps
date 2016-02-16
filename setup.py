from setuptools import setup
import codecs

setup(
    name='pytest-steps',
    description=(
        'pytest-steps is a plugin for py.test that add a steps for test suites'
    ),
    long_description=codecs.open("README.rst", encoding='utf-8').read(),
    version='0.1.1',
    license='BSD',
    author='Oleg Suhavrev',
    author_email='gigimon4ik@gmail.com',
    py_modules=['pytest_steps', 'hooks'],
    entry_points={'pytest11': ['steps = pytest_steps']},
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['pytest>=2.6'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ]
)