xgettext -k_ -L Glade -o po/glade.po share/pyshared/sbw2/ui/*.glade
xgettext -k_ -L Python -o po/source.po sbw2/*.py
sed -i 's/CHARSET/UTF-8/g' po/source.po
msgcat po/source.po po/glade.po -o po/messages.po
rm po/glade.po
rm po/source.po
