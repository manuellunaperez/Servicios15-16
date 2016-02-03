# -*- coding: utf-8 -*-
import sys
import os
from random import choice
import crypt
	
departamento = sys.argv[1]

#Creamos un usuario con una contraseña aleatorio para la utilización de ftp
valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
userpass = ""
userpass = userpass.join([choice(valores) for i in range(8)])
hashpass = crypt.crypt(userpass, valores)
os.system("useradd admin_"+departamento+" -p"+hashpass+"")
print("El usuario y contraseña para la administración ftp son:")
print("Usuario: admin_"+departamento+"")
print("Contraseña: "+userpass+"")


#Creamos un directorio web para el departamento y le asignamos como propietario el usuario creado
vhadd= ["	Alias /"+departamento+" /var/www/html/iesgn/departamentos/"+departamento+"\n",
		"	<Directory> /var/www/html/iesgn/departamentos/"+departamento+">\n",
		"		Options Indexes SymLinksIfOwnerMatch\n",
		"		Require all granted\n",
		"	</Directory>\n",
		"</VirtualHost>\n"]
os.system("sed -i '$d' /etc/apache2/sites-available/iesgn.conf") #Borramos la ultima linea del fichero que será </VirtualHost> 
virtualhosts = open('/etc/apache2/sites-available/iesgn.conf' ,"a") #Añadimos la configuración del nuevo departamento
virtualhosts.writelines(vhadd)
virtualhosts.close()
os.system("mkdir /var/www/html/iesgn/departamentos/"+departamento+"")
os.system("chown -R admin_"+departamento+":admin_"+departamento+" /var/www/html/iesgn/departamentos/"+departamento+"")
os.system("service apache2 restart")

#Escribimos en el fichero de configuración de proftpd el acceso para el usuario.
addftpconf="DefaultRoot     /var/www/html/iesgn/departamentos/"+departamento+" admin_"+departamento+"\n"
ftpconf = open ("/etc/proftpd/proftpd.conf", "a")
ftpconf.writelines(addftpconf)
ftpconf.close()
os.system("service apache2 reload")
os.system("service proftpd reload")
