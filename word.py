# WordPy - An offline wordpress blog tool
# Copyright (C) 2006 Mark Mruss <selsine@gmail.com>
# http://www.learningpython.com
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# If you find any bugs or have any suggestions email: selsine@gmail.com
# URL: http://www.learningpython.com

__author__ = "Mark Mruss <selsine@gmail.com>"
__version__ = "0.1"
__date__ = "Date: 2006/08/20"
__copyright__ = "Copyright (c) 2006 Mark Mruss"
__license__ = "GPL"

#!/usr/bin/env python

import os, sys
try:
 	import pygtk
  	pygtk.require("2.0")
except:
  	pass
try:
	import cPickle
except:
	print "cpickle not found"
	sys.exit(1)
try:
	import gtk
  	import gtk.glade
  	import datetime
  	import xmlrpclib
except:
	sys.exit(1)

try:
	import wordpresslib
except:
	print "wordpresslib required"
	sys.exit(1)

class WordPy:
	"""This is the Wordpy application.  It is a simple PyGTK
	application that interacts with the WorPress Python library."""

	def __init__(self):

		#Set the Glade file
		self.gladefile = "wordpy.glade"
		self.wTree = gtk.glade.XML(self.gladefile, "wndMain")

		"""Create our dictionary and connect it, you may notice
		that I have gone with the default function names this time"""
		dic = {"on_wndMain_destroy" : self.quit
				, "on_btnBold_clicked" : self.on_btnBold_clicked
				, "on_btnItalic_clicked" : self.on_btnItalic_clicked
				, "on_btnLink_clicked" : self.on_btnLink_clicked
				, "on_btnBlockQuote_clicked" : self.on_btnBlockQuote_clicked
				, "on_btnDel_clicked" : self.on_btnDel_clicked
				, "on_btnIns_clicked" : self.on_btnIns_clicked
				, "on_btnImage_clicked" : self.on_btnImage_clicked
				, "on_btnUnorderedList_clicked" : self.on_btnUnorderedList_clicked
				, "on_btnOrderedList_clicked" : self.on_btnOrderedList_clicked
				, "on_btnListItem_clicked" : self.on_btnListItem_clicked
				, "on_btnCode_clicked" : self.on_btnCode_clicked
				, "on_btnMore_clicked" : self.on_btnMore_clicked
				, "on_btnSettings_clicked" : self.on_btnSettings_clicked
				, "on_btnpost_clicked" : self.on_btnpost_clicked}
		self.wTree.signal_autoconnect(dic)
		"""Get the name of the blog data file, sys.path[0] is the
		path where the script is located"""
		self.dat_file = os.path.join(sys.path[0], "Blog.dat")
		self.BlogSettings = WordPressBlogSettings(self.dat_file)
		#Get the Post title
		self.enTitle = self.wTree.get_widget("enTitle")
		#Get the text view
		self.txtPost = self.wTree.get_widget("txtPost")
		#Get the buffer associated with the text view
		self.txtBuffer = self.txtPost.get_buffer()

	def quit(self, widget):
		"""Quit yourself"""
		self.BlogSettings.save(self.dat_file)
		gtk.main_quit()

	def show_error_dlg(self, error_string):
		"""This Function is used to show an error dialog when
		an error occurs.
		error_string - The error string that will be displayed
		on the dialog.
		"""
		error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR
					, message_format=error_string
					, buttons=gtk.BUTTONS_OK)
		error_dlg.run()
		error_dlg.destroy()

	def on_btnBold_clicked(self, widget):
		"""Called when the bold button is clicked"""

		self.wrap_selection("<b>","</b>")

	def on_btnItalic_clicked(self, widget):
		"""Called when the italic button is clicked"""

		self.wrap_selection("<i>","</i>")

	def on_btnLink_clicked(self, widget):
		"""Called when the link button is clicked"""

		#load the dialog from the glade file
		wTree = gtk.glade.XML(self.gladefile, "dlgLink")
		#Get the actual dialog widget
		dlg = wTree.get_widget("dlgLink")
		enURL = wTree.get_widget("enURL")
		enURL.set_text("HTTP://")

		"""Get the selection not and reselect becuase somethimes
		the dialog will remove the selection"""
		start, end = self.get_selection_iters()

		#run the dialog
		if (dlg.run()==gtk.RESPONSE_OK):
			#Reset the selection
			if ((start)and(end)):
				#Select the text
				self.txtBuffer.select_range(end,start)

			#Wrap the selection with the value of the entry fields
			self.wrap_selection("<a href=\"%s\">" % enURL.get_text(),"</a>")

		dlg.destroy()

	def on_btnBlockQuote_clicked(self, widget):
		"""Called when the Block Quote button is clicked"""

		self.wrap_selection("<blockquote>","</blockquote>")

	def on_btnDel_clicked(self, widget):
		"""Called when the Del button is clicked"""

		today = datetime.date.today()
		self.wrap_selection(today.strftime("<del datetime=\"%Y%m%d\">"),"</del>")

	def on_btnIns_clicked(self, widget):
		"""Called when the Ins button is clicked"""

		today = datetime.date.today()
		self.wrap_selection(today.strftime("<ins datetime=\"%Y%m%d\">"),"</ins>")

	def on_btnImage_clicked(self, widget):
		"""Called when the Image button is clicked"""

		#Try to get the wordpress client
		wp = self.BlogSettings.create_wordpress_client()
		if (wp == None):
			#Error creating Client, setting maybe wrong
			self.show_error_dlg("Error creating Worpress client, please check settings.")
			#Now get out of here
			return

		# browse for the image
		image_file = self.browse_for_image()

		if (image_file!=""):
			#We have an image file
			try:
				imageSrc = wp.newMediaObject(image_file)
				if (imageSrc):
					self.insert_text("<img src=\"%s\" />" % imageSrc)
				else:
					self.show_error_dlg("Error uploading image")
			except wordpresslib.WordPressException, e:
				#wordpress lib error
				self.show_error_dlg(
				"Error uploading image:\nError code: %s\nError Message: %s"
				% (e.id, e.message))
			except xmlrpclib.Fault, e:
				self.show_error_dlg(
				"Error uploading image:\nError code: %s\nError Message: %s"
				% (e.faultCode, e.faultString))
			except xmlrpclib.ProtocolError, e:
				self.show_error_dlg(
				"Error uploading image:\nURL: %s\nError code: %s\nError Message: %s"
				% (e.url, e.errcode, e.errmsg))


	def on_btnUnorderedList_clicked(self, widget):
		"""Called when the Unordered List button is clicked"""

		self.wrap_selection("<ul>","</ul>")

	def on_btnOrderedList_clicked(self, widget):
		"""Called when the Ordered List button is clicked"""

		self.wrap_selection("<ol>","</ol>")

	def on_btnListItem_clicked(self, widget):
		"""Called when the List Item button is clicked"""

		self.wrap_selection("<li>","</li>")

	def on_btnMore_clicked(self, widget):
		"""Called when the bold button is clicked"""

		self.insert_text("<!--more-->")

	def on_btnCode_clicked(self, widget):
		"""Called when the Code button is clicked"""

		self.wrap_selection("<code>","</code>")

	def on_btnSettings_clicked(self, widget):
		"""Called when the settings button is clicked.  It will
		show the dlgSettings dialog and let the user set the WordPress
		blog settings."""

		self.show_dlgSettings(self.BlogSettings)

	def on_btnpost_clicked(self, widget):
		"""Called when the post button is clicked, this will
		post the post to the blog."""

		#Try to get the wordpress client
		wp = self.BlogSettings.create_wordpress_client()
		if (wp == None):
			#Error creating Client, setting maybe wrong
			self.show_error_dlg("Error creating Worpress client, please check settings.")
			#Now get out of here
			return

		post = wordpresslib.WordPressPost()
		post.allowPings = True
		post.allowComments = True
		#Title
		post.title = self.enTitle.get_text()
		#Text
		start, end = self.txtBuffer.get_bounds()
		post.description = self.txtBuffer.get_text(start, end)
		#Now post the post!
		try:
				new_post_id = wp.newPost(post, True)
				success_dlg = gtk.MessageDialog(type=gtk.MESSAGE_INFO
					, message_format="Success! Post has been published!"
					, buttons=gtk.BUTTONS_OK)
				success_dlg.run()
				success_dlg.destroy()
		except xmlrpclib.Fault, e:
			self.show_error_dlg(
			"Error publishing post:\nError code: %s\nError Message: %s"
			% (e.faultCode, e.faultString))
		except xmlrpclib.ProtocolError, e:
			self.show_error_dlg(
			"Error publishing post:\nURL: %s\nError code: %s\nError Message: %s"
			% (e.url, e.errcode, e.errmsg))
			#print e.url
			#print e.errcode
			#print e.errmsg
			#print e.headers
		except:
			self.show_error_dlg("Error publishing post.");



	def show_dlgSettings(self, BlogSettings):
		"""This function will show the BlogSettings dialog
		It will return the result code from running the dlg.
		BlogSettings - An instance of WordPressBlogSettings.  Its
		values will only be updated if the user presses the OK button
		returns - The result from running the dlg"""

		#init to cancel
		result = gtk.RESPONSE_CANCEL

		#load the dialog from the glade file
		wTree = gtk.glade.XML(self.gladefile, "dlgSettings")
		#Get the actual dialog widget
		dlg = wTree.get_widget("dlgSettings")
		#Get all of the Entry Widgets and set their text
		enURL = wTree.get_widget("enURL")
		enURL.set_text(BlogSettings.URL)
		enUsername = wTree.get_widget("enUsername")
		enUsername.set_text(BlogSettings.Username)
		enPassword = wTree.get_widget("enPassword")
		enPassword.set_text(BlogSettings.Password)

		#run the dialog and store the response
		result = dlg.run()
		if (result==gtk.RESPONSE_OK):
			#get the value of the entry fields
			BlogSettings.URL = enURL.get_text()
			BlogSettings.Username = enUsername.get_text()
			BlogSettings.Password = enPassword.get_text()

		#we are done with the dialog, destroy it
		dlg.destroy()

		#return the result
		return result

	def browse_for_image(self):
		"""This function is used to browse for an image.
		The path to the image will be returned if the user
		selects one, however a blank string will be returned
		if they cancel or do not select one."""

		file_open = gtk.FileChooserDialog(title="Select Image"
					, action=gtk.FILE_CHOOSER_ACTION_OPEN
					, buttons=(gtk.STOCK_CANCEL
								, gtk.RESPONSE_CANCEL
								, gtk.STOCK_OPEN
								, gtk.RESPONSE_OK))
		"""Create and add the Images filter"""
		filter = gtk.FileFilter()
		filter.set_name("Images")
		filter.add_mime_type("image/png")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/gif")
		filter.add_pattern("*.png")
		filter.add_pattern("*.jpg")
		filter.add_pattern("*.gif")
		file_open.add_filter(filter)
		"""Create and add the 'all files' filter"""
		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		file_open.add_filter(filter)

		"""Init the return value"""
		result = ""
		if file_open.run() == gtk.RESPONSE_OK:
			result = file_open.get_filename()
		file_open.destroy()

		return result

	def get_selection_iters(self):
		"""This function gets the start and end selection
		iters from the text view.  If there is no selection
		the current position of the cursor will be returned.
		Returns - start,end - gtk.TextIter objects"""

		#init
		start = None
		end = None

		#First check to see that the text buffer is valid
		if (not self.txtBuffer):
			self.show_error_dlg("Text buffer not available")
			return start,end

		#Get the selection bounds
		bounds = self.txtBuffer.get_selection_bounds();
		if (bounds):
			#If there is a selection we are done
			start,end = bounds
		else:
			#There is no selection so just get the cursor mark
			cursor_mark = self.txtBuffer.get_insert()
			"""Set start and end to be gtk.TextIter objercts at the
			position of the cursor mark"""
			start = self.txtBuffer.get_iter_at_mark(cursor_mark)
			end = self.txtBuffer.get_iter_at_mark(cursor_mark)

		return start, end

	def insert_text(self, text):
		"""This function inserts text into the text buffer
		self.txtBuffer at the current selection.  If text is
		selected it will be overwritten, otherwise it will simply be
		inserted at the cursor position
		text - The text to be inserted in the buffer
		"""

		start, end = self.get_selection_iters();

		if ((not start)or(not end)):
			self.show_error_dlg("Error inserting text")
			return;

		#Delete the selected text (start and end will be equal after)
		self.txtBuffer.delete(start,end)
		#Save a mark at the start position since after we insert
		#the text start will be invalid
		start_mark = self.txtBuffer.create_mark(None, start, True)
		#Insert, end will be set to the end insert position
		self.txtBuffer.insert(end,text)
		start = self.txtBuffer.get_iter_at_mark(start_mark)
		#select the text, use end as the first param so that
		#it will be the cursor position
		self.txtBuffer.select_range(end,start)
		#delete the start mark
		self.txtBuffer.delete_mark(start_mark)

	def wrap_selection(self, start_tag, end_tag):
		"""This fucntion is used to wrap the currently selected
		text in the gtk.TextView with start_tag and end_tag. If
		there is no selection start_tag and end_tag will be
		inserted at the cursor position
		start_tag - The text that will go at the start of the
		selection.
		end_tag - The text that will go at the end of the
		selection."""

		start, end = self.get_selection_iters();
		if ((not start)or(not end)):
			self.show_error_dlg("Error inserting text")
			return;
		#Create a mark at the start and end
		start_mark = self.txtBuffer.create_mark(None,start, True)
		end_mark = self.txtBuffer.create_mark(None, end, False)
		#Insert the start_tag
		self.txtBuffer.insert(start, start_tag)
		#Get the end iter again
		end = self.txtBuffer.get_iter_at_mark(end_mark)
		#Insert the end tag
		self.txtBuffer.insert(end, end_tag)
		#Get the start and end iters
		start = self.txtBuffer.get_iter_at_mark(start_mark)
		end = self.txtBuffer.get_iter_at_mark(end_mark)
		#Select the text
		self.txtBuffer.select_range(end,start)
		#Delete the gtk.TextMark objects
		self.txtBuffer.delete_mark(start_mark)
		self.txtBuffer.delete_mark(end_mark)

class WordPressBlogSettings:
	"""This class holds the necessary wordpress blog settings
	URL - The URL of the blog
	Username - The username posting
	Password - The password for the username
	"""

	def __init__(self, File="", URL="", Username="", Password=""):

		self.URL = URL
		self.Username = Username
		self.Password = Password
		if (File != ""):
			# Load from file
			try:
				file = open(File, 'rb')
				self.URL = cPickle.load(file)
				self.Username = cPickle.load(file)
				self.Password = cPickle.load(file)
				file.close()
			except:
				return

	def save(self, File):
		"""cPickle the information into the file"""

		try:
			save_file = open(File, 'wb')
			cPickle.dump(self.URL, save_file)
			cPickle.dump(self.Username, save_file)
			cPickle.dump(self.Password, save_file)
			save_file.close()
		except:
			print "Error saving blog settings."

	def create_wordpress_client(self):
		"""Quick helper routine used to create the wordpress
		client"""

		# prepare client object
		try:
			wp = wordpresslib.WordPressClient(self.URL
								, self.Username
								, self.Password)
		except:
			return None


		# select blog id
		wp.selectBlog(0)

		return wp


if __name__ == "__main__":
	word = WordPy()
	gtk.main()
