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
passldap = commands.getoutput("slappasswd -v -h {md5} -s "+userpass+"")
#Creamos la contraseña aleatoria para la utilizacion de ftp
genpassftp = ""
genpassftp = genpassftp.join([choice(valores) for i in range(8)])

#Creamos la contraseña aleatoria para la utilizacion de mysql
genpassdb = ""
genpassdb = genpassdb.join([choice(valores) for i in range(8)])

#Buscamos el uidmax para el alta del nuevo usuario:
uidmax = commands.getoutput("cat /home/tuhosting.com/numusuarios.txt")
uid = int(uidmax)+1
os.system("echo "+str(uid)+" > /home/tuhosting.com/numusuarios.txt")

#Buscamos el usuario y nombre de dominio
busquedausuario = commands.getoutput("ldapsearch -Y EXTERNAL -H ldapi:/// -Q -D 'cn=admin,dc=tuhosting,dc=com' -b 'ou=People,dc=tuhosting,dc=com' 'uid="+usuario+"' | grep numEntries:")
busquedadominio = commands.getoutput("ldapsearch -Y EXTERNAL -H ldapi:/// -Q -D 'cn=admin,dc=tuhosting,dc=com' -b 'dc=tuhosting,dc=com' 'o="+dominio+"' | grep numEntries:")

if busquedausuario == "# numEntries: 1" and busquedadominio == "#numEntries: 1":
	print "El usuario y el dominio introducidos ya existen"
	exit()
elif busquedausuario != "# numEntries: 1 " and busquedadominio == "# numEntries: 1":
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
	crearusuario = open('usuario.ldif','w')
	contenido_plantilla = contenido_plantilla.replace('[[nombreusuario]]', usuario)
	contenido_plantilla = contenido_plantilla.replace('[[nombredominio]]', dominio)
	contenido_plantilla = contenido_plantilla.replace('[[uidnumber]]', uidmax)
	contenido_plantilla = contenido_plantilla.replace('[[password]]', passldap)
	crearusuario.write(contenido_plantilla)
	crearusuario.close()
#Añadimos a ldap el fichero ldif con los datos del nuevo usuario y dominio:
	os.system('ldapadd -x -D "cn=admin,dc=tuhosting,dc=com" -wroot -f  usuario.ldif')
#Creamos el directorio personal del usuario y le asignamos los permisos correspondientes
	print "Creando directorio personal..."
	os.system("mkdir /home/tuhosting.com/"+usuario+" ; cp /etc/skel/.* /home/tuhosting.com/"+usuario+"/ ; chown -R "+uidmax+":2001 /home/tuhosting.com/"+usuario+"")
#Asignamos la cuota de 100 MB al usuario
	print "Asignando cuota de espacio"
	os.system("quotatool -u "+usuario+" -bq 90M -l '100 Mb' /home/tuhosting.com")
#Introducimos la plantilla web en el directorio del usuario:
	os.system("cp -d  plantillas/cyanspark/* /home/tuhosting.com/"+usuario+"/")
	plantilla_web=open("/home/tuhosting.com/"+usuario+"/index.html","r")
	contenido_plantillaweb= plantilla_web.read()
	plantilla_web.close()
	crearindex = open("/home/tuhosting.com/"+usuario+"/index.html","w")
	contenido_plantillaweb = contenido_plantillaweb.replace('[[nombredominio]]', dominio)
	crearindex.write(contenido_plantillaweb)
	crearindex.close()
#Creamos el nuevo virtual host utilizando la plantilla.
	print "Añadiendo el nuevo dominio al servidor web"
	os.system ("cd /etc/apache2/sites-available/")
	os.system("touch "+dominio+".conf")
	plantilla_vhost=open('plantillas/virtualhost.conf','r')
	contenido_plantillavhost= plantilla_vhost.read()
	plantilla_vhost.close()
	crearvhost = open("/etc/apache2/sites-available/"+dominio+".conf","w")
	contenido_plantillavhost = contenido_plantillavhost.replace('[[nombreusuario]]', usuario)
	contenido_plantillavhost = contenido_plantillavhost.replace('[[nombredominio]]', dominio)
	crearvhost.write(contenido_plantillavhost)
	crearvhost.close()
	os.system("a2ensite "+dominio+".conf > /dev/null")
	
#Creamos el nuevo usuario virtual para la gestión del ftp, lo almacenamos en uan base de datos.
	crearusuarioftp = "INSERT INTO `ftpuser` (`id`, `userid`, `passwd`, `uid`, `gid`, `homedir`, `shell`, `count`, `accessed`, `modified`) VALUES ('', '"+usuario+"_ftp', ENCRYPT('"+genpassftp+"'), 2005, 2005, 'home/tuhosting.com/"+usuario+"/', '/sbin/nologin', 0, '', ''); "
	os.system("mysql -uroot -proot -e "+crearusuarioftp+"")
	print("El usuario y contraseña para la administración ftp son:")
	print("Usuario : "+usuario+"_ftp")
	print("Contraseña: "+genpassftp+"")
#Creamos un nuevo usuario y una nueva base de datos para el usuario.
	acciones = ["create user 'my"+usuario+"'@'localhost' identified by '"+genpassdb+"'","create database "+usuario+"","grant all privileges on "+usuario+".* to 'my"+usuario+"'@'localhost'", "flush privileges"]
	for i in acciones:
		os.system('mysql -u root -proot -e "'+i+'"')
		
	print("El usuario y contraseña para la administración de la base de datos son:")
	print("Usuario : my"+usuario+"")
	print("Contraseña: "+genpassdb+"")
#Definimos el nombre de dominio para la resolución dns.
	zonadominio= 'zone "'+dominio+'" {\n	type master;\n	file "db.'+dominio+'";\n };\n'
	ficheroconf = open("/etc/bind/named.conf.local","a")
	ficheroconf.write(zonadominio)
	ficheroconf.close()#Creamos la zona de resolución directa:
	print "Creando zona de resolución directa..."
	plantilla_directa=open('plantillas/directa.conf','r')
	contenido_plantilladirecta= plantilla_directa.read()
	plantilla_directa.close()
	os.system("touch /var/cache/bind/db."+dominio+"")
	os.system("chown bind:bind -R /var/cache/bind/*")
	os.system("chmod 660 -R /var/cache/bind/*")
	creardirecta = open('/var/cache/bind/db.'+dominio+'','w')
	contenido_plantilladirecta = contenido_plantilladirecta.replace('[[nombredominio]]', dominio)
	creardirecta.write(contenido_plantilladirecta)
	creardirecta.close()

os.system("service apache2 reload")
os.system("service proftpd reload")
os.system("service bind9 reload")
