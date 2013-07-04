#
# SublimeFeelingLucky.py
#
# v 0.2.2
#

import sublime, sublime_plugin, re, os, json, time

_word = ""
_prefix = ""
_type = ""
_count = 0
_openCount = 0

#
# css
#
class FeelingLuckyCss(sublime_plugin.TextCommand):
	def run(self, edit):
		global _type
		_type = "css"
		self.view.run_command("feeling_lucky")

#
# js
#
class FeelingLuckyJs(sublime_plugin.TextCommand):
	def run(self, edit):
		global _type
		_type = "js"
		self.view.run_command("feeling_lucky")


#
# main
#
class FeelingLucky(sublime_plugin.TextCommand):

	def run(self, edit):
		global _prefix
		global _word
		global _count

		if not _check(self, -4, "html") :
			_showAlert("html file only")
			return

		# get Json data
		data = self.loadJSON()
		if not data :
			return

		projectPath = sublime.active_window().folders()[0]

		# file_name_list = os.listdir(projectPath)

		# for file_name in file_name_list:
		#     f = open(os.path.join(projectPath, file_name))
		#     line = f.readline()
		#     line_number = 1
		#     while line:
		#         m = re.search(search_pattern, line)
		#         if m:
		#             print "Pattern Found: file:%s, line:%d, data:%s" % (file_name, line_number, line)
		#         line = f.readline()
		#         line_number = line_number + 1
		#     f.close()

		for region in self.view.sel():
			_word = self.view.substr(self.view.word(region))
			line = self.view.substr(self.view.line(region))

			match = re.search(r'.+(id|class).+', line)
			if match is None:
				_showAlert("Not match 'id' or 'class'")
				return
			else:
				type = match.group(1)
				if   type == "id" 	 : _prefix = "#"
				elif type == "class" : _prefix = "."

			_count = 0
			obj = []

			if _type == "css" :
				# check css / sass
				self.fileCheck(data, "css", obj, _count)
				self.fileCheck(data, "sass", obj, _count)

			elif _type == "js" :
				# check js / coffee
				self.fileCheck(data, "js", obj, _count)
				self.fileCheck(data, "coffee", obj, _count)


			_printError("hogehoge")

			# openFile
			for p in obj :
				self.view.window().run_command('expand_and_focus_right_panel', { "len": p["len"], "count": p["count"] })
				view = self.view.window().open_file(p["path"])
				view.window().set_view_index(view, p["count"], 0)
				_scrollMatchPoint(view.window(), p["line_number"])
				_printError(view.window(), p["line_number"])



	def fileCheck(self, data, type, list, count) :
		global _word
		projectPath = sublime.active_window().folders()[0]
		if type in data :
			for a in data[type] :
				path = os.path.join(projectPath, a)
				f = open(path)
				line = f.readline()
				lineNumber = 1
				while line:
					m = re.search(_word, line)
					if m:
						print "Pattern Found: file:%s, line:%d, data:%s" % (a, lineNumber, line)
						count += 1
						list.append({"path":path, "len":len(data[type]), "count":count, "text":_prefix + _word, "line_number":lineNumber})

					line = f.readline()
					lineNumber += 1
				f.close()



	def loadJSON(self) :
		try:
			f = open(os.path.join(sublime.active_window().folders()[0], "config.feelinglucky"))
			data = json.load(f)
			f.close()
			return data
		except Exception as e:
			if sublime.ok_cancel_dialog('Not found config.feelinglucky\nMake config.feelinglucky file ?') :
				self.view.run_command("make_config_dot_feeling_lucky")
			return False


#
# file check
#
class FeelingLuckyFile(sublime_plugin.TextCommand):

	def run(self, edit):

		_printError("FeelingLuckyFile")



#
# css/sass file
#
# class FeelingLuckyCssFile(sublime_plugin.TextCommand):

# 	def run(self, edit):
# 		# global _openCount
# 		# text = _prefix + _word
# 		# match = self.view.find(text, 0, sublime.LITERAL)
# 		# _scrollMatchPoint(self, match)


#
# js/coffee file
#
# class FeelingLuckyJsFile(sublime_plugin.TextCommand):

# 	def run(self, edit):
# 		# global _openCount

# 		# text = _prefix + _word
# 		# match = self.view.find(text, 0, sublime.LITERAL)
# 		# _scrollMatchPoint(self, match)


#
# event
#
class FeelingLuckyEventListener(sublime_plugin.EventListener):

	def on_load(self, view):
		self.call(view)

	# def on_activated(self, view):
	# 	self.call(view)

	def call(self, view):
		view.run_command("feeling_lucky_file")


#
# config.feelinglucky
#
class MakeConfigDotFeelingLucky(sublime_plugin.TextCommand):

	def run(self, edit):

		projectPath = sublime.active_window().folders()[0]

		if os.path.isfile(os.path.join(projectPath, "config.feelinglucky")) :
			_showAlert("Found config.feelingLucky")

		else :
			css = []
			sass = []
			js = []
			coffee = []
			for root, dirs, files in os.walk(projectPath):
			    for file in files:
			    	f = os.path.join(root, file)
			    	ff = f.replace(projectPath + "/", "")
			    	if file[-4:] == ".css" :
			    		css.append(ff)
		    		elif file[-5:] == ".scss" :
		    			sass.append(ff)
		    		elif file[-3:] == ".js" :
		    			js.append(ff)
		    		elif file[-7:] == ".coffee" :
		    			coffee.append(ff)

			print('Make config.feelingLucky')
			config = { "js":js, "coffee":coffee, "sass":sass, "css":css }
			file = open(os.path.join(projectPath, "config.feelinglucky"), "w")
			json.dump(config, file, indent=4)


#
# window controll
#
class ExpandAndFocusRightPanel(sublime_plugin.WindowCommand):

	def run(self, len, count):
		w = 0.6;

		if len == 1:
			p = {
					"cols": [0.0, w, 1.0],
					"rows": [0.0, 1.0],
					"cells":
					[
						[0, 0, 1, 1], [1, 0, 2, 1]
					]
				}
		elif len == 2 :
			p = {
					"cols": [0.0, w, 1.0],
					"rows": [0.0, 0.5, 1.0],
					"cells":
					[
					    [0, 0, 1, 2], [1, 0, 2, 1],
					                  [1, 1, 2, 2]
					]
				}
		elif len >= 3 :
			p = {
					"cols": [0.0, w, 1.0],
					"rows": [0.0, 0.33, 0.66, 1.0],
					"cells":
					[
					    [0, 0, 1, 3], [1, 0, 2, 1],
					                  [1, 1, 2, 2],
					                  [1, 2, 2, 3]
					]
				}

		self.window.run_command("set_layout", p)
		self.window.run_command("focus_group", {"group": count})


#
# utils
#

def _showAlert(message) :
	sublime.error_message("SublimeFeelingLucky : \n" + message)

def _printError(message) :
	print("[FeelingLucky Error] : " + message)

# file type check
def _check(self, range, type) :
	fileName = self.view.file_name()
	if fileName[range:] == type :
		return True
	else :
		return False

# scroll
def _scrollMatchPoint(self, match) :
	if match :
		self.view.sel().clear()
		self.view.sel().add(match)
		self.view.show_at_center(match)

