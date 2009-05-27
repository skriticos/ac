# 2.5
from __future__ import with_statement

import os, getopt, sys
import ConfigParser

import plistlib

# AniChou
import globs

def usage(prog):
    """
    Print command line help.
    
    Takes an application name to display.
    """
    # Won't strip indentation.
    print """
    Usage: %s [options]

    Options:
      --version       show program's version number and exit
      -h, --help      show this help message and exit
      -d, --no-gui    disable GUI
      -t, --tracker   enable play-tracker
      -c <file>       use an alternative configuration file
      -r              overwrite config with default values

    Developers only:
      -a              disable login and site updates
      -f <file>       load XML from file instead of the server

    """ % prog

def options(prog, version, argv):
    """
    Return options found in argv.
    
    prog will be to usage() when --help is requested.
    
    version will be printed for --version.
    
    The first items of argv must be an option, not the executable name like
    in sys.argv!
    
    The result has the format {section: {option: value}}
    """
    # For getopt we have to mention each option several times in the code,
    # unlike with the optparse module. But then that's more readable.
    # Also optparse doesn't keep information on which options where
    # actually given on the command line versus the hard-coded defaults.
    try:
        opts, args = getopt.getopt(argv, "hdtc:arf:", ["version", "help",
            "no-gui", "tracker", "config=", "anonymous", "reset"])
    except getopt.GetoptError, err:
        print str(err)
        usage(prog)
        sys.exit(2)
    given = {}
    for o, a in opts:
        if o == "--version":
            print prog, version
            sys.exit()
        elif o in ("-h", "--help"):
            usage(prog)
            sys.exit()
        elif o in ("-d", "--no-gui"):
            given.setdefault("startup", {})["gui"] = False
        elif o in ("-t", "--tracker"):
            given.setdefault("startup", {})["tracker"] = True
        elif o == "-c":
            given.setdefault(None, {})["config"] = a
        elif o == "-a":
            given.setdefault("mal", {})["login"] = False
        elif o == "-r":
            given.setdefault(None, {})["reset"] = True
        elif o == "-f":
            given.setdefault("mal", {})["mirror"] = a
        else:
            assert False, "getopt knew more than if"
    return given

class DefaultConfig(ConfigParser.ConfigParser):
    """
    Knows the content for a fresh configuration file.
    """
    def __init__(self):
        ConfigParser.ConfigParser.__init__(self)
        # ConfigParser cannot handle options without a section.
        ac = dict(
            mal = dict(
                username = '',
                password = ''
                ),
            startup = dict(
                sync = 'False',
                tracker = 'False'
                ),
            search_dir = dict(
                dir1 = os.path.expanduser('~')
                )
            )

        for s, oo in ac.iteritems():
            self.add_section(s)
            for o, v in oo.iteritems():
                self.set(s, o, v)

    def valid(self):
        """
        Returns false if too few, too many, or the wrong sections are present.
        """
        # Doesn't matter whether frozen or not.
        ac = frozenset(['mal', 'startup', 'search_dir'])
        me = frozenset(self.sections())
        return me == ac

class Section(object):
    """
    Magic for convenient attribute syntax.
    
    Potentially makes debugging harder.
    """
    def __init__(self, parser, section):
        """
        Takes an instance that responds to parse.get(section, name) and
        parser.set(section, name, value) which will be called for self.name
        """
        self._parser = parser
        self._section = section

    def __setattr__(self, name, value):
        if name[0] == '_':
            object.__setattr__(self, name, value)
        else:
            self._parser.set(self._section, name, value)
            
    def __getattr__(self, name):
        # In contrast to setattr we are only called when no regular
        # attribute is found.
        assert name[0] != '_'
        return self._parser.get(self._section, name)

class ac_config(object):
    """
    Interface to our configuration system.
    """
    def __init__(self):
        """
        Takes no arguments, always interprets sys.argv and
        globs.ac_config_path
        
        Multiple instances will therefore return identical information.
        """
        prog = os.path.basename(sys.argv[0])
        self.override = options(prog, globs.ac_version, sys.argv[1:])
        # Local shortcut.
        self.config = ini = DefaultConfig()
        cfg = self.get(None, 'config')
        if not self.get(None, 'reset'):
            ini.read(cfg)
        # This allows files that do not contain all required sections.
        if not ini.valid():
            # Never destroy user's data without asking.
            # Better do this in the GUI.
            sys.exit("Unknown sections in %s\nDelete or use -r" % cfg)
        with open(cfg, 'wb') as f:
            ini.write(f)

    def __getattr__(self, name):
        """
        Syntax sugar allowing self.section.option = value
        
        Either this or get/set should be the canonical interface. Only the
        latter supports arguments.
        """
        # Wastefully creating a new object every time.
        return Section(self, name)

    def get(self, section, name, stored = False):
        """
        Return a configuration option in the correct type.
        
        The same option given on the command line overrides the configuration
        file. If you need the real values for a preferences dialog, pass
        positional stored = True.
        
        When the option isn't found absolutely anywhere, raises KeyError.
        """
        # We have to hard-code defaults here because options() must be
        # faithful to the command line to allow overriding.
        defaults = dict(
            startup = dict(gui = True),
            mal = dict(login = True),
            )
        try:
            if not stored:
                return self.override[section][name]
        except KeyError:
            pass
        if section == 'startup' and name in ('tracker', 'sync'):
            # Automatic type conversion.
            # Thanks to the defaults this should never raise.
            return self.config.getboolean(section, name)
        elif section is None:
            # Defaults for command line options that were not given.
            return dict(config = globs.ac_config_path, reset = False)[name]
        try:
            return self.config.get(section, name)
        except ConfigParser.NoOptionError:
            return defaults[section][name]
        
    def set(self, section, name, value):
        """
        Set a configuration option.
        
        This overrides the command line override, so subsequent retrieval of
        an option will yield the new value.
        """
        try:
            del self.override[section][name]
        except KeyError:
            pass
        # Convert booleans.
        self.config.set(section, name, unicode(value))

    def save(self):
        """
        Write the current configuration, sans any remaining command line
        overrides, to disk.
        """
        with open(self.get(None, 'config'), 'wb') as f:
            self.config.write(f)

if __name__ == '__main__':

    para = ac_config()

    # Test every parameter allowed for get()
    ac = dict(
        mal = dict(
            username = 0,
            password = 0,
            login = 0
            ),
        startup = dict(
            sync = 0,
            tracker = 0,
            gui = 0
            ),
        search_dir = dict(
            dir1 = 0
            ),
        )
    ac[None] = dict(config = 0, reset = 0)

    for s, oo in ac.iteritems():
        for o in oo.keys():
            print o, para.get(s, o)
            if s is not None:
                # Test magic.
                print o, getattr(getattr(para, s), o)
