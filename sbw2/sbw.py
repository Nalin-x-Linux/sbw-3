###########################################################################
#    SBW - Sharada-Braille-Writer
#    Copyright (C) 2012-2014 Nalin.x.Linux GPL-3
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
import configparser
import re


from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Pango

from sbw2 import converter
from sbw2 import global_var
from sbw2.basic_editor import editor
from sbw2.basic_editor import spell_check
from sbw2.basic_editor import find
from sbw2.basic_editor import find_and_replace

import gettext
_ = gettext.gettext
gettext.textdomain('sbw2')


class writer(editor):
	def __init__ (self,filename=None):
		self.letter = {}
		self.guibuilder = Gtk.Builder()
		self.guibuilder.add_from_file("%s/ui/ui.glade" %(global_var.data_dir))
		self.window = self.guibuilder.get_object("window")
		self.textview = self.guibuilder.get_object("textview")
		self.label = self.guibuilder.get_object("info_label")
		self.language_menu = self.guibuilder.get_object("menuitem_Language")
		self.textbuffer = self.textview.get_buffer();
		self.guibuilder.connect_signals(self);

		#Switching off the event bell
		settings = Gtk.Settings.get_default()
		settings.set_property("gtk-error-bell", False)
				
		# braille letters
		self.pressed_keys = "";
		
		#Key code map
		self.keycode_map = {41:"f",40:"d",39:"s",44:"j",45:"k",46:"l",43:"h",42:"g"}
		
		#Grabing focus
		self.textview.grab_focus();
		
		
		
		# Setting language menu items with keys
		menu_languages = Gtk.Menu()
		accel_group = Gtk.AccelGroup()
		self.window.add_accel_group(accel_group)
		i = 1
		for line in open("%s/data/languages.txt" % global_var.data_dir,'r'):
			menuitem = Gtk.MenuItem()
			menuitem.set_label(line[:-1])
			menuitem.connect("activate",self.load_language);
			key,mods=Gtk.accelerator_parse("F%d" % i)
			if (i < 13):
				menuitem.add_accelerator("activate", accel_group,key, mods, Gtk.AccelFlags.VISIBLE)
				i = i + 1
			menu_languages.append(menuitem);
		self.language_menu.set_submenu(menu_languages);
		
		
		#Load the first language by default
		self.load_map("english en")
		
		#Braille Iter's
		self.braille_iter = 0;
		self.braille_letter_map_pos = 0;
		
		
		#capital switch
		self.capital_switch = 0;
		
		self.spinbutton_line = self.guibuilder.get_object("spinbutton_line")
		self.spinbutton_label = self.guibuilder.get_object("spinbutton_label")
		self.spinbutton_line.hide()
		self.spinbutton_label.hide()
		
		#User Preferences
		config = configparser.ConfigParser()
		if config.read('%s/.sbw_2_0.cfg'%global_var.home_dir) != []:
			self.font = config.get('cfg','font')
			self.font_color = config.get('cfg','font_color')
			self.background_color = config.get('cfg','background_color')
			self.line_limit = int(config.get('cfg','line_limit'))
			self.simple_mode = int(config.get('cfg','simple_mode'))
			self.auto_new_line = int(config.get('cfg','auto_new_line'))
		else:
			self.font = 'Georgia 14'
			self.font_color = '#fff'
			self.background_color = '#000'		
			self.line_limit =  100
			self.simple_mode = 1
			self.auto_new_line = 1;
		
		pangoFont = Pango.FontDescription(self.font)
		self.textview.modify_font(pangoFont)
		self.textview.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.font_color))
		self.textview.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.background_color))
					
		self.guibuilder.get_object("fontbutton").set_font_name(self.font)
		self.guibuilder.get_object("colorbutton_font").set_color(Gdk.color_parse(self.font_color))
		self.guibuilder.get_object("colorbutton_background").set_color(Gdk.color_parse(self.background_color))
		self.guibuilder.get_object("spinbutton_line_limit").set_value(self.line_limit)
		self.guibuilder.get_object("checkbutton").set_active(self.simple_mode)
		self.guibuilder.get_object("checkbutton_auto_new_line").set_active(self.auto_new_line)
		
		if (filename):
			 self.textbuffer.set_text(open(filename,"r").read())
			 self.save_file_name = filename
				

		
		self.window.maximize();
		self.textview.show_all();
		self.window.show_all();
		Gtk.main();
		
	def order_pressed_keys(self,pressed_keys):
		ordered = ""
		for key in ["g","f","d","s","h","j","k","l"]:
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
				if ordered_pressed_keys == "gh":
					start = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());
					end = start.copy()
					start.backward_word_start()
					self.label.set_text(_("{} deleted").format(self.textbuffer.get_text(start,end,True)));
					self.textbuffer.delete(start, end)
					
					
				elif ordered_pressed_keys == "h":
					self.backspace(-1);

						
				elif ordered_pressed_keys == "g" and self.language == "english":
					self.capital_switch = 1	
										
				elif ordered_pressed_keys in self.contractions_dict.keys() and not self.simple_mode:
					self.braille_letter_map_pos = self.contractions_dict[ordered_pressed_keys];
					print (self.braille_letter_map_pos);
				else:
					try:
						value = self.map[ordered_pressed_keys][self.braille_letter_map_pos];
					except KeyError:
						value = ""
					
					#Make letter capitol if switch is on 
					if (self.capital_switch):
						value = value.upper();
						self.capital_switch = 0;
						
					self.textbuffer.insert_at_cursor(value);
					self.braille_letter_map_pos = 1;
					if value in ["'","(",'"',"[","{","-"]:
						self.braille_letter_map_pos = 0;
					print ("Map Pos : ",self.braille_letter_map_pos)
					if  (len(value) > 1):
						self.label.set_text(value);
					
			else:
				#Space or enter
				if (event.hardware_keycode in [65,36]):
					self.braille_letter_map_pos = 0;
					self.textbuffer.insert_at_cursor(event.string);
					
					if (event.hardware_keycode == 36):
						iter = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());
						self.label.set_text(_("new line {}").format(iter.get_line()+1));
					else:
						#Line limit info
						iter = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());	
						if (iter.get_chars_in_line() >= self.line_limit):
							if (self.auto_new_line):
								self.textbuffer.insert_at_cursor("\n");
								self.label.set_text(_("new line"));
							else:
								self.label.set_text(_("Limit exceeded {}").format(iter.get_chars_in_line()));
					
				
				# ; for punctuations
				elif (event.hardware_keycode == 47):
					self.braille_letter_map_pos = 2;
				
				#Backspace
				elif (event.hardware_keycode == 22 or event.hardware_keycode == 43):
					self.backspace(-1)
				
				# substitute abbriviation 
				elif (event.hardware_keycode == 38 and not self.simple_mode):
					iter = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());
					start = iter.copy();
					start.backward_word_start()
					last_word = self.textbuffer.get_text(start,iter,False)
					if (last_word in self.abbreviations.keys()):
						self.textbuffer.delete(start,iter);
						self.textbuffer.insert_at_cursor(self.abbreviations[last_word]);
						self.label.set_text("%s" % self.abbreviations[last_word]);				
				elif (event.hardware_keycode == 49):
					self.textbuffer.insert_at_cursor('\t');
					iter = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());
					self.label.set_text(_("Tab at {}").format(iter.get_line_offset()));					
				elif (event.hardware_keycode == 64):
					self.braille_letter_map_pos = 0;
				elif (event.hardware_keycode == 108):
					self.braille_letter_map_pos = 1;					
				else:
					print (event.hardware_keycode);
					
				
			
			self.pressed_keys = "";
		
		elif (self.braille_iter < 0):
			self.braille_iter = 1;
		self.braille_iter -= 1;
	
	def load_language(self,widget):
		self.load_map(widget.get_label())
		
	def load_map(self,language_with_code):
		self.language = language_with_code.split()[0]
		self.label.set_text(_("{} loaded").format(self.language));
		self.enchant_language = language_with_code.split()[1]
		print ("loading Map for language : %s" %self.language)
		self.map = {}
		submap_number = 1;
		self.append_sub_map("beginning.txt",submap_number);
		submap_number = 2;
		self.append_sub_map("middle.txt",submap_number);
		submap_number = 3;
		self.append_sub_map("punctuations.txt",submap_number);
		
		#Contraction dict 
		self.contractions_dict = {};
		
		#load each contractions to map
		for text_file in os.listdir("%s/data/%s/"%(global_var.data_dir,self.language)):
			if text_file not in ["beginning.txt","middle.txt","abbreviations.txt","abbreviations_default.txt","punctuations.txt","help.txt"]:
				if "~" not in text_file:
					submap_number += 1;
					self.append_sub_map(text_file,submap_number);
					self.contractions_dict[text_file[:-4]] = submap_number-1;
		#Load abbreviations if exist
		self.load_abbrivation();
		


	
	def append_sub_map(self,filename,submap_number):
		print("Loading sub map file for : %s with sn : %d " % (filename,submap_number))	
		for line in open("%s/data/%s/%s"%(global_var.data_dir,self.language,filename),"r",encoding='utf-8'):
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
				 
	def load_abbrivation(self):
		self.abbreviations = {}
		try:
			for line in open("%s/data/%s/abbreviations.txt"%(global_var.data_dir,self.language),"r"):
				self.abbreviations[line.split("  ")[0]] = line.split("  ")[1][:-1]
		except FileNotFoundError:
			pass
					
	def delete(self,wedget,data=None):
		self.backspace(1);

	def backspace(self,move):
		if (self.textbuffer.get_has_selection()):
			self.textbuffer.delete_selection(True,True)
			self.label.set_text(_("Selection Deleted"));
		else:
			iter = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());
			start = iter.copy()
			if(move == 1 and not iter.is_end()):
				iter.forward_char()
				self.label.set_text(_("{} at {} deleted").format(self.textbuffer.get_text(start,iter,True),iter.get_line_offset() ));
				self.textbuffer.backspace(iter,True,True);
			elif(move == -1):
				start.backward_char();
				self.label.set_text(_("{} at {} deleted").format(self.textbuffer.get_text(start,iter,True),iter.get_line_offset() ));
				self.textbuffer.backspace(iter,True,True);

		
	def font_set(self,widget):
		self.font = widget.get_font_name();
		pangoFont = Pango.FontDescription(self.font)
		self.textview.modify_font(pangoFont)

	def font_color_set(self,widget):
		self.font_color = widget.get_color().to_string()
		self.textview.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.font_color))

	def background_color_set(self,widget):
		self.background_color = widget.get_color().to_string()
		self.textview.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse(self.background_color))

	def line_limit_set(self,widget):
		self.line_limit = widget.get_value_as_int()
	
	def simple_mode_checkbutton_toggled(self,widget):
		self.simple_mode = int(widget.get_active())
	def checkbutton_auto_new_line_toggled(self,widget):
		self.auto_new_line = int(widget.get_active());
				
	def open_abbreviation(self,widget):
		abbreviations = open("%s/data/%s/abbreviations.txt"%(global_var.data_dir,self.language),"r")
		self.textbuffer.set_text(abbreviations.read())
		self.textbuffer.place_cursor(self.textbuffer.get_end_iter())
		abbreviations.close()
		self.textbuffer.set_modified(False)
		self.label.set_text(_("List opened"));

	def save_abbreviation(self,widget):
		abbreviations = open("%s/data/%s/abbreviations.txt"%(global_var.data_dir,self.language),"w")
		start, end = self.textbuffer.get_bounds()
		text = self.textbuffer.get_text(start, end,False)
		text = text.replace("\r","\n")
		for line in text.split("\n"):
			if (len(line.split("  ")) == 2):
				abbreviations.write("%s\n"%(line))
				#abbreviations.write("%s  %s\n"%(line.split("~")[0],line.split("~")[1]))
		abbreviations.close()
		self.load_abbrivation();
		self.textbuffer.set_modified(False)
		self.label.set_text(_("Abbreviation saved"));

	def restore_abbreviation(self,widget):
		abbreviations = open("%s/data/%s/abbreviations.txt"%(global_var.data_dir,self.language),"w")
		abbreviations_default = open("%s/data/%s/abbreviations_default.txt"%(global_var.data_dir,self.language),"r")
		abbreviations.write(abbreviations_default.read())
		abbreviations.close()
		abbreviations_default.close()
		self.load_abbrivation();
		self.label.set_text(_("Abbreviation restored"));

	def expand_short_hand(self,widget):
		try:
			start,end = self.textbuffer.get_selection_bounds()
		except ValueError:
			start,end = self.textbuffer.get_bounds()
		
		text = self.textbuffer.get_text(start,end,False)
		self.textbuffer.delete(start,end);
		
		for key in self.abbreviations.keys():
			if key in text.split():
				text = re.sub("(?<![\w\d])"+key+"(?![\w\d])",self.abbreviations[key],text)
		self.textbuffer.insert(start,text)

	def readme(self,wedget,data=None):
		with open("{0}/data/%s/help.txt".format(global_var.data_dir,self.language)) as file:
			self.textbuffer.set_text(file.read())
			start = self.textbuffer.get_start_iter()
			self.textbuffer.place_cursor(start)
			self.textbuffer.set_modified(False)

	def about(self,wedget,data=None):
		guibuilder_about = Gtk.Builder()
		guibuilder_about.add_from_file("%s/ui/about.glade" % (global_var.data_dir))
		window_about = guibuilder_about.get_object("aboutdialog")
		window_about.show()

	def audio_converter(self,widget):
		try:
			start,end = self.textbuffer.get_selection_bounds()
		except ValueError:
			start,end = self.textbuffer.get_bounds()
		
		text = self.textbuffer.get_text(start,end,False)		
		converter.record(text)
		
	def spell_check(self,widget):
		spell_check(self.textview,self.textbuffer,self.language,self.enchant_language)

	def find(self,widget):
		find(self.textview,self.textbuffer,self.language).window.show()
	def find_and_replace(self,widget):
		find_and_replace(self.textview,self.textbuffer,self.language).window.show()				

	def quit_with_saving_preferences(self,data,widget=None):
		config = configparser.ConfigParser()
		if (config.read('%s/.sbw_2_0.cfg' % global_var.home_dir) == []):
			config.add_section('cfg')			
		config.set('cfg', 'font',self.font)
		config.set('cfg', 'font_color',self.font_color)
		config.set('cfg', 'background_color',self.background_color)			
		config.set('cfg', 'line_limit',str(self.line_limit))
		config.set('cfg', 'simple_mode',str(self.simple_mode))
		config.set('cfg', 'auto_new_line',str(self.auto_new_line))
		with open('%s/.sbw_2_0.cfg'% global_var.home_dir , 'w') as configfile:
			config.write(configfile)
		self.quit(self,widget)
		
if __name__ == "__main__":
	writer()
	
