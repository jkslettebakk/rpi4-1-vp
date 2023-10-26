#
#
# Update routine for Raspberry Pi computers i slettebakk.com
sudo apt update
#
sudo apt dist-upgrade
#
sudo apt install
#
sudo apt clean
#
# update and clean up in one shell command
#
# sudo apt update -y && sudo apt full-upgrade -y && sudo apt autoremove -y && sudo apt clean -y && sudo apt autoclean -y
#
# This could be better?
sudo apt update -y && sudo apt upgrade -y && sudo apt autoremove -y && sudo apt clean -y && sudo apt autoclean -y
# Samba
sudo apt install samba samba-common-bin
