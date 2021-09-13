Gothamctl configuration
=======================

You can configure your adminsitration tool under $INSTALL_PATH/Gothamctl/Config/config.ini.

The following list cover all sections supported in the configuration file :
  - ``[orchestrator_infos]`` section permits to define where is the GOTHAM api
  - ``[hp_display]`` defines which information has to be shown when displaying honeypot data with gothamctl
  - ``[serv_display]`` defines which information has to be shown when displaying server data with gothamctl
  - ``[link_display]`` defines which information has to be shown when displaying link data with gothamctl

We will detail each sections by showing a configuration template.

orchestrator_infos
------------------

.. code:: bash

  [orchestrator_infos]
  host = "ip or fqdn of gotham api"
  port = "api port"


hp_display
----------

.. code:: bash

  [hp_display]
  default = "TBD"
  normal = "coma-separated list of fields to be shown on normal mode"
  wide = "coma-separated list of fields to be shown on wide mode"
  full = "TBD"


serv_display
------------

.. code:: bash

  [serv_display]
  default = "TBD"
  normal = "coma-separated list of fields to be shown on normal mode"
  wide = "coma-separated list of fields to be shown on wide mode"
  full = "TBD"


link_display
------------

.. code:: bash

  [link_display]
  default = "TBD"
  normal = "coma-separated list of fields to be shown on normal mode"
  wide = "coma-separated list of fields to be shown on wide mode"
  full = "TBD"


