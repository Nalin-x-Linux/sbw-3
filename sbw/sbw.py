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
from gi.repository import Pango

import configparser
from subprocess import getoutput
from threading import Thread
import enchant

#Where the data is located
data_dir = "/usr/share/pyshared/sbw";

#Changing directory to Home folder
home_dir = os.environ['HOME']


class writer():
	def __init__ (self,filename=None):
		self.letter = {}
		self.guibuilder = Gtk.Builder()
		self.guibuilder.add_from_file("%s/ui/ui.glade" %(data_dir))
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
		for line in open("%s/data/languages.txt" % data_dir,'r'):
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
		if config.read('%s/.sbw.cfg'%home_dir) != []:
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
			self.simple_mode = 0
			self.auto_new_line = 0;
		
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
					self.label.set_text("%s deleted" % self.textbuffer.get_text(start,end,True));
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
						self.label.set_text("new line %d" % (iter.get_line()+1));
					else:
						#Line limit info
						iter = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());	
						if (iter.get_chars_in_line() >= self.line_limit):
							if (self.auto_new_line):
								self.textbuffer.insert_at_cursor("\n");
								self.label.set_text("new line");
							else:
								self.label.set_text("Limit exceeded %s" % iter.get_chars_in_line());
					
				
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
					self.label.set_text("Tab at %s" % iter.get_line_offset());					
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
		self.label.set_text("%s loded" % self.language);
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
		for text_file in os.listdir("%s/data/%s/"%(data_dir,self.language)):
			if text_file not in ["beginning.txt","middle.txt","abbreviations.txt","abbreviations_default.txt","punctuations.txt","help.txt"]:
				if "~" not in text_file:
					submap_number += 1;
					self.append_sub_map(text_file,submap_number);
					self.contractions_dict[text_file[:-4]] = submap_number-1;
		#Load abbreviations if exist
		self.load_abbrivation();
		


	
	def append_sub_map(self,filename,submap_number):
		print("Loading sub map file for : %s with sn : %d " % (filename,submap_number))	
		for line in open("%s/data/%s/%s"%(data_dir,self.language,filename),"r"):
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
			for line in open("%s/data/%s/abbreviations.txt"%(data_dir,self.language),"r"):
				self.abbreviations[line.split("  ")[0]] = line.split("  ")[1][:-1]
		except FileNotFoundError:
			pass
					
	def copy(self,wedget,data=None):
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.textbuffer.copy_clipboard(self.clipboard)
	def cut(self,wedget,data=None):
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.textbuffer.cut_clipboard(self.clipboard, True)
	def paste(self,wedget,data=None):
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.textbuffer.paste_clipboard(self.clipboard, None, True)
	def delete(self,wedget,data=None):
		self.backspace(1);

	def backspace(self,move):
		if (self.textbuffer.get_has_selection()):
			self.textbuffer.delete_selection(True,True)
		else:
			iter = self.textbuffer.get_iter_at_mark(self.textbuffer.get_insert());
			start = iter.copy()
			if(move == 1 and not iter.is_end()):
				iter.forward_char()
				self.label.set_text("%s at %d deleted" % (self.textbuffer.get_text(start,iter,True),iter.get_line_offset() ));
				self.textbuffer.backspace(iter,True,True);
			elif(move == -1):
				start.backward_char();
				self.label.set_text("%s at %d deleted" % (self.textbuffer.get_text(start,iter,True),iter.get_line_offset() ));
				self.textbuffer.backspace(iter,True,True);
			
							
	
	def go_to_line(self,wedget,data=None):
		insert_mark = self.textbuffer.get_insert()
		offset = self.textbuffer.get_iter_at_mark(insert_mark)
		line = offset.get_line()
		maximum = self.textbuffer.get_line_count() 
		adj = Gtk.Adjustment(value=1, lower=1, upper=maximum, step_incr=1, page_incr=5, page_size=0)
		self.spinbutton_line.set_adjustment(adj)
		self.spinbutton_line.set_value(line)		
		self.spinbutton_line.show()
		self.spinbutton_label.show()
		self.spinbutton_label.set_mnemonic_widget(self.spinbutton_line)
		self.spinbutton_line.connect("activate",self.go_to_line_function)
		self.spinbutton_line.grab_focus()

	def go_to_line_function(self,data=None):
		self.spinbutton_line.hide()
		self.spinbutton_label.hide()
		to = self.spinbutton_line.get_value_as_int()
		iter = self.textbuffer.get_iter_at_line(to)	
		self.textbuffer.place_cursor(iter)
		self.textview.scroll_to_iter(iter, 0.0,False,0.0,0.0)

	
	def new(self,wedget,data=None):
		if (self.textbuffer.get_modified() == True):
			dialog =  Gtk.Dialog("Start new without saving ?",self.window,True,
			("Save", Gtk.ResponseType.ACCEPT, "Cancel" ,Gtk.ResponseType.CLOSE, "Start-New!", Gtk.ResponseType.REJECT))                           						

			label = Gtk.Label("Start new without saving ?")
			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()

			response = dialog.run()
			dialog.destroy()				
			
			if response == Gtk.ResponseType.REJECT:
				start, end = self.textbuffer.get_bounds()
				self.textbuffer.delete(start, end)
				del self.save_file_name													
			elif response == Gtk.ResponseType.ACCEPT:
				if (self.save(self)):
					start, end = self.textbuffer.get_bounds()
					self.textbuffer.delete(start, end)
					del self.save_file_name
		else:
			start, end = self.textbuffer.get_bounds()
			self.textbuffer.delete(start, end)
		self.textview.grab_focus();

	def open(self,wedget,data=None):
		open_file = Gtk.FileChooserDialog("Select the file to open",None,Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		open_file.set_current_folder("%s"%(os.environ['HOME']))
		response = open_file.run()
		if response == Gtk.ResponseType.OK:
			to_read = open("%s" % (open_file.get_filename()))
			to_open = to_read.read()
			try:
				self.textbuffer.set_text(to_open)
			except FileNotFoundError:
					pass
			else:
				self.save_file_name = open_file.get_filename()
				self.textbuffer.place_cursor(self.textbuffer.get_end_iter())
		open_file.destroy()


	def save(self,wedget,data=None):
		start,end = self.textbuffer.get_bounds()
		text = self.textbuffer.get_text(start,end,False)
		try:
			self.save_file_name
		except AttributeError:
			save_file = Gtk.FileChooserDialog("Save ",None,Gtk.FileChooserAction.SAVE,
		                    buttons=(Gtk.STOCK_SAVE,Gtk.ResponseType.OK))    
			save_file.set_current_folder("%s"%(os.environ['HOME']))
			save_file.set_current_name(text[0:10]);
			save_file.set_do_overwrite_confirmation(True);
			filter = Gtk.FileFilter()
			filter.add_pattern("*.txt")
			filter.add_pattern("*.text")
			save_file.add_filter(filter)
			response = save_file.run()
			if response == Gtk.ResponseType.OK:
				self.save_file_name = "%s"%(save_file.get_filename())
				open("%s" %(self.save_file_name),'w').write(text)
				self.label.set_text("Text saved to %s" % self.save_file_name);
				self.textbuffer.set_modified(False)	
				save_file.destroy()
				return True
			else:
				save_file.destroy()
				return False
		else:
			open("%s" %(self.save_file_name),'w').write(text)
			self.label.set_text("Text saved to %s" % self.save_file_name);	
			self.textbuffer.set_modified(False)
			return True		

	def save_as(self,wedget,data=None):
		del self.save_file_name
		self.save(self);
		
	def quit(self,wedget,data=None):
		config = configparser.ConfigParser()
		if (config.read('%s/.sbw.cfg' % home_dir) == []):
			config.add_section('cfg')			
		config.set('cfg', 'font',self.font)
		config.set('cfg', 'font_color',self.font_color)
		config.set('cfg', 'background_color',self.background_color)			
		config.set('cfg', 'line_limit',str(self.line_limit))
		config.set('cfg', 'simple_mode',str(self.simple_mode))
		config.set('cfg', 'auto_new_line',str(self.auto_new_line))
		with open('%s/.sbw.cfg'% home_dir , 'w') as configfile:
			config.write(configfile)
			
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
				if (self.save(self)):
					Gtk.main_quit()
			else:
				return True
		else:
			Gtk.main_quit()

	def readme(self,wedget,data=None):
		try:
			readme_text = open("%s/data/%s/help.txt"%(data_dir,self.language),"r").read()
		except FileNotFoundError:
			pass
		else:
			self.textbuffer.set_text(readme_text)
			start = self.textbuffer.get_start_iter()
			self.textbuffer.place_cursor(start)
			self.textbuffer.set_modified(False)

	def about(self,wedget,data=None):
		guibuilder_about = Gtk.Builder()
		guibuilder_about.add_from_file("%s/ui/about.glade" % (data_dir))
		window_about = guibuilder_about.get_object("aboutdialog")
		guibuilder_about.connect_signals({"about_close" : self.about_close })		
		window_about.show()
	
	def about_close(self,wedget,data=None):
		wedget.destroy()
		
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
		abbreviations = open("%s/data/%s/abbreviations.txt"%(data_dir,self.language),"r")
		self.textbuffer.set_text(abbreviations.read())
		self.textbuffer.place_cursor(self.textbuffer.get_end_iter())
		abbreviations.close()
		self.textbuffer.set_modified(False)
		self.label.set_text("List opened");

	def save_abbreviation(self,widget):
		abbreviations = open("%s/data/%s/abbreviations.txt"%(data_dir,self.language),"w")
		start, end = self.textbuffer.get_bounds()
		text = self.textbuffer.get_text(start, end,False)
		for line in text.split("\n"):
			if (len(line.split("  ")) == 2):
				abbreviations.write("%s\n"%(line))
				#abbreviations.write("%s  %s\n"%(line.split("~")[0],line.split("~")[1]))
		abbreviations.close()
		self.load_abbrivation();
		self.textbuffer.set_modified(False)
		self.label.set_text("Abbreviation saved");

	def restore_abbreviation(self,widget):
		abbreviations = open("%s/data/%s/abbreviations.txt"%(data_dir,self.language),"w")
		abbreviations_default = open("%s/data/%s/abbreviations_default.txt"%(data_dir,self.language),"r")
		abbreviations.write(abbreviations_default.read())
		abbreviations.close()
		abbreviations_default.close()
		self.load_abbrivation();
		self.label.set_text("Abbreviation restored");
	def audio_converter(self,widget):
		try:
			start,end = self.textbuffer.get_selection_bounds()
		except ValueError:
			start,end = self.textbuffer.get_bounds()
		
		text = self.textbuffer.get_text(start,end,False)		
		record(text)
		
	def spell_check(self,widget):
		Spell_Check(self.textview,self.textbuffer,self.language,self.enchant_language)
		

class record:
	def __init__(self,text):
		to_convert = open("temp.txt",'w')
		to_convert.write(text)
		to_convert.close()
		
		builder = Gtk.Builder()
		builder.add_from_file("%s/ui/audio_converter.glade" % (data_dir))
		builder.connect_signals(self)
		self.audio_converter_window = builder.get_object("window")
			
			
			
		self.spinbutton_speed = builder.get_object("spinbutton_speed")
		self.spinbutton_pitch = builder.get_object("spinbutton_pitch")
		self.spinbutton_split = builder.get_object("spinbutton_split")
		self.spinbutton_vloume = builder.get_object("spinbutton_vloume")
		self.spinbutton_speed.set_value(170)
		self.spinbutton_pitch.set_value(50)
		self.spinbutton_split.set_value(5)
		self.spinbutton_vloume.set_value(100)
			
		voice_combo = builder.get_object("combobox_language_convert")
		
		list_store = Gtk.ListStore(str)
		output = getoutput("espeak --voices")
		for line in output.split("\n"):
			list_store.append([line.split()[3]])
		
		voice_combo.set_model(list_store)
		self.model_voice = voice_combo.get_model()
		self.index_voice = voice_combo.get_active()
		
				
		voice_combo.connect('changed', self.change_voice)
		self.audio_converter_window.show()		                

	def change_voice(self, voice):
		self.model_voice = voice.get_model()
		self.index_voice = voice.get_active()
		
	def close_audio_converter(self,widget,data=None):
		self.audio_converter_window.destroy()
		
	def convert_to_audio(self,widget,data=None):
		self.filename = Gtk.FileChooserDialog("Type the output wav name",None,Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,Gtk.STOCK_SAVE, Gtk.ResponseType.OK));
		self.filename.set_current_folder("%s"%(os.environ['HOME']))
		self.filename.run()
		self.file_to_output = self.filename.get_filename()
		self.filename.destroy()
		Thread(target=self.record_to_wave,args=()).start()
		self.audio_converter_window.destroy()

               
		
	def record_to_wave(self):
		os.system('espeak -a %s -v %s -f temp.txt -w %s.wav --split=%s -p %s -s %s' % (self.spinbutton_vloume.get_value(),self.model_voice[self.index_voice][0],self.file_to_output,self.spinbutton_split.get_value(),self.spinbutton_pitch.get_value(),self.spinbutton_speed.get_value()))
		os.system('espeak "Conversion finish and saved to %s"' % (self.file_to_output))





#  FUNCTION TO CHECK SPELLING		
class Spell_Check:
	def __init__ (self,textview,textbuffer,language,enchant_language):
		self.textbuffer = textbuffer;
		self.textview = textview;
		#Loading Dict
		self.dict = enchant.Dict(enchant_language)
		
		#Builder And Gui
		builder = Gtk.Builder()
		builder.add_from_file("%s/ui/Spell.glade" % (data_dir))
		self.spell_window = builder.get_object("window")
		builder.connect_signals(self)
		self.entry = builder.get_object("entry")
		

		self.liststore = Gtk.ListStore(str)
		self.treeview = builder.get_object("treeview")
		self.treeview.connect("row-activated",self.activate_treeview)
		
		self.treeview.set_model(self.liststore)
		column = Gtk.TreeViewColumn("Suggestions : ")
		self.treeview.append_column(column)		
		cell = Gtk.CellRendererText()
		column.pack_start(cell, False)
		column.add_attribute(cell, "text", 0)
				
		self.user_dict={}
		mark = self.textbuffer.get_insert()
		self.word_start = self.textbuffer.get_iter_at_mark(mark)
		
		self.find_next_miss_spelled()
		self.spell_window.show()
			
	
	def activate_treeview(self,widget, row, col):
		model = widget.get_model()
		text = model[row][0]
		self.entry.set_text(text)
		self.entry.grab_focus()  
				
	def close(self,widget,data=None):
		self.spell_window.destroy()	

	def change(self,data=None):
		self.textbuffer.delete(self.word_start, self.word_end)
		self.textbuffer.insert(self.word_start, self.entry.get_text())
		self.find_next_miss_spelled()
		
		
	def change_all(self,data=None):
		self.textbuffer.delete(self.word_start, self.word_end)
		self.textbuffer.insert(self.word_start, self.entry.get_text())
		self.user_dict[self.word] = self.entry.get_text()		
		self.find_next_miss_spelled()

	def ignore(self,data=None):
		self.word_start.forward_word_ends(2)
		self.word_start.backward_word_starts(1)
		self.find_next_miss_spelled()	

	def ignore_all(self,data=None):
		if self.dict.is_added(self.word) == False:
			self.dict.add(self.word)	
		self.find_next_miss_spelled()	

	def find_next_miss_spelled(self):
		if (self.move_iters_to_next_misspelled()):
			self.textbuffer.select_range(self.word_start,self.word_end)
			self.textview.scroll_to_iter(self.word_start, 0.2, use_align=False, xalign=0.5, yalign=0.5)
			
			self.entry.set_text("")
			self.word = self.textbuffer.get_text(self.word_start,self.word_end,False)		
			self.entry.set_text(self.word)
			
			self.liststore.clear()
			for item in self.dict.suggest(self.word):
				self.liststore.append([item])
			self.entry.grab_focus()
			self.textbuffer.select_range(self.word_start,self.word_end)
			return True
		else:
			self.spell_window.destroy()
			return False	
	

	def move_iters_to_next_misspelled(self):
		while(True):
			self.word_end = self.word_start.copy()
			self.word_end.forward_word_end()
				
			self.word = self.textbuffer.get_text(self.word_start,self.word_end,False)			
			try:
				if (self.dict.check(self.word) == False and len(self.word) > 1):
					if (self.word in self.user_dict.keys()):
						self.textbuffer.delete(self.word_start, self.word_end)
						self.textbuffer.insert(self.word_start,self.user_dict[self.word])
					else:
						return True
			except:
				pass
				
			last_word_end = self.textbuffer.get_end_iter();
			last_word_end.backward_word_start()
			last_word_end.forward_word_end()
			
			if (self.word_end.equal(last_word_end)):
				return False
			
			self.word_start.forward_word_ends(2)
			self.word_start.backward_word_starts(1)
		
		



		
if __name__ == "__main__":
	writer()
	
