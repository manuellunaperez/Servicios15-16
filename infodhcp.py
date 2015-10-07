#coding: utf-8
import sys
import commands

parametro=sys.argv[1]

if (parametro) == "-l":
	print "Concesiones realizadas por el servidor dhcp:"
	print "--------------------------------------------"
	concesiones = commands.getoutput ("cat /var/lib//dhcp/dhcpd.leases |grep lease.*.*{ |sort |uniq")
	concesiones = concesiones.replace ("lease", "");
	concesiones = concesiones.replace ("{", "");
 	print concesiones
 	print "--------------------------------------------"
 	
 	
 	
	
	
	
