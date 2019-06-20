import re
from setuptools import setup

pkg_version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('Jackin4Beats/Jackin4Beats.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

    
setup(
        name='Jackin4Beats',
        version=pkg_version,
        description='Includes CLI tools useful for processing audio files.',
        long_description=long_descr,
        url='https://github.com/JoeArauzo/Jackin4Beats.git',
        author='Joe Arauzo',
        author_email='joe@arauzo.net',
        license='GPLv3+',
        packages=['Jackin4Beats'],
        install_requires=['Click','pydub', 'pytaglib', 'Send2Trash', 'sh'],
        entry_points={
            "console_scripts": ['trim-audiosilence = Jackin4Beats.Jackin4Beats:trim_audiosilence'],
            "console_scripts": ['write-sourceinfo = Jackin4Beats.Jackin4Beats:write-sourceinfo']
            },
        zip_safe=False
)
