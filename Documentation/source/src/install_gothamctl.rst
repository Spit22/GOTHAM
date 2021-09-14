**********************
Gothamctl installation
**********************

gothamctl is an easy administration tool for GOTHAM administrators.

It is available on the GOTHAM github repository :

.. code:: bash

  cd $GOTHAM_HOME/Gothamctl/


Then, you can copy this folder on ervery workstations you want (Debian,Ubuntu,Windows,MAC) as it is fully portable. The only requirement is that python3 is installed.

To install gothamctl as system-part command on UNIX-LIKE systems, please do :

.. code:: bash

  ln -s $GOTHAM_HOME/Gothamctl/gothamctl.py /usr/sbin/gothamctl


So you will just have to run 'gothamctl' on your terminal to execute it.

Please note that the configuration file of the tool is under $GOTHAM_HOME/Gothamctl/Config/
