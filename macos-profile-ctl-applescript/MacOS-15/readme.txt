Dev Env

Hardware: 
Mac-mini M4
Model Identifier: Mac16,10

ProductName:		macOS
ProductVersion:		15.5
BuildVersion:		24F74

-----------------
Execution

1) from .applescript

  osascript foo.applescript

2) from .scpt

  osascript bar.scpt

-----------------
Compile Apple Script txt file .applescript to .scpt

If you have written your code in a plain text file (e.g., using vi or joe), 
you can compile it into a .scpt file using the following command in Terminal:

osacompile -o output_file.scpt input_file.applescript

-----------------
Decompiling for Editing (.scpt -> .applescript)

osadecompile existing_script.scpt > editable_script.applescript

