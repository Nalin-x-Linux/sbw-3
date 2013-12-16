#!/bin/bash

if [ $UID -ne 0 ];
then
echo "Please run this script as root"
exit
fi

echo "Sharada Braille Writer : - SBW is a six key approach to producing
 printmaterials. Letters f, d, s, j, k, l represent 1 2 3 4 5 6 of the
 braille dots respectively. By pressing "f" and "s" together will
 produce letter "k" and like."


echo "Checking and Installing dependencies"
apt-get -qq install python3-gi espeak python3-enchant

<<<<<<< HEAD
echo "============ Checking and removing existing files ================"
if [ -d /usr/share/pyshared/sbw-2.0 ];
then 
rm -rf /usr/share/pyshared/sbw-2.0
echo "Removing existing Data...............Ok"
fi

if [ -d /usr/lib/python3/dist-packages/sbw-2.0 ];
then 
rm -rf /usr/lib/python3/dist-packages/sbw-2.0
=======
#Removing cache files
find -iname *~ -delete

echo "Checking and removing existing files"
if [ -d /usr/share/pyshared/sbw_2_0 ];
then 
rm -rf /usr/share/pyshared/sbw_2_0
echo "Removing existing Data...............Ok"
fi

if [ -d /usr/lib/python3/dist-packages/sbw_2_0 ];
then 
rm -rf /usr/lib/python3/dist-packages/sbw_2_0
>>>>>>> version_independent
echo "Removing existing source.............Ok"
fi


if [ -e /usr/bin/sharada-braille-writer-2.0 ];
then 
rm /usr/bin/sharada-braille-writer-2.0
echo "Removing bin ........................Ok"
fi

if [ -e /usr/share/applications/sharada-braille-writer-2.0.desktop ];
then 
rm /usr/share/applications/sharada-braille-writer-2.0.desktop
echo "Removing icon .......................Ok"
fi

<<<<<<< HEAD
echo "==================== Copying new files ==========================="
echo "Creating sbw folder  ................OK"
mkdir /usr/share/pyshared/sbw-2.0
echo "Copying dara ........................OK"
cp -r data /usr/share/pyshared/sbw-2.0/
echo "Copying ui xml's ....................OK"
cp -r ui /usr/share/pyshared/sbw-2.0/
echo "Copying source files ................OK"
cp -r sbw-2.0 /usr/lib/python3/dist-packages/
=======
echo "Copying new files "
echo "Creating sbw_2_0 folder  ............OK"
mkdir /usr/share/pyshared/sbw_2_0
echo "Copying dara ........................OK"
cp -r data /usr/share/pyshared/sbw_2_0/
echo "Copying ui xml's ....................OK"
cp -r ui /usr/share/pyshared/sbw_2_0/
echo "Copying source files ................OK"
cp -r sbw_2_0 /usr/lib/python3/dist-packages/
>>>>>>> version_independent
echo "Copying starter .....................OK"
cp sharada-braille-writer-2.0 /usr/bin/
echo "Copying icon ........................OK"
cp sharada-braille-writer-2.0.desktop /usr/share/applications/
sudo chmod 755 /usr/share/applications/sharada-braille-writer-2.0.desktop

ldconfig
<<<<<<< HEAD
touch /usr/lib/python3/dist-packages/sbw-2.0/__init__.py
sudo chmod -R 777 /usr/share/pyshared/sbw-2.0/
echo "============ Compleated==========================================="
#sudo -u `whoami` sharada-braille-writer
=======
sudo chmod -R 777 /usr/share/pyshared/sbw_2_0/
sudo update-menus
echo "Compleated"
#sudo -u `whoami` sharada-braille-writer-2.0
>>>>>>> version_independent
