try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# package_data info must!! also be added to MANIFEST.in!

setup(
    name='tt_reduce',
    description="libraries for reducing complex social data to feature vectors.",
    long_description=(
        '%s\n\n%s' % (
            open('README.md').read(),
            open('CHANGELOG.md').read()
        )
    ),
    version=open('VERSION').read().strip(),
    author='TipTap',
    install_requires=['nltk', 'pytrie', 'regex'],
    package_dir={'tt_reduce': 'src'},
    packages=['tt_reduce'],
    include_package_data=True,
    package_data={'tt_social': ['dictionaries/*', 'text/*']}
)
