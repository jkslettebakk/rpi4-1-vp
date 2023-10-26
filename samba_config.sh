PINAME=rpi4-1
echo "#======================= Global Settings =======================" > /etc/samba/smb.conf
echo "[global]" >> /etc/samba/smb.conf
echo "workgroup = WORKGROUP" >> /etc/samba/smb.conf
echo "wide links = yes" >> /etc/samba/smb.conf
echo "unix extensions = no" >> /etc/samba/smb.conf


#echo ";server string = " $RPINAME " server" >> /etc/samba/smb.conf
#echo ";netbios name = " $RPINAME >> /etc/samba/smb.conf

echo "dns proxy = no" >> /etc/samba/smb.conf

echo "#### Debugging/Accounting ####" >> /etc/samba/smb.conf
echo "log file = /var/log/samba/log.%m" >> /etc/samba/smb.conf
echo "max log size = 1000" >> /etc/samba/smb.conf
echo "syslog = 0" >> /etc/samba/smb.conf
echo "panic action = /usr/share/samba/panic-action %d" >> /etc/samba/smb.conf

echo "####### Authentication #######" >> /etc/samba/smb.conf
echo "security = user" >> /etc/samba/smb.conf
echo "map to guest = Bad User" >> /etc/samba/smb.conf
echo "guest account = pi" >> /etc/samba/smb.conf

echo "#======================= Share Definitions =======================" >> /etc/samba/smb.conf

echo "[root]" >> /etc/samba/smb.conf
echo "comment = Admin Config Share" >> /etc/samba/smb.conf
echo "path = /" >> /etc/samba/smb.conf
echo "browseable = yes" >> /etc/samba/smb.conf
echo "force user = root" >> /etc/samba/smb.conf
echo "force group = root" >> /etc/samba/smb.conf
echo "admin users = pi" >> /etc/samba/smb.conf
echo "writeable = yes" >> /etc/samba/smb.conf
echo "read only = no" >> /etc/samba/smb.conf
echo "guest ok = yes" >> /etc/samba/smb.conf
echo "create mask = 0777" >> /etc/samba/smb.conf
echo "directory mask = 0777" >> /etc/samba/smb.conf

echo "#-------------------------------------------------------------------" >> /etc/samba/smb.conf

echo "[pi]" >> /etc/samba/smb.conf
echo "comment = pi user /homepi folder" >> /etc/samba/smb.conf
echo "path = /home/pi" >> /etc/samba/smb.conf
echo "browseable = yes" >> /etc/samba/smb.conf
echo "force user = pi" >> /etc/samba/smb.conf
echo "force group = pi" >> /etc/samba/smb.conf
echo "admin users = pi" >> /etc/samba/smb.conf
echo "writeable = yes" >> /etc/samba/smb.conf
echo "read only = no" >> /etc/samba/smb.conf
echo "guest ok = yes" >> /etc/samba/smb.conf
echo "create mask = 0777" >> /etc/samba/smb.conf
echo "directory mask = 0777" >> /etc/samba/smb.conf


sudo samba restart


# time to finish!

echo
echo 
#echo "Have fun with " $RPINAME"
echo
echo "Remember to logon as user=pi password= 'the password you have chosen' your windows machines"
echo
