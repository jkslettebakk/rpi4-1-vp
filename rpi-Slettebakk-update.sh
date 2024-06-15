#
#
# Update routine for Raspberry Pi computers i slettebakk.com
#
sudo apt dist-upgrade
#
sudo apt install
#
sudo apt clean
#
# update and clean up in one shell command
#
sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y && sudo apt clean -y && sudo apt autoclean -y
sudo apt update
#
# This could be better?
# Samba
sudo apt install samba samba-common-bin
