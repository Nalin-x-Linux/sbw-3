# coding: latin-1

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
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Gio
from gi.repository import GLib
from gi.repository import Pango

from sbw_2_0 import global_var

class editor():
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
			("Save", Gtk.ResponseType.ACCEPT,"Start-New!", Gtk.ResponseType.REJECT))                           						

			label = Gtk.Label("Start new without saving ?")
			box = dialog.get_content_area();
			box.add(label)
			dialog.show_all()

			response = dialog.run()
			dialog.destroy()				
			if response == Gtk.ResponseType.ACCEPT:
				self.save(self)
		start, end = self.textbuffer.get_bounds()
		self.textbuffer.delete(start, end)
		self.textview.grab_focus();
		self.label.set_text("New");

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
	def append(self,wedget,data=None):
		append_file_dialog = Gtk.FileChooserDialog("Select the file to append",None,Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		append_file_dialog.set_current_folder("%s"%(os.environ['HOME']))
		append_file_dialog.run()
		with open(append_file_dialog.get_filename()) as file:
			text_to_append = file.read()
			end = self.textbuffer.get_end_iter()
			self.textbuffer.insert(end,text_to_append)
		append_file_dialog.destroy()
	
	def punch(self,wedget,data=None):
		insert_at_cursor_dialog = Gtk.FileChooserDialog("Select the file to insert at cursor",None,Gtk.FileChooserAction.OPEN,buttons=(Gtk.STOCK_OPEN,Gtk.ResponseType.OK))
		insert_at_cursor_dialog.set_current_folder("%s"%(os.environ['HOME']))
		insert_at_cursor_dialog.run()
		with open(insert_at_cursor_dialog.get_filename()) as file:
			text_to_insert_at_cursor = file.read()
			self.textbuffer.insert_at_cursor(text_to_insert_at_cursor)
		insert_at_cursor_dialog.destroy()

	def quit(self,wedget,data=None):
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


	def copy(self,wedget,data=None):
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.textbuffer.copy_clipboard(self.clipboard)
	def cut(self,wedget,data=None):
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.textbuffer.cut_clipboard(self.clipboard, True)
	def paste(self,wedget,data=None):
		self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
		self.textbuffer.paste_clipboard(self.clipboard, None, True)
		
class find():
	def __init__ (self,textview,textbuffer,language,glade_file="find"):
		self.textbuffer = textbuffer;
		self.textview = textview;
				
		mark = self.textbuffer.get_insert()
		self.iter = self.textbuffer.get_iter_at_mark(mark)
		self.match_start = self.iter.copy()
		self.match_start.backward_word_start()
		self.match_end = self.iter.copy()
		self.match_end.forward_word_end()
		
		
		self.tag = self.textbuffer.create_tag(foreground = "Blue")


		#Builder And Gui
		self.builder = Gtk.Builder()
		self.builder.add_from_file("{0}/ui/{1}.glade".format(global_var.data_dir,glade_file))
		self.window = self.builder.get_object("window")
		self.builder.connect_signals(self)
		self.entry = self.builder.get_object("entry_word")
		self.context_label = self.builder.get_object("context_label")
		
				

	def close(self,widget,data=None):
		start,end = self.textbuffer.get_bounds()
		self.textbuffer.remove_all_tags(start,end)
		self.window.destroy()	

	def correct_context(self,text):
		"""cut the line if it is too lengthy (more than 10 words)
		without rearranging existing lines. This will avoid the resizing of spell window"""
		new_text = ""
		for line in text.split('\n'):
			if (len(line.split(' ')) > 10):
				new_line = ""
				pos = 1
				for word in line.split(" "):
					new_line += word
					pos += 1
					if (pos % 10 == 0):
						new_line += '\n'
					else:
						new_line += ' '

				new_text += new_line
				if (pos % 10 > 3):
					new_text += '\n'
			else:
				new_text += line + '\n'
		return new_text
	
	def find_next(self,widget,data=None):
		self.find(True)

	def find_previous(self,widget,data=None):
		self.find(False)		
		
	def find(self,data):
		word = self.entry.get_text()
		start , end = self.textbuffer.get_bounds()
		if (data == True):
			self.match_start.forward_word_end()
			results = self.match_start.forward_search(word, 0, end)
		else:
			self.match_end.backward_word_start()
			results = self.match_end.backward_search(word, 0,start)
		
		if results:
			self.textbuffer.remove_all_tags(start,end)
			self.match_start, self.match_end = results
			self.textbuffer.place_cursor(self.match_start)
			self.textbuffer.apply_tag(self.tag,self.match_start, self.match_end)
			self.textview.scroll_to_iter(self.match_start, 0.2, use_align=False, xalign=0.5, yalign=0.5)
			sentence_start=self.match_start.copy()
			sentence_start.backward_sentence_start()
			sentence_end=self.match_start.copy()
			sentence_end.forward_sentence_end()
			sentence = self.textbuffer.get_text(sentence_start,sentence_end,True)
			self.context_label.set_text(self.correct_context(sentence))
		else:
			self.context_label.set_text("Word {0} Not found".format(word))
			

class find_and_replace(find):
	def __init__(self,textview,textbuffer,language,glade_file="find_and_replace"):
		find.__init__(self,textview,textbuffer,language,glade_file="find_and_replace")
		self.replace_entry = self.builder.get_object("entry_replace_word")
		
	def replace(self,widget,data=None):
		replace_word = self.replace_entry.get_text()
		self.textbuffer.delete(self.match_start, self.match_end)
		self.textbuffer.insert(self.match_end,replace_word)
		self.match_start = self.match_end.copy()
		self.find(True)
	
	def replace_all(self,widget,data=None):
		word = self.entry.get_text()
		replace_word = self.replace_entry.get_text()
		end = self.textbuffer.get_end_iter()
		while(True):
			self.match_start.forward_word_end()
			results = self.match_start.forward_search(word, 0, end)
			if results:
				self.match_start, self.match_end = results
				self.textbuffer.delete(self.match_start, self.match_end)
				self.textbuffer.insert(self.match_end,replace_word)
				self.match_start = self.match_end.copy()
			else:
				break
