# coding: latin-1

###########################################################################
#    SBW - Sharada-Braille-Writer
#    Copyright (C) 2012-2013 Nalin.x.Linux GPL-3
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
import os
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib

data_dir = "/usr/share/pyshared/sbw";

class writer():
	def __init__ (self):
		self.letter = {}
		self.guibuilder = Gtk.Builder()
		self.guibuilder.add_from_file("%s/ui/ui.glade" %(data_dir))
		self.window = self.guibuilder.get_object("window")
		self.textview = self.guibuilder.get_object("textview")
		self.label = self.guibuilder.get_object("label")
		self.language_menu = self.guibuilder.get_object("menuitem_Language")
		self.textbuffer = self.guibuilder.get_object("textbuffer")
		
		
		#self.guibuilder.connect_signals(self);
		
		
		# braille letters
		self.pressed_keys = "";
		
		#Key code map
		self.keycode_map = {41:"f",40:"d",39:"s",44:"j",45:"k",46:"l"}
		
		#Grabing focus
		self.textview.grab_focus();
		
		
		# Setting language menu items
		menu_languages = Gtk.Menu()
		for line in open("%s/data/languages.txt" % data_dir,'r'):
			menuitem = Gtk.MenuItem()
			menuitem.set_label(line[:-1])
			menuitem.connect("activate",self.load_language);
			menu_languages.append(menuitem);
		self.language_menu.set_submenu(menu_languages);
		
		
		
		#Braille Iter
		self.braille_iter = 0;
		
		#self.window.maximize();
		self.textview.show_all();
		self.window.show_all();
		Gtk.main();
		self.load_map("english");
		
		
	def key_pressed(self,widget,event):
		self.pressed_keys  += self.keycode_map[event.hardware_keycode];
		self.braille_iter = len(self.pressed_keys); 

	def key_released(self,widget,data=None):
		if (self.braille_iter == 1):
			print ("Finding %s"%self.pressed_keys);
			self.pressed_keys = "";
		elif (self.braille_iter < 0):
			self.braille_iter = 1;
		self.braille_iter -= 1;
		

	
	def load_language(self,widget):
		self.load_map(widget.get_label())
		
	def load_map(self,language):
		print ("loading Map for language : %s" %language)
		self.map = {}
		submap_number = 1;
		self.append_sub_map(language,"beginning.txt",submap_number);
		submap_number = 2;
		self.append_sub_map(language,"middle.txt",submap_number);
		
		for text_file in os.listdir("%s/data/%s/"%(data_dir,language)):
			if text_file not in ["beginning.txt","middle.txt"]:
				submap_number += 1;
				self.append_sub_map(language,text_file,submap_number);		
		

	
	def append_sub_map(self,language,filename,submap_number):
		print("Loading sub map file for : %s with sn : %d " % (filename,submap_number))
		
		for line in open("%s/data/%s/%s"%(data_dir,language,filename),"r"):
			if (line.split(" ")[0]) in self.map.keys():
				self.map[line.split(" ")[0]].append(line.split(" ")[1][:-1])
				if len(self.map[line.split(" ")[0]]) != submap_number:
					print("Repeated on : ",line.split(" ")[0])
			else:
				list=[];
				for i in range (1,submap_number):
					list.append(" ");
				list.append(line.split(" ")[1][:-1]);
				self.map[line.split(" ")[0]] = list;
		
		for key in self.map.keys():
			if len(self.map[key]) < submap_number:
				self.map[key].append(" ");
				 
				
			
		
		

		
if __name__ == "__main__":
	writer()
	
