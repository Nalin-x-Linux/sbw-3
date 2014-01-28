from distutils.core import setup
from glob import glob
setup(name='sbw2',
      version='2.1',
      description='Python Distribution Utilities',
      author='Nalin.x.Linux',
      author_email='Nalin.x.Linux@gmail.com',
      url='https://github.com/Nalin-x-Linux/',
      license = 'GPL-3',
      packages=['sbw2'],
      data_files=[('share/applications',glob('share/applications/*')),
      ('share/pyshared/sbw2/data/english/',glob('share/pyshared/sbw2/data/english/*')),
      ('share/pyshared/sbw2/data/hindi/',glob('share/pyshared/sbw2/data/hindi/*')),
      ('share/pyshared/sbw2/data/kannada/',glob('share/pyshared/sbw2/data/kannada/*')),
      ('share/pyshared/sbw2/data/malayalam/',glob('share/pyshared/sbw2/data/malayalam/*')),
      ('share/pyshared/sbw2/data/numerical/',glob('share/pyshared/sbw2/data/numerical/*')),
      ('share/pyshared/sbw2/data/tamil/',glob('share/pyshared/sbw2/data/tamil/*')),
      ('share/pyshared/sbw2/data/spanish/',glob('share/pyshared/sbw2/data/spanish/*')),
      ('share/pyshared/sbw2/data/',glob('share/pyshared/sbw2/data/languages.txt')),
      ('share/pyshared/sbw2/ui/',glob('share/pyshared/sbw2/ui/*')),
      ('bin/',glob('bin/*'))]
      )
