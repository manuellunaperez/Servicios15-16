# -*- coding: utf-8 -*-
import sys
import os
import string
from random import choice
import crypt
import commands
import MySQLdb

dominio = sys.argv[1]


#Buscamos el usuario y nombre de dominio
busquedadominio = commands.getoutput("ldapsearch -Y EXTERNAL -H ldapi:/// -Q -D 'cn=admin,dc=tuhosting,dc=com' -b 'dc=tuhosting,dc=com' 'o="+dominio+"' | grep numEntries:")

if  busquedadominio != "# numEntries: 1":
	print "El dominio no se encuentra"
	exit()
else:
	print "Borrando dominio"
	usuario = commands.getoutput("ldapsearch -Y EXTERNAL -H ldapi:/// -Q -D 'cn=admin,dc=tuhosting,dc=com' -b 'dc=tuhosting,dc=com' 'o="+dominio+"' | grep description: | sed -e 's,description: ,,'")
#Borramos usuario y dominio de ldap 	
	os.system('ldapdelete -x -D "cn=admin,dc=tuhosting,dc=com" -wroot "o='+dominio+',dc=tuhosting,dc=com"')
	os.system('ldapdelete -x -D "cn=admin,dc=tuhosting,dc=com" -wroot "uid='+usuario+',ou=People,dc=tuhosting,dc=com"')
	os.system('ldapdelete -x -D "cn=admin,dc=tuhosting,dc=com" -wroot "cn='+usuario+',ou=Group,dc=tuhosting,dc=com"')
#Borramos el directorio personal del usuario
	print "Borrando directorio personal..."
	os.system("rm -fr /home/tuhosting.com/"+usuario+"/")
	

#Borramos el nuevo virtual host.
	print "Borrando virtual host"
	os.system("cd /etc/apache2/sites-enabled/")
	os.system("a2dissite "+dominio+".conf > /dev/null")
	os.system("rm /etc/apache2/sites-available/"+dominio+".conf")
	
	
	print "Borrando virtual host phpmyadmin"
	os.system("cd /etc/apache2/sites-enabled/")
	os.system("a2dissite "+dominio+"db.conf > /dev/null")
	os.system("rm /etc/apache2/sites-available/"+dominio+"db.conf")
#Creamos un nuevo usuario y una nueva base de datos para el usuario.
	acciones = ["drop user 'my"+usuario+"'@'localhost'","drop database "+usuario+""]
	for i in acciones:
		os.system('mysql -u root -proot -e "'+i+'"')
		
	print("El usuario para la administración de la base de datos ha sido borrado")
	
#Definimos el nombre de dominio para la resolución dns.
	numdominio = commands.getoutput('cat /etc/bind/named.conf.local |grep -n "^zone.*.'+dominio+'"')
	linea = numdominio.split(":")
	lineas = int(linea[0])+3
	print "Borrando zona de resolución directa..."
	os.system("sed -i '"+str(linea[0])+","+str(lineas)+"d' /etc/bind/named.conf.local")
	os.system('rm /var/cache/bind/db.'+dominio+'')

os.system("service apache2 reload")
os.system("service proftpd reload")
os.system("service bind9 reload")
