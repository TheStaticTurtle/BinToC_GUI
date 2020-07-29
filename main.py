import sys
import subprocess
import os.path
import re
import shutil

try:
	import tkinter as tk
	from tkinter.filedialog import *
	from tkinter import scrolledtext
	from tkinter import ttk
except ImportError:
	print("Uh oh. It appears that you don't have tkinter installer to install it run \"sudo apt install python3-tk\" on linux and on windows re-run the installer and be sure that the \"Tcl/Tk\" option is enabled on mac you can try to execute \"brew install tcl-tk\"")
	sys.exit(1)

try:
	import pyperclip
except ImportError:
	print("The package pyperclip wasn't installed Executing: \""+sys.executable+" -m pip install pyperclip\"")
	try:
		subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
	except Exception:
		print("The auto installation failed please find a suitable way to install the pyperclip module for this python version")
		sys.exit(1)

class PythonConverter:
	def __init__(self):
		self.path = None

	def set_file(self, path):
		self.path = path

	def convert(self):
		if self.path != None:
			try:
				output = ""
				fname = self.path.replace("\\","/").split("/")[-1]
				formated_fname = re.sub(r'\W+', '_', ('.'.join(fname.split(".")[:-1])))

				output += "//\n//"+fname+"\n//\n"
				output += "const uint8_t "+formated_fname+"[] PROGMEM = {\n"
				with open(self.path, "rb") as file:
					bytes = file.read(16)
					while bytes != b"":
						output += "\t" + ', '.join([ str(hex(b)) + ' '*(4-len(str(hex(b)))) for b in bytes]) +",\n"
						bytes = file.read(16)
				output = output[:-2]+"\n};"
				return output

			except Exception as e:
				return "Error detected: %s" % str(e)
		else:
			return "No file was specified to the converter"


class BinToC_Converter:
	def __init__(self):
		self.path = None

	def set_file(self, path):
		self.path = path

	def is_present(self):
		if shutil.which("bin_to_c") is not None:
			return True

		files = [f for f in os.listdir('.') if os.path.isfile(f)]
		if "bin_to_c" in files or "bin_to_c.exe" in files:
			return True

		return False

	def convert(self):
		try:
			if shutil.which("bin_to_c") is not None:
				return subprocess.check_output(['bin_to_c',self.path])
			else:
				return subprocess.check_output(['./bin_to_c',self.path])
		except subprocess.CalledProcessError as exc:
			return "Error: \n"+str(exc.output.decode("utf-8"))

class Application(tk.Frame):
	def __init__(self, root=None, converter=None):
		super().__init__(root)
		self.converter = converter
		root.title("File to C converter")

		file_grid = Frame(root, height=100, width=100)
		file_grid.pack(side=tk.TOP, fill=tk.X)

		self.label_input_file = ttk.Label(file_grid, text="File path: ", font=("TkDefaultFont", 11))
		self.label_input_file.pack(fill=tk.X, expand=tk.NO, side=tk.LEFT)

		self.textbox_input_file_path = ttk.Entry(file_grid, width=50, font=("TkDefaultFont", 11))
		self.textbox_input_file_path.pack(fill=tk.X, expand=tk.YES, side=tk.LEFT)
		self.textbox_input_file_path.config(state="disabled")

		self.button_open_file_dialog = tk.Button(file_grid, text="Open file", fg="black", command=self.open_file_dialog, font=("TkDefaultFont", 11))
		self.button_open_file_dialog.pack(fill=tk.X, expand=tk.NO, side=tk.LEFT)

		self.button_start_conversion = tk.Button(root, text="Reconvert", fg="black", command=self.convert, font=("TkDefaultFont", 12))
		self.button_start_conversion.pack(fill=tk.X, expand=tk.YES, side=tk.TOP)
		self.button_start_conversion.config(state="disabled")

		self.scrolledtext_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=125, height=40, font=None)
		self.scrolledtext_output.pack(fill=tk.BOTH, expand=tk.YES)

		self.button_copy = tk.Button(root, text="Copy to clipboard", fg="black", command=self.copy, font=("TkDefaultFont", 12))
		self.button_copy.pack(fill=tk.X, expand=tk.YES, side=tk.BOTTOM)
		self.button_copy.config(state="disabled")

		if type(converter) == PythonConverter:
			self.scrolledtext_output.delete('1.0',tk.END)
			self.scrolledtext_output.insert(tk.INSERT, "WARNING: \nThis program should use bitbank2 bin_to_c converter, however it wasn't found in the path nor the current folder.\nFalling back to the deprecated python implementation")


	def convert(self):
		result = self.converter.convert()
		self.scrolledtext_output.delete('1.0',tk.END)
		self.scrolledtext_output.insert(tk.INSERT, result)
		self.button_copy.config(state="normal")
		self.button_start_conversion.config(state="normal")

	def open_file_dialog(self):
		fname = askopenfilename(filetypes=[
			("Gif files", "*.gif"),
			("All files", "*.*")
		])

		self.textbox_input_file_path.config(state="normal")
		self.textbox_input_file_path.delete(0, 'end')
		self.textbox_input_file_path.insert(0, fname)
		self.textbox_input_file_path.config(state="disabled")
		self.converter.set_file(fname)
		self.convert()

	def copy(self):
		result = self.converter.convert()
		pyperclip.copy(result)


bin2c = BinToC_Converter()

converter = bin2c if bin2c.is_present() else PythonConverter()

app = Application(root=tk.Tk(), converter=converter)
app.mainloop()
