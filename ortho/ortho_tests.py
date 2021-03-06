#!/usr/bin/env python

"""
Unit test definitions for ortho.
Called by unittester so each suite runs in written order.
Call standard tests with `make unittester` and special ones with `make unittester name=special`.

move or abscond?
    move env, config.json (done), reqs.yaml
or alternately make everything else temporary?
    ...
"""

# note that unicode_literals is good for backporting to 2 because it presumes u'string' everywhere
from __future__ import print_function,unicode_literals
import unittest
import os,sys,copy,re,json
import ortho
# multiple ways to check strings but recommended methid is isinstance(u'string',string_types)
from ortho.misc import str_types,string_types,basestring

#! via: https://stackoverflow.com/questions/3223604
import contextlib,shutil,tempfile
@contextlib.contextmanager
def cd(newdir, cleanup=lambda: True):
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try: yield
    finally:
        os.chdir(prevdir)
        cleanup()
@contextlib.contextmanager
def tempdir():
    dirpath = tempfile.mkdtemp()
    def cleanup(): shutil.rmtree(dirpath)
    with cd(dirpath, cleanup): yield dirpath

# pylint: disable=not-callable,no-member

config_fn = 'config.json'

dummy_function = """
def dummy(): print('special code')
"""

dummy_function_conda_list = """
import os
def conda_list(): 
    os.system('WHERE_CONDA list')
"""

reqs_basic = {'channels':['conda-forge','defaults'],'dependencies':['ipdb','scipy','pylint']}

### GENERIC TESTS

# recommend testing Python 2 and 3 compatibility for generic tests and Ortho below with:
#   python=python3 make unittester && make unittester
#   but be sure to unset activate_env temporarily

class TestOrthoBasicPython2(unittest.TestCase):
    """Tests for the ortho module."""
    def setUp(self): 
        if sys.version_info[0]>=3: self.skipTest('This test is for Python 2.')
    @unittest.expectedFailure
    def test_1(self):
        zip(*[(1,2),(3,4)])[0]
        self.assertTrue(isinstance(b'a'.decode(),str))
        self.assertTrue(isinstance(u'a',str))
    def test_2(self): self.assertTrue(b'1'==u'1')
    def test_3(self):
        self.assertTrue(isinstance(u'a',unicode))
        self.assertTrue(type(u'a') in str_types)
        self.assertTrue(type(b'a') in str_types)

class TestOrthoBasicPython3(unittest.TestCase):
    def setUp(self): 
        if sys.version_info[0]<3: self.skipTest('This test is for Python 3.')
    @unittest.expectedFailure
    def test_1(self):
        """ Python 3 syntax examples excluded here or the test will not run.
        #! note that you could put the tests in separate files and rely on the imports to ignore invalid ones
        a,b,*rest = range(10)
        def f(a, b, *args, option=True) # no more accidental argument swallowing
        def extendto(value, *, shorter=None, longer=None) # force kwargs for clarity
        """
        self.assertTrue(b'1'==u'1')
        self.assertTrue(type(b'a') in str_types)
    def test_2(self):
        # note u'a' and 'a' are both str in python 3
        self.assertTrue(isinstance(b'a'.decode(),str))
        self.assertTrue(isinstance(u'a',str))
        self.assertTrue(type(u'a') in str_types)
        self.assertTrue(type(str('a')) in str_types)

### ORTHO TESTS

class TestOrthoBasic(unittest.TestCase):
    """Tests for the ortho module."""
    # tests are ordered by line number via caseFactory/suiteFactory in unittester.py which runs this
    def test_make(self):
        """Make a blank config and ensure that it matches bootstrap and also test bootstrap."""
        self.assertFalse(os.path.isfile(config_fn))
        ortho.bash('make')
        self.conf_start = ortho.read_config() #! ignore this
        bootstrap = {}
        exec(open('bootstrap.py','r').read(),bootstrap,bootstrap)
        self.assertIn('default_configuration',bootstrap)
        default_conf = bootstrap.get('default_configuration',{})
        self.assertTrue(self.conf_start==default_conf)
        self.assertIn('bootstrap_default',bootstrap)
    def test_config_view(self):
        """Print the configuration."""
        ortho.bash('make config text=True')
    def test_env_list(self):
        """Simply print the environment list."""
        ortho.bash('make env list text=True')
    # set, set_dict, setlist, unset
    def test_add_command(self):
        """Add a command."""
        test_fn = 'test_commands.py'
        self.assertFalse(os.path.isfile(test_fn))
        with open(test_fn,'w') as fp: fp.write(dummy_function)
        ortho.bash('make setlist commands %s'%test_fn)
        conf = ortho.read_config() #! ignore this
        self.assertTrue(test_fn in conf.get('commands',[]))
        result = ortho.bash('make dummy',scroll=False)
        # best to use bytes in patterns from now one
        self.assertIsNotNone(re.search(b'special code',result.get('stdout')))
        os.remove(test_fn)
    @unittest.expectedFailure
    def test_compatibility_python2(self):
        if sys.version_info[0]>=3: raise Exception
        zip(*[(1,2),(3,4)])[0]
    def tearDown(self):
        """Clean up tests, on failure."""
        test_fn = 'test_commands.py'
        if os.path.isfile(test_fn): os.remove(test_fn)

### SPECIAL TESTS MAKE NEW ENVIRONMENTS

class SpecialTestOrthoBasic(unittest.TestCase):
    """Tests for the ortho module."""
    # tests are ordered by line number via caseFactory/suiteFactory in unittester.py which runs this
    # note that the ...??? how to programatically make tests

    def setUp(self): self.check_miniconda()

    def check_miniconda(self):
        if not os.path.isfile('miniconda.sh'):
            # raise exception during setUp rather than using the hackish KeyboardInterrupt in a test
            raise Exception('cannot find a local copy of miniconda.sh. link it here to complete the tests')

    @classmethod
    def prepare_environs(self):
        """Prepare the environment list."""
        # control the available environments, otherwise set in environments.py
        conf = ortho.read_config()
        from ortho.environments import default_envs
        conf['envs'] = default_envs
        # make sure we have an installer and a requirements in each environment
        for env_name,this in conf['envs'].items():
            missing_keys = [k for k in ['installer','reqs'] 
                if k not in this.get('sources',[])]
            if any(missing_keys): raise Exception('environment %s is missing sources: %s'%(
                env_name,missing_keys))
        ortho.write_config(conf)
        ortho.bash('make env list text=True')

    @classmethod
    def _generate_programmatic_tests(self):
        """Special function noticed by suiteFactory to programatically add tests."""
        # since we need to generate programmatic tests, we also run the typical setUp here as well
        # ensure that we have a config.json
        ortho.bash('make')
        # make sure the config.json has the environments
        self.prepare_environs()
        # setUp is done here
        # get the configuration and prepare unit tests for each environment
        conf = ortho.read_config()
        for env_name,detail in conf.get('envs',{}).items():
            def this_test(self):
                # note that you don't get variables from parent scope without refering to them (obv)
                env_shortname = detail['name']
                # rather than expecting a reqs.yaml, we use a single reqs_basic for all environment tests
                #! should the requirements vary by environment in the test? real use-cases may differ
                req_file = tempfile.NamedTemporaryFile(delete=False,suffix='json')
                req_file.write(json.dumps(reqs_basic))
                req_file.close()
                # replace requirements. note that we check for installer and reqs above
                conf['envs'][env_name]['sources']['reqs'] = req_file.name
                custom_spot = tempfile.mkdtemp(prefix='env_%s_'%env_name,dir='.')
                conf['envs'][env_name]['where'] = custom_spot
                # use the update flag to install in a preexisting temporary directory
                conf['envs'][env_name]['update'] = True
                ortho.write_config(conf)
                ortho.bash('make env %s'%env_name)
                ortho.bash('make set activate_env="%s %s"'%(os.path.join(custom_spot,
                    'bin','activate'),env_shortname))
                # conda is quirky. it does not appear in the path but runs after you source the env 
                # ... (possibly alias?) hence we have to use an absolute path to conda and also source 
                # ... the environment to check it we check on conda by using activate_env to ensure that 
                # ... this test is true-to-use
                test_fn = 'test_commands.py'
                #! this is conda specific. the whole test should be conda specific!
                with open(test_fn,'w') as fp: fp.write(re.sub('WHERE_CONDA',
                    os.path.join(custom_spot,'bin','conda'),dummy_function_conda_list))
                ortho.bash('make setlist commands %s'%test_fn)
                # note ortho.bash fails to find conda in the conda_list dummy function
                # note also that `result = ortho.bash('./env/bin/conda list')` does not source the 
                # ... right environment
                result = ortho.bash('make conda_list',scroll=False)
                # or `result = ortho.bash('source env/bin/activate py2 && ./env/bin/conda list',scroll=False)`
                # check for some packages in reqs.yaml
                reqs = reqs_basic['dependencies']
                for key in reqs: self.assertIsNotNone(re.search(key,result.get('stdout')))
                # clean up the test commands. note that config.json is replaced by the unittester
                os.remove(test_fn)
                return
            # attach the tests to the class
            func_name = str('test_environ_%s'%env_name)
            this_test.__name__ = func_name
            setattr(self,this_test.__name__,this_test)
