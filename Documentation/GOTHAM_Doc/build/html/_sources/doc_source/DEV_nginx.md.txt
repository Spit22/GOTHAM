# Installation

Installation en compilant les sources : manière propre + ajouter le paramètre --with-stream lors de la compilation.

On télécharge les sources sur le site officiel de nginx : https://nginx.org/en/download.html

On décompresse le ficher (tar.gz)

Préalable : 
    * installer gcc
    * installer la PCRE (libpcre3 et libpcre3-dev)
    * installer la librairie zlib (zlib1g et zlib1g-dev)

On exécute ./configure avec les arguments pour appliquer la conf pré-compilation (voir les paramètres avec ./configure --help)

Arguments : --with-stream


