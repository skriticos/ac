'''
	This is a player detection module for animecollector.
'''

import Queue
import time
import os
import subprocess

class detectPlayers:

    system = None

    def __init__( self, debug ):
        self.system = os.name

        self.debug = debug

    def check( self ):
        if self.system == "posix":
            ps = subprocess.Popen( "ps -C mplayer -o args=", shell=True, stdout=subprocess.PIPE )

            paths = [ match.split() for match in ps.communicate()[ 0 ].split( "\n" ) ]

            for path in paths:
                if len( path ):
                    print path[ -1 ]

        return True
