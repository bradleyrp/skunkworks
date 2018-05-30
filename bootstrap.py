#!/usr/bin/env python -B

"""
Bootstrap the configuration for a module that uses the ortho module to control the configuration.
Note that this script must be called `bootstrap.py` and must supply a function called `bootstrap_default` 
which returns the default configuration and/or a function called `bootstrap_post` which runs other
configuration tasks. If these are missing the user is warned.
"""

from __future__ import print_function

# currently using default envs which expects a local link to Miniconda3-latest-Linux-x86_64.sh
# see environments.py for instructions on (re)-loading a complicated envs section after bootstrapping
# you could also make your own default configuration for use with ortho
default_configuration = {
	'commands':['cli.py'],
}

def bootstrap_default(): 
	"""
	Return default configuration.
	You can also run other commands here 
	but they will not print to stdout and they cannot use the config yet.
	"""
	return default_configuration

def bootstrap_post():
	"""
	Commands after configuration is written.
	For some reason `make config` fails here.
	"""
	import os
	print('status','running bootstrap_post from bootstrap.py')
	os.system('make config')
	return
