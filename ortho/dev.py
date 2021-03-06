#!/usr/bin/env python

"""
ORTHO
development tools
"""

from __future__ import print_function
import sys,re,traceback
from .misc import say

def tracebacker_base(exc_type,exc_obj,exc_tb,debug=False):
	"""Standard traceback handling for easy-to-read error messages."""
	tag = say('[TRACEBACK]','gray')
	tracetext = tag+' '+re.sub(r'\n','\n%s'%tag,str(''.join(traceback.format_tb(exc_tb)).strip()))
	if not debug:
		print(say(tracetext))
		print(say('[ERROR]','red_black')+' '+say('%s'%exc_obj,'cyan_black'))
	else: 
		try: import ipdb as pdb_this
		except: 
			print('note','entering debug mode but cannot find ipdb so we are using pdb')
			import pdb as pdb_this
		print(say(tracetext))	
		print(say('[ERROR]','red_black')+' '+say('%s'%exc_obj,'cyan_black'))
		print(say('[DEBUG] entering the debugger','mag_gray'))
		import ipdb;ipdb.set_trace()
		pdb_this.pm()

def tracebacker(*args,**kwargs):
	"""Standard traceback handling for easy-to-read error messages."""
	debug = kwargs.pop('debug',False)
	if kwargs: raise Exception('unprocessed kwargs %s'%kwargs)
	# note: previously handled interrupt here but this prevents normal traceback
	if len(args)==1: 
		exc_type,exc_obj,exc_tb = sys.exc_info()
		tracebacker_base(exc_type,exc_obj,exc_tb,debug=debug)
	elif len(args)==3: tracebacker_base(*args,debug=debug)
	else: raise Exception(
		'tracebacker expects either one or three arguments but got %d'%
		len(args))

def debugger(*args): 
	"""Run the tracebacker with interactive debugging if possible."""
	debug = not (hasattr(sys, 'ps1') or not sys.stderr.isatty())
	if args[0]==KeyboardInterrupt: 
		print()
		print('status','received KeyboardInterrupt')
		debug = False
	return tracebacker(*args,debug=debug)
