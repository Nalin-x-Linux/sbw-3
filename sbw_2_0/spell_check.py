import enchant
import inspect
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango


#Where the data is located
data_dir = "/usr/share/pyshared/sbw_2_0";



def log(function):
	def loged_function(*args):
		print("Entering : ",function.__name__,args);
		f = function(*args)
		print("Leaving  : ",function.__name__);
		return f
	return loged_function


def decallmethods(decrator):
	def decrated_class(cls):
		for name, m in inspect.getmembers(cls, inspect.isfunction):
			setattr(cls,name,decrator(m))
		return cls
	return decrated_class


# CHECK SPELLING
@decallmethods(log)		
class Spell_Check:
	def __init__ (self,textview,textbuffer,language,enchant_language):
		self.textbuffer = textbuffer;
		self.textview = textview;
		
		#Loading Dict
		try:
			self.dict = enchant.Dict(enchant_language)
		except:
			dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR,Gtk.ButtonsType.CANCEL, "Dict not found!")
			dialog.format_secondary_text("Please install the aspell dict for your language({0})".format(enchant_language))
			dialog.run()
			dialog.destroy()
			return
			
		
		#Builder And Gui
		builder = Gtk.Builder()
		builder.add_from_file("%s/ui/Spell.glade" % (data_dir))
		self.spell_window = builder.get_object("window")
		builder.connect_signals(self)
		self.entry = builder.get_object("entry")
		self.context_label = builder.get_object("label_context")
		

		self.liststore = Gtk.ListStore(str)
		self.treeview = builder.get_object("treeview")
		self.treeview.connect("row-activated",self.activate_treeview)
		
		self.treeview.set_model(self.liststore)
		column = Gtk.TreeViewColumn("Suggestions : ")
		self.treeview.append_column(column)		
		cell = Gtk.CellRendererText()
		column.pack_start(cell, False)
		column.add_attribute(cell, "text", 0)
				
		#user dict for change all
		self.user_dict={}
		
		#Tag for misspelled
		size = self.textview.get_style().font_desc.get_size()/Pango.SCALE
		desc = self.textview.get_style().font_desc
		desc.set_size((size+size/2)*Pango.SCALE)
		self.tag = self.textbuffer.create_tag(font = desc)
		
		#get the current cursor position 
		mark = self.textbuffer.get_insert()
		pos = self.textbuffer.get_iter_at_mark(mark)
		
		#move the pos to end of the near word
		pos.backward_word_start()
		pos.forward_word_end()
		
		#get the position of last word end
		last_word_end = self.textbuffer.get_end_iter();
		last_word_end.backward_word_start()
		last_word_end.forward_word_end()
		 
		if (pos.equal(last_word_end)):
			#start the spell-check from begining if pos and last-word-end are same
			self.word_start = self.textbuffer.get_start_iter();
		else:
			self.word_start = pos.copy();
			self.word_start.backward_word_start()
						
		
		self.find_next_miss_spelled()
		self.spell_window.show()


	def activate_treeview(self,widget, row, col):
		model = widget.get_model()
		text = model[row][0]
		self.entry.set_text(text)
		self.entry.grab_focus()  
	
	def close(self,widget,data=None):
		start,end = self.textbuffer.get_bounds()
		self.textbuffer.remove_all_tags(start,end)
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
	
	def delete(self,data=None):
		self.textbuffer.delete(self.word_start, self.word_end)
		self.find_next_miss_spelled()	

	def find_next_miss_spelled(self):
		if (self.move_iters_to_next_misspelled()):
			start,end = self.textbuffer.get_bounds()
			self.textbuffer.remove_all_tags(start,end)
			self.textbuffer.apply_tag(self.tag,self.word_start,self.word_end)
			self.textview.scroll_to_iter(self.word_start, 0.2, use_align=False, xalign=0.5, yalign=0.5)
			
			self.entry.set_text("")
			self.word = self.textbuffer.get_text(self.word_start,self.word_end,False)		
			start=self.word_start.copy()
			start.backward_sentence_start()
			end=self.word_start.copy()
			end.forward_sentence_end()
			sentence = self.textbuffer.get_text(start,end,True)			

			context = "Misspelled word {0} : -  {1}".format(self.word,sentence)
			self.context_label.set_text(context)
			self.entry.set_text(self.word)
			
			self.liststore.clear()
			for item in self.dict.suggest(self.word):
				self.liststore.append([item])
			self.entry.grab_focus()
			return True
		else:
			self.spell_window.destroy()
			start,end = self.textbuffer.get_bounds()
			self.textbuffer.remove_all_tags(start,end)
			return False	
	

	def move_iters_to_next_misspelled(self):
		#loop till a misspelled word found
		while(True):
			self.word_end = self.word_start.copy()
			self.word_end.forward_word_end()
				
			self.word = self.textbuffer.get_text(self.word_start,self.word_end,False)			
			
			#check only non empty word
			if (len(self.word) > 1):
				if (self.dict.check(self.word) == False):
					if (self.word in self.user_dict.keys()):
						self.textbuffer.delete(self.word_start, self.word_end)
						self.textbuffer.insert(self.word_start,self.user_dict[self.word])
					else:
						return True
				
			#check for the end reached
			last_word_end = self.textbuffer.get_end_iter();
			last_word_end.backward_word_start()
			last_word_end.forward_word_end()	
			if (self.word_end.equal(last_word_end)):
				return False
			
			#move to next word
			self.word_start.forward_word_ends(2)
			self.word_start.backward_word_starts(1)
