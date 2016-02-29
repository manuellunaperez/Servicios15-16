# -*- coding: utf-8 -*-
import sys
import os
import string
from random import choice
import crypt
import commands

usuario = sys.argv[1]
dominio = sys.argv[2]

#Generar contraseña ldap
#Creamos una contraseña aleatoria para la utilización de ldap
valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
userpass = ""
userpass = userpass.join([choice(valores) for i in range(8)])
passldap = commands.getoutput("slappasswd -v -h {md5} -s "+userpass+""
#Creamos la contraseña aleatoria para la utilizacion de ftp
genpassftp = ""
genpassftp = genpassftp.join([choice(valores) for i in range(8)])
passftp = crypt.crypt(genpassftp, valores)

#Buscamos el uidmax para el alta del nuevo usuario:
uidmax = commands.getoutput("cat /home/tuhosintg.com/numusuarios.txt")
uidmax = uidmax+1
os.system("echo "+uidmax+" > /home/tuhosting.com/numusuarios.txt")

#Buscamos el usuario y nombre de dominio
busquedausuario = commands.getoutput("ldapsearch -Y EXTERNAL -H ldapi:/// -Q -D 'cn=admin,dc=tuhosting,dc=com' -b 'ou=People,dc=tuhosting,dc=com' 'uid="+usuario"' | grep numEntries:")
busquedadominio = commands.getoutput("ldapsearch -Y EXTERNAL -H ldapi:/// -Q -D 'cn=admin,dc=tuhosting,dc=com' -b 'dc=tuhosting,dc=com' 'o="+dominio+"' | grep numEntries:")

if busquedausuario == "# numEntries: 1" and busquedadominio == "#numEntries: 1":
	print "El usuario y el dominio introducidos ya existen"
	exit()
elif busquedausuario != "#numEntries: 1 " and busquedadominio == "# numEntries: 1" 
	print "El dominio ya está siendo utilizado por otro usuario";
	exit()
elif busquedausuario == "# numEntries: 1" and busquedadominio != "#numEntries: 1":
	print "Este usuario ya está siendo utilizado"
	print "Puedes crear el nombre de dominio dando de alta otro usuario"
	exit()
else:
	print "Usuario y nombre de dominio disponibles"
	print "Creando usuario..."
	
	#Utilizamos la plantilla para generar un nuevo archivo ldif con los datos del nuevo usuario y dominio
	plantilla_usuario=open('plantillas/usuario.ldif','r')
	contenido_plantilla= plantilla_usuario.read()
	plantilla_usuario.close()
	crearusuario= open('usuario.ldif','w')
	contenido_plantilla = contenido_plantilla.replace('[[nombreusuario]]', usuario)
	contenido_plantilla = contenido_plantilla.replace('[[nombredominio]]', dominio)
	contenido_plantilla = contenido_plantilla.replace('[[uidnumber]]', uidmax)
	contenido_plantilla = contenido_plantilla.replace('[[password]]', passldap)
	crearusuario.write(contenido_plantilla)
	crearusuario.close()
	#Añadimos a ldap el fichero ldif con los datos del nuevo usuario y dominio:
	os.system('ldapadd -Y EXTERNAL -H ldapi:/// -Q -D "cn=admin,dc=tuhosting,dc=com" < usuario.ldif')
	#Creamos el directorio personal del usuario y le asignamos los permisos correspondientes
	os.system("mkdir /home/tuhosting.com/"+usuario+" ; cp /etc/skel/.* /home/tuhosting.com/"+usuario+"/ ; chown -R "+uidmax+":2001 /home/tuhosting.com/"+usuario+""
	#Asignamos la cuota de 100 MB al usuario
	os.system("quotatool -u "+usuario+" -bq 90M -l '100 Mb' /home/tuhosting.com"
