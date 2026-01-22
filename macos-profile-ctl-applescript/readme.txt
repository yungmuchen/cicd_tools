Using Apple script to automate profile add / delete (all).

Text file here. 
The code uses "load script" command. It cannot directly load plain text .applescript files.
Users have to compile them by Applescript tool to filename.scpt style for execution.

-----------------
Execution

  osascript bar.scpt

-----------------
Compile Apple Script txt file .applescript to .scpt

If you have written your code in a plain text file (e.g., using vi or joe), 
you can compile it into a .scpt file using the following command in Terminal:

osacompile -o output_file.scpt input_file.applescript

-----------------
Decompiling for Editing (.scpt -> .applescript)

osadecompile existing_script.scpt > editable_script.applescript
