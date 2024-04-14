from setuptools import setup
import os


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('mousepad')

setup(
    name='mousepad',
    version='0.1.1',
    description='Multidevice controller using python',
    url='https://github.com/neetishsingh/mousepad',
    author='Neetish Singh',
    author_email='neetishsingh97@gmail.com',
    license='MIT License',
    packages=['mousepad'],
    package_data={'mousepad': extra_files},
    include_package_data=True,
    install_requires=['fastapi',
                      'uvicorn[standard]', 'asyncio', 'pyautogui'
                      ],

    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: Freeware',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python'
    ],
)
