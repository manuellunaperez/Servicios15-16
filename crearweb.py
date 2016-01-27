# -*- coding: utf-8 -*-
import sys
import os
from random import choice


	
departamento = sys.argv[1]

os.system("mkdir /var/www/html/departamentos ; mkdir /var/www/html/departamentos/"+departamento+"")
os.system("chown -R www-data:www-data /var/www/html/departamentos/"+departamento+"")

vhadd= ["	Alias /"+departamento+" /var/www/html/iesgn/departamentos/"+departamento+"\n",
		"	<Directory> /var/www/html/iesgn/departamentos/"+departamento+">\n",
		"		Options Indexes SymLinksIfOwnerMatch\n",
		"		Require all granted\n",
		"	</Directory>\n",
		"</VirtualHost>\n"]
os.system("sed -i '$d' /etc/apache2/sites-available/iesgn.conf") #Borramos la ultima linea del fichero que será </VirtualHost> 
virtualhosts = open('/etc/apache2/sites-availables/iesgn.conf' ,"a") #Añadimos la configuración del nuevo departamento
virtualhosts.writelines(vhadd)
virtualhosts.close()
os.system("service apache2 restart")

#Creamos un usuario con una contraseña aleatorio para la utilización de ftp
valores = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
userpass = ""
userpass = userpass.join([choice(valores) for i in range(8)])
os.system("useradd admin"+departamento" -p "+userpass+"")
print("El usuario y contraseña para la administración ftp son:")
print("Usuario: "+departamento+"")
print("Contraseña: "+userpass+"")
