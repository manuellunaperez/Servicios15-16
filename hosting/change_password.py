# -*- coding: utf-8 -*-
import sys
import os
import string
from random import choice
import crypt
import commands
import MySQLdb

usuario = sys.argv[1]
opcion = sys.argv[2]
password = sys.argv[3]	

busquedausuario = commands.getoutput("ldapsearch -Y EXTERNAL -H ldapi:/// -Q -D 'cn=admin,dc=tuhosting,dc=com' -b 'ou=People,dc=tuhosting,dc=com' 'uid="+usuario+"' | grep numEntries:")

if busquedausuario != "# numEntries: 1":
	print "El usuario buscado no ha sido encontrado";
	exit()
else:	
	if opcion == "-ftp":
	#Creamos el nuevo usuario virtual para la gestión del ftp, lo almacenamos en uan base de datos. 
		bd = MySQLdb.connect("localhost","root","root","netftp" )
		cursor = bd.cursor()
		cursor.execute('UPDATE ftpuser SET passwd=ENCRYPT("'+password+'" WHERE  userid="'+usuario+'_ftp";')
		bd.commit()
		bd.close()
		print("Contrseña para usuario ftp cambiada")

	
	
	#Creamos un nuevo usuario y una nueva base de datos para el usuario.

	elif opcion == "-sql":
		bd = MySQLdb.connect("localhost","root","root","mysql" )
		cursor = bd.cursor()
		cursor.execute('UPDATE user SET password=PASSWORD("'+password+'" WHERE  User="my'+usuario+'";')
		bd.commit()
		bd.close()
		print("Contraseña para usuario mysql cambiada")
	else:
		print "Opción no encontrada"
		print "Use -mysql o -ftp"
		exit()
