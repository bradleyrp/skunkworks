#!/usr/bin/env python

"""
ORTHO
Simple configuration manager.
"""

from __future__ import print_function
import os,json,re
from .misc import treeview,str_types
from .bootstrap import bootstrap
<<<<<<< HEAD

# exported in from __init__.py (defined for linting)
conf = {}
config_fn = None
=======
>>>>>>> 3a34d39c903bc43c6d66011edf534b0ebcd27c10

def abspath(path):
	"""Get the right path."""
	return os.path.abspath(os.path.expanduser(path))

def read_config(source=None,default=None):
	"""Read the configuration."""
	global config_fn
	source = source if source else config_fn
	locations = [abspath(source),os.path.join(os.getcwd(),source)]
	found = next((loc for loc in locations if os.path.isfile(loc)),None)
	if not found and default==None: raise Exception('cannot find file "%s"'%source)
	elif not found and default!=None: 
		# when new users run make for the first time and create the config.json it also runs bootstrap.py
		# ... to set up any other paths from the dependent module
		boot = bootstrap(post=False)
		if type(boot)==dict:
			if 'default' not in boot and 'post' not in boot: 
				raise Exception('bootstrap.py must contain function bootstrap_default or bootstrap_post')
			elif 'default' in boot: default.update(**boot.get('default',{}))
		# we write the config once even if bootstrap writes it again
		write_config(config=default,source=locations[0])
		#!!!!!!!!!
		if False:
			if type(boot)==dict and 'post' in boot: 
				import time
				time.sleep(3)
				boot['post']()
		return default
	else: 
		with open(found,'r') as fp: 
			return json.load(fp)

def write_config(config,source=None):
	"""Write the configuration."""
	global config_fn
	with open(source if source else config_fn,'w') as fp:
		json.dump(config,fp)

def interpret_command_text(raw):
	"""
	Interpret text pythonically, if possible.
	Adapted from the pseudo-yaml parser in automacs.
	Note that sending in python text from makefile requires weird syntax: key=\""<expression>"\"
	"""
	try: val = eval(raw)
	except: val = raw
	# protect against sending e.g. "all" as a string and evaluating to builtin all function
	if val.__class__.__name__=='builtin_function_or_method': result = str(val)
	elif type(val) in [list,dict]: result = val
	elif type(val) in str_types:
		if re.match('^(T|t)rue$',val): result = True
		elif re.match('^(F|f)alse$',val): result = False
		elif re.match('^(N|n)one$',val): result = None
		#! may be redundant with the eval command above
		elif re.match('^[0-9]+$',val): result = int(val)
		elif re.match(r"^[0-9]*\.[0-9]*$",val): result = float(val)
		else: result = val
	else: result = val
	return result

def set_config(*args,**kwargs):
	"""
	Update the configuration in a local configuration file (typically ``config.py``).
	This function routes ``make set` calls so they update flags using a couple different syntaxes.
	We make a couple of design choices to ensure a clear grammar: a
	1. a single argument sets a boolean True (use unset to remove the parameter and as a style convention, 
		always assume that something is False by default, or use kwargs to specify False)
	2. pairs of arguments are interpreted as key,value pairs
	3. everything here assumes each key has one value. if you want to add to a list, use ``setlist``
	"""
	global conf # from __init__.py
	outgoing = dict()
	# pairs of arguments are interpreted as key,value pairs
	if len(args)%2==0: outgoing.update(**dict(zip(args[::2],args[1::2])))
	# one argument means we set a boolean
	elif len(args)==1: outgoing[args[0]] = True
	else: raise Exception('set_config received an odd number of arguments more than one: %s'%args)
	# interpret kwargs with an opportunity to use python syntax, or types other than strings
	for key,raw in kwargs.items(): outgoing[key] = interpret_command_text(raw)
	# write the config
	conf.update(**outgoing)
	write_config(conf)

def setlist(*args):
	"""
	Special handler for adding list items.
	The first argument must be the key and the following arguments are the values to add. Send kwargs to the
	``unset`` function below to remove items from the list.
	"""
	global conf,config_fn # from __init__.py
	if len(args)<=1: raise Exception('invalid arguments for setlist. you need at least two: %s'%args)
	key,vals = args[0],list(args[1:])
	if key not in conf: conf[key] = vals
	elif type(conf[key])!=list: raise Exception('cannot convert singleton to list in %s'%config_fn)
	else: conf[key] = list(set(conf[key]+vals))
	write_config(conf)

def unset(*args):
	"""Remove items from config."""
	config = read_config()
	for arg in args: 
		if arg in config: del config[arg]
		else: print('[WARNING] cannot unset %s because it is absent'%arg)
	write_config(config)

def config():
	"""Print the configuration."""
	global conf,config_fn # from __init__.py
	treeview({config_fn:conf})

def set_hash(*args,**kwargs):
	"""
	Add a dictionary hash to the configuration.
	Note that sending a pythonic hash through makefile otherwise requires the following clumsy syntax:
		make set env_ready=\""{'CONDA_PREFIX':'/Users/rpb/worker/factory/env/envs/py2'}"\"
	This method names the hash with the first argument and the rest are key,value pairs.
	Also accepts kwargs which override any args.
	Interprets pythonic strings.
	"""
	use_note = '`make set_hash <name> <key_1> <val_1> <key_2> <val_2> key_3=val3 ...`'
	if len(args)==0 or len(args)%2!=1: 
		print('usage',use_note)
		raise Exception('invalid arguments args=%s kwargs=%s'%(str(args),kwargs))
	name,pairs = args[0],args[1:]
	pairwise = dict(zip(pairs[::2],pairs[1::2]))
	pairwise.update(**kwargs)
	for key,val in pairwise.items():
	 	pairwise[key] = interpret_command_text(val)
	conf[name] = pairwise
	write_config(conf)
