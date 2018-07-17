import setuptools

with open('../README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='shacl_form',
    version='1.0',
    author='Laura Guillory',
    author_email='laura.guillory@csiro.au',
    description='Auto-generation of web UIs, given only a logical expression of the data model as a SHACL shape.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/CSIRO-enviro-informatics/shacl-form',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    )
)
