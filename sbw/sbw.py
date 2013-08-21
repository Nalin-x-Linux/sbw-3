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
		
		
		self.textbuffer = self.textview.get_buffer();
		self.guibuilder.connect_signals(self);
		self.textbuffer.insert_at_cursor("This is a sample of text");
		
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
		
		
		#Load the english map by default
		self.load_map("english")
		
		#Braille Iter's
		self.braille_iter = 0;
		self.braille_letter_map_pos = 0;
		
		#self.window.maximize();
		self.textview.show_all();
		self.window.show_all();
		Gtk.main();
		
	def order_pressed_keys(self,pressed_keys):
		ordered = ""
		for key in ["f","d","s","j","k","l"]:
			if key in pressed_keys:
				ordered += key;
		return ordered;
			
		
	def key_pressed(self,widget,event):
		if event.hardware_keycode in self.keycode_map.keys():
			self.pressed_keys  += self.keycode_map[event.hardware_keycode];
			self.braille_iter = len(self.pressed_keys);
		else:
			self.braille_iter = 1; 

	def key_released(self,widget,event):
		if (self.braille_iter == 1):
			if self.pressed_keys != "":
				ordered_pressed_keys = self.order_pressed_keys(self.pressed_keys);
				
				if ordered_pressed_keys in self.contractions_dict.keys():
					self.braille_letter_map_pos = self.contractions_dict[ordered_pressed_keys];
					print (self.braille_letter_map_pos);
				else:
					value = self.map[ordered_pressed_keys][self.braille_letter_map_pos];
					self.textbuffer.insert_at_cursor(value);
					print (self.braille_letter_map_pos)
					self.braille_letter_map_pos = 1;
			else:
				#Space or enter
				if (event.hardware_keycode in [65,36]):
					self.braille_letter_map_pos = 0;
					self.textbuffer.insert_at_cursor(event.string);
				
				# ; for punctuations
				elif (event.hardware_keycode == 47):
					self.braille_letter_map_pos = 2;
				
				#Backspace delete or h
				elif (event.hardware_keycode in [22,119,43]):
					if (self.textbuffer.get_has_selection()):
						self.textbuffer.delete_selection(True,True)
					else:
						iter = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());
						if event.hardware_keycode == 119:
							iter.forward_char()
						self.textbuffer.backspace(iter,True,True);
				
				# substitute abbriviation 
				elif (event.hardware_keycode == 38):
					iter = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());
					start = iter.copy();
					start.backward_word_start()
					last_word = self.textbuffer.get_text(start,iter,False)
					if (last_word in self.abbreviations.keys()):
						self.textbuffer.delete(start,iter);
						self.textbuffer.insert_at_cursor(self.abbreviations[last_word]);
						
				
				else:
					print (event.hardware_keycode);
					
				
			
			self.pressed_keys = "";
		
		elif (self.braille_iter < 0):
			self.braille_iter = 1;
		self.braille_iter -= 1;
		

	
	def load_language(self,widget):
		self.load_map(widget.get_label())
		
	def load_map(self,language):
		print ("loading Map for language : %s" %language)
		self.map = {}
		self.abbreviations = {}
		submap_number = 1;
		self.append_sub_map(language,"beginning.txt",submap_number);
		submap_number = 2;
		self.append_sub_map(language,"middle.txt",submap_number);
		submap_number = 3;
		self.append_sub_map(language,"punctuations.txt",submap_number);
		
		#Contraction dict 
		self.contractions_dict = {};
		
		#load each contractions to map
		for text_file in os.listdir("%s/data/%s/"%(data_dir,language)):
			if text_file not in ["beginning.txt","middle.txt","abbreviations.txt","abbreviations_default.txt","punctuations.txt","help.txt"]:
				if "~" not in text_file:
					submap_number += 1;
					self.append_sub_map(language,text_file,submap_number);
					self.contractions_dict[text_file[:-4]] = submap_number-1;
		
		
		#Load abbreviations if exist
		try:
			for line in open("%s/data/%s/abbreviations.txt"%(data_dir,language),"r"):
				self.abbreviations[line.split("  ")[0]] = line.split("  ")[1][:-1]
		except FileNotFoundError:
			pass

	
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
				 

	def quit(self,wedget,data=None):
		if self.textbuffer.get_modified() == True:
			dialog =  Gtk.Dialog(None,self.window,1,
			("Close without saving",Gtk.ResponseType.YES,"Save", Gtk.ResponseType.NO,"Cancel", Gtk.ResponseType.CANCEL))
			
			label = Gtk.Label("Close without saving ?.")
			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()
			
			response = dialog.run()
			dialog.destroy()
			if response == Gtk.ResponseType.YES:
				Gtk.main_quit()			
			elif response == Gtk.ResponseType.NO:
				if (self.on_save_activate(self)):
					Gtk.main_quit()
			else:
				pass
		else:
			Gtk.main_quit()
				
			
		
		

		
if __name__ == "__main__":
	writer()
	
