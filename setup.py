from setuptools import setup, find_packages
import sys, os

version = '0.1.5'

setup(name='pyspoolingstack',
      version=version,
      description="A stack that will only grow to a certain point before it "
                  "pushes to physical files, and vice-versa.",
      long_description="A stack that will only grow to a certain point before "
                       "it pushes to physical files, and vice-versa. Was "
                       "developed to be used as a temporary spool for massive "
                       "amounts of incoming heirarchical data that is "
                       "received in no particular order, prior to pushing it "
                       "into the DB. Also provides a 'collection'-type class "
                       "for managing many stacks concurrently.",
      classifiers=['Development Status :: 5 - Production/Stable',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Utilities' ],
      keywords='python stack spool file',
      author='Dustin Oprea',
      author_email='myselfasunder@gmail.com',
      url='https://github.com/dsoprea/PySpoolingStack',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

