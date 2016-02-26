# -*- coding: utf-8 -*-
import sys
import os
import string
from random import choice
import crypt
	
usuario = sys.argv[1]
dominio = sys.argv[2]

plantilla_usuario=open('plantillas/usuario.ldif','r')
contenido_plantilla= plantilla_usuario.read()
plantilla_usuario.close()
crearusuario= open('usuario.ldif','w')
contenido_plantilla = contenido_plantilla.replace('[[nombreusuario]]', usuario)
contenido_plantilla = contenido_plantilla.replace('[[nombredominio]]', dominio)
crearusuario.write(contenido_plantilla)
crearusuario.close()
