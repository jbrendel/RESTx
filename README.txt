RESTx
=====
The fastest way to create RESTful resourcs.

This is an open source project I worked on for a company a few years ago. The
original repository has been taken down, so I created a new repository with a
copy of the code. Unfortunately, the development history is now lost.

Please see the old project home page with lots of information here:

    https://web.archive.org/web/20130127154128/http://restx.mulesoft.org/

Please see 'CONTRIBUTORS.txt' to see who helped.

Please see 'INSTALL.txt' for installation instructions.

Please see 'LICENSE.txt' for the GPLv3 license text.

Once you have started the server, it will listen on localhost:8001.


Demo
----
RESTx comes with a built in guided tour and demo.

This demo utilizes an sqlite database for some chapters. Please download the
sqlite JDBC driver from http://www.zentus.com/sqlitejdbc/ 
(http://files.zentus.com/sqlitejdbc/sqlitejdbc-v056.jar).
Copy the JAR file in the RESTx/lib folder. Copy the file 'test.db' (to be found
in the RESTx directory) to /var/tmp. Then restart the server.

You can get a guided tour of the server by visiting
http://localhost:8001/static/demo/start.html


Files
-----

You can see the following files and directories:

install.sh      The installation script for Linux/Unix. It performs necessary
                sanity checks on the environment, installs Jython if necessary
                and constructs various helper scripts.

restxctl        The main control script for RESTx. Built during the install.
                Used to start/stop the server, create and install new
                components, and so on.

conf/           Contains the doc string for the server as well as the version
                number.

bin/            Contains most of the helper scripts, which are created during
                the install.

lib/            Location for JAR files.

languages/      Contains language specific component templats and tools.

src/            Contains the source code

src/python      Contains the Python code (this includes some test utilities).
                The restx/ directory there contains most of the code.
                starter.py and restxjson.py are the exception.

src/java        Contains the Java code.

src/javascript  Contains the JavaScript code.

src/python/starter.py  The start script for the RESTx server. No need to call
                it directly. The restxctl script performs all the necessary
                steps for you.

src/python/restx/settings.py  A settings file in which values like the port or
                document root can be set.

static_files/   The directory from where the RESTx server can serve static
                files.

resourceDB/     This is where the RESTx server stores resource definitions.

storageDB/      This is where the file-storage facility for components stores
                its files.

tools/          Holds a few third party sources we are bundling to reduce
                dependencies during install.

test.db         A small sqlite database, which is used in the demo.


