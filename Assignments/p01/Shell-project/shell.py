#!/usr/bin/env python
"""
This file is about using getch to capture input and handle certain keys 
when the are pushed. The 'command_helper.py' was about parsing and calling functions.
This file is about capturing the user input so that you can mimic shell behavior.

"""
import os
import sys
import stat
import shutil # used for file "handling" (cp, rm)
import getpass # used for whoami function
from time import sleep
from rich import print
from getch import Getch

##################################################################################
##################################################################################

# create instance of our getch class
getch = Getch()
# a list to store the command history
cmd_history = []
# index for navigating history
history_index = -1
# current position of the cursor
cursor_position = 0

'''
parse_cmd:
parses the command line input into a list of dictionaries
'''
def parse_cmd(cmd_input):
    command_list = []
    cmds = cmd_input.split("|") # split piping on the | character
    for cmd in cmds:
        # add in/outfile and append to our dictionary
        parts = {"input":None,"cmd":None,"params":[],"flags":"", "infile": None, "outfile": None, "append": None}
        subparts = cmd.strip().split()
        i = 0
        while i < len(subparts):
            # command part
            part = subparts[i]
            # read the input from a file
            if part == "<":
                # grab filename, save it to dictionary
                parts["infile"] = subparts[i+1]
                i += 2
            # write the output TO file
            elif part == ">":
                parts["outfile"] = subparts[i+1]
                parts["append"] = False     # do not append
                i += 2
            # write output to a file, but append
            elif part == ">>":
                parts["outfile"] = subparts[i+1]
                parts["append"] = True
                i += 2
            # separate the flag and add to "flags"
            elif part.startswith("-") and len(part) > 1:
                parts["flags"] += part[1:]
                i += 1
            else:
                # parameter handling
                if parts["cmd"] is None:
                    parts["cmd"] = part
                else:
                    parts["params"].append(part)
                i += 1
        # once finished, append the dictionary to command list
        command_list.append(parts)
    return command_list

def print_cmd(cmd):
    """This function "cleans" off the command line, then prints
    whatever cmd that is passed to it to the bottom of the terminal.
    """
    padding = " " * 80
    sys.stdout.write("\r" + padding)

    try:
        cwd = os.getcwd()
    except:
        cwd = "/"

    sys.stdout.write(f"\r{cwd}$ {cmd}")
    sys.stdout.flush()

'''
help
- displays correct use of commands.
'''
def help(parts, command_map=None):
    '''
    displays corrects use of commands.
    '''
    params = parts.get("params") or []
    if not params:
        return {"output": "Enter a command after help to see more.", "error": None}
    
    name_of_cmd = params[0].lower()
    if name_of_cmd in command_map:
        docstr = command_map[name_of_cmd].__doc__ or "No documentation available."
        return {"output": docstr, "error": None}
    else:
        return {"output": None, "error": f"help: no such command '{name_of_cmd}'"}

    
'''
ls
lists the entire working directory.

flags:
-a : shows all files, indluding hidden ones
-l : log listing (permissions, size, and name)
-h: human readable sizes (KB, MB, GB)
'''
def ls(parts):
    '''
    lists the entire working directory. 

    flags:
    -a : shows all files
    -l : long listing
    -h : human-readable format/sizes

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    input = parts.get("input", None)
    flags = parts.get("flags", None) or ""
    params = parts.get("params", None) or []

    # determine which directory to list
    if len(params) > 0:
        # use a specified directory
        directory = params[0]
    else:
        # default to the current directory
        directory = "."

    try:
        # get the list of files in the directory
        files = os.listdir(directory)

        # handles the -a flag (show all files, including hidden ones)
        if "a" not in flags:
            files = [f for f in files if not f.startswith(".")]

        # sorts the files alphabetically
        files.sort()

        # handles the -l flag (long listing format)
        if "l" in flags:
            output_lines = []
            for file in files:
                filepath = os.path.join(directory, file)
                try:
                    stat_info = os.stat(filepath)
                    size = stat_info.st_size

                    # use actual file permissions
                    permissions = stat.filemode(stat_info.st_mode)

                    # handles the -h flag (human readable sizes)
                    if "h" in flags:
                        if size >= 1024**3:
                            size_str = f"{size/1024**3:.1f}G"
                        elif size >= 1024**2:
                            size_str = f"{size/1024**2:.1f}M"
                        elif size >= 1024:
                            size_str = f"{size/1024:.1f}K"
                        else:
                            size_str = f"{size}B"
                    else:
                        size_str = str(size)

                    output_lines.append(f"{permissions} {size_str:>8} {file}")

                except OSError:
                    output_lines.append(f"?--------- {'?':>8} {file}")
            
            output = "\n".join(output_lines)

        else:
            # simple listing with just filenames
            output = "  ".join(files)
        
        return {"output": output, "error": None}
    
    except FileNotFoundError:
        return {"output": None, "error": f"ls: cannot access '{directory}': No such file or directory"}
    except PermissionError:
        return {"output": None, "error": f"ls: cannot open directory '{directory}': Permission denied"}
    except Exception as e:
        return {"output": None, "error": f"ls: {str(e)}"}

'''
exit:
exit the shell
'''
def exit():
    '''
    forces termination of command shell.
    '''
    os.exit

'''
mkdir:
creates a new directory 
'''
def mkdir(parts):
    '''
    creates a new directory within the current directory.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    params = parts.get("params")    
    if not params:
        return {"output": None, "error": "mkdir: missing operand"}

    # returns the inputted directory name
    path = params[0]  

    try:
        os.mkdir(path)
        return {"output": None, "error": None}
    except FileExistsError:
        return {"output": None, "error": f"mkdir: cannot create directory '{path}': File exists"}
    except PermissionError:
        return {"output": None, "error": f"mkdir: cannot create directory '{path}': Permission denied"}
    except Exception as e:
        return {"output": None, "error": f"mkdir: {str(e)}"}


'''
cd:
changes the current working directory
'''
def cd(parts):
    '''
    changes the current working directory.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''

    try:
        # retrieves the list of parameters from parts
        params = parts.get("params",None) or []

        # if there are no params, default to the home directory
        if not params:
            target_directory = os.path.expanduser("~")
        # if there is at least one param, store the first one in arg
        else:
            arg = params[0]

            # if the argument is "~", go to the home directory
            if arg == "~":
                target_directory = os.path.expanduser("~")
            # if the argument is "..", move up one directory from the current one
            elif arg == "..":
                target_directory = os.path.dirname(os.getcwd())
            # otherwise, assume the user provided a valid path
            else:
                target_directory = os.path.expanduser(arg)

        # changes the current working directory
        os.chdir(target_directory)
        # if successful, return no output or error
        return {"output": None, "error": None}

    # if the directory doesn't exist, return an error message
    except FileNotFoundError:
        return {"output": None, "error": f"cd: no such file or directory: {params[0]}"}
    # if the path is not a directory, return an error message
    except NotADirectoryError:
        return {"output": None, "error": f"cd: not a directory: {params[0]}"}
    # if the user doesn't have permission to access the directory, return an error message
    except PermissionError:
        return {"output": None, "error": f"cd: permission denied: {params[0]}"}
    # if anything else goes wrong, return a error message
    except Exception as e:
        return {"output": None, "error": f"cd: {str(e)}"}
    

'''
pwd:
prints the current working directory to the terminal
'''
def pwd(parts):
    '''
    prints the current working directory to the terminal.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    try:
        # asks the OS for the current working directory
        current_directory = os.getcwd()
        # if everything works, return the current directory with no error
        return {"output":current_directory, "error":None}
    # if anything goes wrong, return an error message
    except Exception as e:
        return {"output":None, "error": f"pwd:{str(e)}"}

'''
mv:
moves files/directories to a different location and renames files
'''
def mv(parts):
    params = parts.get("params") or []
    if len(params)<2:
        return {"output":None, "error":"mv: missing file operation"}

    source, dest = params[0], params[1]

    try:
        os.rename(source, dest)
        return {"output":None, "error":None}
    except FileNotFoundError:
        return {"output":None, "error":f"mv:{source}: There is no such file exixts"}
    except PermissionError:
        return{"output":None, "error":f"mv:permission denied"}        
    except Exception as e:
        return{"output":None, "error":f"mv:{str(e)}"}    
    

'''
cp:
makes a copy of the first argument into the second argument
'''
def cp(parts):
    '''
    makes a copy of the first argument into the second argument.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    params = parts.get("params") or []
    if len(params)<2:
        return {"output":None, "error":"cp: missing file operation"}

    source, dest = params[0], params[1]

    try:
        shutil.copy(source, dest)   # copies contents of a given source file, 
                                    # and creates a destination file with those contents.
        return {"output":None, "error":None}
    except FileNotFoundError:
        return {"output":None, "error":f"cp:{source}: There is no such file exixts"}
    except PermissionError:
        return{"output":None, "error":f"cp:permission denied"}
    except Exception as e:
        return{"output":None, "error":f"cp:{str(e)}"} 

'''
rm:
allows the user to delete a file/directory by passing its name
'''
def rm(parts):
    """
    removes files or directories.

    flags:
    -r : recursive (delete directories and their contents)
    -f : force (ignore errors, no prompts)

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output: dict: {"output":string,"error":string}
    """
    params = parts.get("params") or []
    flags = parts.get("flags") or ""

    if not params:
        return {"output": None, "error": "rm: missing operand"}

    # used as an error message display
    errors = []

    for path in params:
        try:
            # if the path is a file, delete it
            if os.path.isfile(path):
                os.remove(path)
            # if the path is a directory
            elif os.path.isdir(path):
                if "r" in flags:
                    if "f" not in flags:
                        user = input(f"Are you sure you want to delete '{path}' and its contents? (y/n) ")
                        # if ANYTHING but "y" is entered, do nothing
                        if user.lower() != "y":
                            continue
                    # deletion
                    shutil.rmtree(path)
                else:
                    if "f" not in flags:
                        errors.append(f"rm: cannot remove '{path}': Is a directory")
            # if the files doesn't exist
            else:
                if "f" not in flags:
                    errors.append(f"rm: cannot remove '{path}': No such file or directory")

        # display error exception msg
        except Exception as e:
            if "f" not in flags:
                errors.append(f"rm: error removing '{path}': {str(e)}")
    if errors:
        error_output = "\n".join(errors)
    else:
        error_output = None
    return {"output": None, "error": error_output}
 

'''
cat:
allows the user to view the contents of a file
'''
def cat(parts):
    '''
    Displays or cats file contents or piped input, with optional formatting.

    Flags:
    -n : number all lines
    -b : number non-empty lines (overrides -n)
    -s : collapse multiple blank lines into one
    -v : display non-printing characters (except tabs and newlines)

    Input: dict with keys: "input" (str), "cmd" (str), "params" (list), "flags" (str)
    Output: dict with keys: "output" (str), "error" (str)
    '''
    arguments = parts.get("params", [])
    options = parts.get("flags", "")
    piped_data = parts.get("input")
    output_file = parts.get("outfile")
    append_mode = parts.get("append", False)

    # Determine input sources
    if piped_data is not None:
        sources = ["<stdin>"]
    else:
        sources = arguments
        if not sources:
            return {"output": None, "error": "cat: No file provided"}

    all_lines = []

    # Collect content from all sources
    for source in sources:
        try:
            if source == "<stdin>":
                all_lines.extend(piped_data.splitlines(keepends=True))
            else:
                with open(source, "r", encoding="utf-8") as file:
                    all_lines.extend(file.readlines())
        except FileNotFoundError:
            return {"output": None, "error": f"cat: {source}: File not found"}
        except PermissionError:
            return {"output": None, "error": f"cat: {source}: Access denied"}
        except Exception as err:
            return {"output": None, "error": f"cat: Error: {str(err)}"}

    # Apply -s flag: reduce multiple blank lines
    if "s" in options:
        filtered_lines = []
        last_was_blank = False
        for line in all_lines:
            is_blank = line.strip() == ""
            if is_blank and last_was_blank:
                continue
            filtered_lines.append(line)
            last_was_blank = is_blank
        all_lines = filtered_lines

    # Apply -v flag: show non-printing characters
    if "v" in options:
        import string
        modified_lines = []
        for line in all_lines:
            new_line = ""
            for char in line:
                if char in string.printable or char in ("\t", "\n"):
                    new_line += char
                else:
                    new_line += f"^{chr(ord(char) % 128 + 64)}"
            modified_lines.append(new_line)
        all_lines = modified_lines

    # Apply -b or -n flag: add line numbers
    if "b" in options:
        numbered_lines = []
        line_counter = 0
        for line in all_lines:
            if line.strip():
                line_counter += 1
                numbered_lines.append(f"{line_counter:6}  {line.rstrip()}\n")
            else:
                numbered_lines.append(line)
        all_lines = numbered_lines
    elif "n" in options:
        all_lines = [f"{i+1:6}  {line.rstrip()}\n" for i, line in enumerate(all_lines)]

    final_output = "".join(all_lines).rstrip()

    # Handle output redirection
    if output_file:
        try:
            mode = "a" if append_mode else "w"
            with open(output_file, mode, encoding="utf-8") as file:
                file.write(final_output + "\n")
            return {"output": None, "error": None}
        except PermissionError:
            return {"output": None, "error": f"cat: {output_file}: Access denied"}
        except Exception as err:
            return {"output": None, "error": f"cat: Error: {str(err)}"}

    return {"output": final_output, "error": None}


'''
mv:
moves files/directories to a different location and renames files
'''
def mv(parts):
    
    params = parts.get("params") or []
    if len(params) < 2:
        return {"output": None, "error": "mv: missing file operand"}

    src, dest = params[0], params[1]

    try:
        # If target is a directory, append the filename
        if os.path.isdir(dest):
            dest = os.path.join(dest, os.path.basename(src))

        shutil.move(src, dest)
        return {"output": f"Moved '{src}' to '{dest}'", "error": None}

    except FileNotFoundError:
        return {"output": None, "error": f"mv: cannot stat '{src}': No such file or directory"}
    except PermissionError:
        return {"output": None, "error": f"mv: cannot move '{src}': Permission denied"}
    except Exception as e:
        return {"output": None, "error": f"mv: {str(e)}"}



'''changes the permissions of a file 
what the numbers mean in command ex: 777 
it grants permission access for a file 
the [0] = owner
[1] = group
[2] = others 
"0": "---", "1": "--x", "2": "-w-", "3": "-wx",
"4": "r--", "5": "r-x", "6": "rw-", "7": "rwx"
'''
def chmod(parts):
    '''
    changes the permissions of a file. 
    
    [0] = owner
    [1] = group
    [2] = others 
    "0": "---", "1": "--x", "2": "-w-", "3": "-wx",
    "4": "r--", "5": "r-x", "6": "rw-", "7": "rwx"
    '''
    params = parts.get("params") or []

    if len(params) < 2:
        return{"output":None, "error": "chmod:missing operand \n usage: chmod <mode> <filename>"}
    

    mode_str, filename = params[0], params[1]

    try:
        #this convert  the strings like "777" into octal int (example 0o777)

        mode = int(mode_str, 8)

        os.chmod(filename, mode)

        permissions = stat.filemode(mode)

        return {"output": f"permission of '{filename}' changed to {mode_str}", "error":None}

    except ValueError:
        return {"ouput":None, "error": f"chmod invalid mode:'{mode_str}'", "error":None}

    except FileNotFoundError:
        return{"output":None, "error":f"chmod: there no such file '{filename}'"}

    except PermissionError:
        return {"output": None, "error": f"chmod: changing permissions of '{filename}': Permission denied"}

    except Exception as e:
        return {"output": None, "error": f"chmod: {str(e)}"}

'''
wc
counts the total number of words/lines in a file or piped input
'''
def wc(parts):
    '''
    Counts lines, words, bytes, and/or characters in files or piped input.

    Flags:
    -l : count lines
    -w : count words
    -c : count bytes
    -m : count characters (overrides -c if specified)

    Input: dict with keys: {"input" (str), "cmd" (str), "params" (list), "flags" (str)}
    Output: dict with keys: "output" (str), "error" (str)
    '''
    arguments = parts.get("params", [])
    options = parts.get("flags", "")
    piped_data = parts.get("input")

    # Decide what to count based on flags or default behavior
    show_lines = "l" in options or not options
    show_words = "w" in options or not options
    show_bytes = "c" in options or not options
    show_chars = "m" in options
    if show_chars and "c" in options:
        show_bytes = False  # -m takes precedence over -c

    # Determine input sources
    sources = arguments if arguments else []
    if piped_data is not None:
        sources = ["<stdin>"]  # Handle piped input

    overall_lines = 0
    overall_words = 0
    overall_bytes = 0
    overall_chars = 0
    results = []

    for source in sources:
        if source == "<stdin>":
            text_content = piped_data
        else:
            try:
                with open(source, "r", encoding="utf-8") as file:
                    text_content = file.read()
            except FileNotFoundError:
                return {"output": None, "error": f"word_count: {source}: File not found"}
            except PermissionError:
                return {"output": None, "error": f"word_count: {source}: Access denied"}
            except Exception as err:
                return {"output": None, "error": f"word_count: Error: {str(err)}"}

        # Calculate counts
        line_total = text_content.count("\n") + (1 if text_content and not text_content.endswith("\n") else 0)
        word_total = len(text_content.split())
        byte_total = len(text_content.encode("utf-8"))
        char_total = len(text_content)

        # Accumulate totals for multiple files
        overall_lines += line_total
        overall_words += word_total
        overall_bytes += byte_total
        overall_chars += char_total

        # Build output for this source
        counts = []
        if show_lines:
            counts.append(f"{line_total:8}")
        if show_words:
            counts.append(f"{word_total:8}")
        if show_chars:
            counts.append(f"{char_total:8}")
        if show_bytes:
            counts.append(f"{byte_total:8}")
        if source != "<stdin>":
            counts.append(source)
        results.append(" ".join(counts))

    # Add totals if multiple files
    if len(sources) > 1:
        total_counts = []
        if show_lines:
            total_counts.append(f"{overall_lines:8}")
        if show_words:
            total_counts.append(f"{overall_words:8}")
        if show_chars:
            total_counts.append(f"{overall_chars:8}")
        if show_bytes:
            total_counts.append(f"{overall_bytes:8}")
        total_counts.append("total")
        results.append(" ".join(total_counts))

    return {"output": "\n".join(results).strip(), "error": None}

          

'''
sort:
sorts the contents of a file(s) in ASCII order
'''
def sort(parts):
    '''
    sorts the contents of a file(s) in ASCII order.
    '''
    params = parts.get("params") or []
    if not params:
        return{"output":None, "error": "sort:missing file operand"}

    filename = params[0]

    try:
        with open(filename, "r", encoding ="utf-8") as f:
            lines = f.readlines()
            sorted_lines = sorted(line.strip() for line in lines)
            result ="\n".join(sorted_lines)
            return {"output": result, "error":None}
        
    except FileNotFoundError:
        return{"output":None, "error":f"sort: {filename}: no such file exists"}
    except PermissionError:
        return{"output":None, "error":f"sort:{filename}: permisiion denied"}

'''
less:
allows the user to only see snippets of files
'''
def less(parts):
    '''
    Shows a file's contents page by page, with optional line count and line numbers.

    Flags:
    -N : show line numbers
    '''
    params = parts.get("params", [])
    flags = parts.get("flags", "")
    show_numbers = "N" in flags

    # Check if any parameters are provided
    if not params:
        return {"output": None, "error": "less: No file given"}

    # Default to 20 lines per page
    lines_per_page = 10
    file_name = None

    # Find file name and line count
    for param in params:
        if param.isdigit():
            lines_per_page = int(param)  # Set custom line count
            if lines_per_page <= 0:
                return {"output": None, "error": "less: Line count must be positive"}
        else:
            file_name = param  # Set file name

    if not file_name:
        return {"output": None, "error": "less: No file given"}

    try:
        # Read the file
        with open(file_name, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Start at the first line
        start_line = 0

        # Show file page by page
        while start_line < len(lines):
            # Get the next chunk of lines
            end_line = min(start_line + lines_per_page, len(lines))
            for i, line in enumerate(lines[start_line:end_line], start=start_line + 1):
                if show_numbers:
                    print(f"{i:4} {line.rstrip()}")  # Show line number
                else:
                    print(line.rstrip())  # Show line without extra newline

            # Stop if we’ve shown all lines
            if end_line >= len(lines):
                break

            # Show prompt and wait for user input
            sys.stdout.write("--More-- (press space to continue, q to quit)")
            sys.stdout.flush()

            # Use getch to get a single key
            from getch import Getch
            key = Getch()()

            # Clear the prompt
            sys.stdout.write("\r" + " " * 40 + "\r")
            sys.stdout.flush()

            # Handle user input
            if key.lower() == "q":
                return {"output": None, "error": None}
            if key in (" ", "\r"):
                start_line += lines_per_page  # Move to next page
            # Ignore other keys and loop again

        return {"output": None, "error": None}

    except FileNotFoundError:
        return {"output": None, "error": f"less: {file_name}: File not found"}
    except PermissionError:
        return {"output": None, "error": f"less: {file_name}: Access denied"}
    except Exception as e:
        return {"output": None, "error": f"less: Error: {str(e)}"}
    

'''
head:
displays the first ten lines of a file
'''
def head(parts):
    '''
    displays the first ten lines of a file.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    # if params doesn't exist, defaults to an empty list
    params = parts.get("params") or []
    # if flags doesn't exist, defaults to an empty string
    flags = parts.get("flags") or ""

    # if a filename is not provided, return an error message
    if not params:
        return {"output": None, "error": "Head: missing file operand"}
    
    # assumes the first parameter is a filename
    filename = params[0]
    # default number of lines to show
    n = 10

    if "n" in flags:
        # check that there's at least one more parameter after the filename
        if len(params) > 1:
            # tries to convert the second parameter to an integer
            try:
                n = int(params[1])
            # if the second parameter isn't an integer return an error message
            except ValueError:
                return {"output": None, "error": "head: invalid number of lines"}
        # if the user typed head {filename} -n without a number after the n
        # return an error message
        else:
            return {"output": None, "error": "head: option requires an argument -- 'n'"}
    # tries to open the file and read its lines    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            # reads all lines into a list
            lines = f.readlines()
            # returns the first n lines as a single string
            return {"output": "".join(lines[:n]), "error": None}
    # if the file doesn't exist, return an error message
    except FileNotFoundError:
        return {"output": None, "error": f"head: {filename}: No such file or directory"}
    # if the user doesn't have permission to read the file, return an error message
    except PermissionError:
        return {"output": None, "error": f"head: {filename}: Permission denied"}
    
'''
tail:
prints the data at the end of a file
'''
def tail(parts):
    '''
    prints the data at the end of a file.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    # if params doesn't exist, defaults to an empty list
    params = parts.get("params") or []
    # if flags doesn't exist, defaults to an empty string
    flags = parts.get("flags") or ""

    # if a filename is not provided, return an error message
    if not params:
        return {"output": None, "error": "tail: missing the file operand"}
    
    # assumes the first parameter is a filename
    filename = params[0]
    # default number of lines to show
    n = 10

    # if the user included the "n" flag
    if "n" in flags:
        # check that there's at least one more parameter after the filename
        if len(params) > 1:
            # tries to convert the second parameter to an integer
            try:
                n = int(params[1])
            # if the second parameter isn't an integer return an error message
            except ValueError:
                return {"output": None, "error": "tail: invalid number of lines"}
        # if the user typed tail {filename} -n without a number after the n
        # return an error message
        else:
            return {"output": None, "error": "tail: option requires an argument -- 'n'"}
    # tries to open the file and read its lines   
    try:
        with open(filename, "r", encoding="utf-8") as f:
            # reads all lines into a list
            lines = f.readlines()
            # returns the last n lines as a single string
            return {"output": "".join(lines[-n:]), "error": None}
    # if the file doesn't exist, return an error message
    except FileNotFoundError:
        return {"output": None, "error": f"tail: cannot open '{filename}': No such file"}
    # if the user doesn't have permission to read the file, return an error message
    except PermissionError:
        return {"output": None, "error": f"tail: cannot open '{filename}': Permission denied"}
'''
grep:
finds matching words within text files
'''
def grep(parts):
    """
    Runs a search on a file or through piped input.

    Flags:
    -i : ignore case
    -l : list matching filenames only
    """
    params = parts.get("params") or []
    flags = parts.get("flags") or ""
    input_text = parts.get("input")

    # throw error
    if not params:
        return {"output": None, "error": "grep: missing search pattern"}

    to_match = params[0]
    files = params[1:]

    ignore_case = "i" in flags
    list_files = "l" in flags
    count_only = "c" in flags

    lines_match = []
    files_match = set()
    count_match = 0

    # search in files, if applicable
    for filename in files:
        try:
            count = 0
            # open file
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    # check the lines to match the pattern
                    line_to_check = line
                    pattern_to_check = to_match
                    # if "i" in flags
                    if ignore_case:
                        line_to_check = line.lower()
                        pattern_to_check = to_match.lower()

                    if pattern_to_check in line_to_check:
                        # if "l" in flags
                        if list_files:
                            files_match.add(filename)
                            break
                            # if "c" in flags
                        elif count_only:
                            count += 1
                        else:
                            lines_match.append(f"{filename}:{line.rstrip()}")
            if count_only:
                lines_match.append(f"{filename}:{count}")
        except FileNotFoundError:
            return {"output": None, "error": f"grep: {filename}: No such file"}
        except PermissionError:
            return {"output": None, "error": f"grep: {filename}: Permission denied"}

    # search piped input if no files are given
    if not files and input_text:
        for line in input_text.splitlines():
            line_to_check = line
            pattern_to_check = to_match
            if ignore_case:
                line_to_check = line.lower()
                pattern_to_check = to_match.lower()

            if pattern_to_check in line_to_check:
                if count_only:
                    count += 1
                else:
                    lines_match.append(line.rstrip())

        if count_only:
            lines_match.append(str(count))

    # display output
    if list_files:
        return {"output": "\n".join(files_match), "error": None}
    else:
        return {"output": "\n".join(lines_match), "error": None}

'''
history:
prints the entire history of commands used as an enumerated list, beginning from 1 to i
'''
def history(parts=None):
    '''
    prints the entire history of commands used as an enumerated list, beginning from 1 to i.
    '''
    lines = []
    # enumerate and append each cmd to cmd_history
    for i, cmd in enumerate(cmd_history):
        lines.append(f"{i+1} {cmd}")
    return {"output": "\n".join(lines), "error": None}

'''
exclamation (!):
runs the command specified by the history index
'''
def exclamation(user_input):
    '''
    runs the command specified by the history index.
    '''
    # if an exclamation is not attached
    if not user_input.startswith("!"):
        return None

    num_str = user_input[1:]

    # if num is NOT a digit, error message
    if not num_str.isdigit():
        return None # only handle numbers after !

    num = int(num_str)  # typecast num as an int to check for boundary issue

    # if num is out of the range of cmd history, error message
    if num < 1 or num > len(cmd_history):
        return None

    # print the command before returning
    print(cmd_history[num - 1])
    return cmd_history[num - 1]

'''
whoami: 
displays the username of the logged in user
'''
def whoami(parts):
    '''
    displays the username of the logged in user.
    '''
    try:
        # get the user from getpass library
        user = getpass.getuser()
        return {"output": user, "error": None}
    except Exception as e:
        return {"output": None, "error": f"whoami: {str(e)}"}

'''
clear
clears the terminal screen
'''
def clear(parts=None):
    '''
    clears the terminal screen.
    '''

    # ANSI escape sequence to clear the screen and move the cursor to the top-left corner
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

    # prints an empty command prompt after clearing the terminal
    redraw_prompt("", 0)
    return {"output": None, "error": None}

'''
piping: 
handles piping of commands as well as redirects
'''
def piping(command_list):
    prev_output = None  # output from previous command

    for cmd_dict in command_list:
        # handle input file
        if cmd_dict.get("infile"):
            try:
                with open(cmd_dict["infile"], "r", encoding="utf-8") as f:
                    cmd_dict["input"] = f.read()
            except FileNotFoundError:
                return {"output": None, "error": f"{cmd_dict['cmd']}: {cmd_dict['infile']}: No such file"}
            except PermissionError:
                return {"output": None, "error": f"{cmd_dict['cmd']}: {cmd_dict['infile']}: Permission denied"}

        # pass previous command's output as input
        if prev_output is not None:
            cmd_dict["input"] = prev_output

        # execute the command
        result = execute_command(cmd_dict)

        # update prev_output for next command
        prev_output = result.get("output")

        # handle output redirection
        if cmd_dict.get("outfile") and result.get("output") is not None:
            if cmd_dict.get("append"):
                mode = "a"  
            else:
                mode = "w"
            with open(cmd_dict["outfile"], mode, encoding="utf-8") as f:
                f.write(result["output"] + "\n")

        # if there’s an error, stop the pipe
        if result.get("error"):
            return result
    # display result
    return result


'''
execute_command
executes the command given on the command dictionary 
'''
def execute_command(command_dict):
    """
    Command dispatcher - routes commands to their respective functions
    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output: dict: {"output":string,"error":string}
    """
    command_map = {
        # Add more commands here as you implement them
        'pwd': pwd,
        'ls': ls,
        'history': history,
        'mkdir': mkdir,
        'whoami': whoami,
        'exit': exit,
        'cd': cd,
        'wc':wc,
        'sort': sort,
        'mv' : mv, 
        'head': head, 
        'tail': tail,
        'cat': cat,
        'less': less,
        'rm': rm,
        'cp': cp,
        'grep': grep,
        'help': help,
        'clear': clear,
        'chmod': chmod
        # etc.ex
    }

    cmd_name = command_dict.get('cmd', '').lower()

    # snippet to handle the 'help' command
    if cmd_name in command_map:
        if cmd_name == "help":
            return command_map[cmd_name](command_dict, command_map = command_map)
        else:
            return command_map[cmd_name](command_dict)
    else: # if command does not exist
        return {"output": None, "error": f"Command '{cmd_name}' not found"}

'''
redraw_prompt
redraws the current prompt and command, placing the cursor at the correct position
'''
def redraw_prompt(cmd, cursor_position):
    '''
    redraws the current prompt and command, placing the cursor at the correct position
    '''
    # clears the current line
    sys.stdout.write("\r\033[K")

    try:
        cwd = os.getcwd()

    except:
        cwd = "/"
    # prints the prompt with the current working directory and command
    sys.stdout.write(f"{cwd}$ {cmd}")
    sys.stdout.flush()

    # moves the cursor to the correct position
    prompt_length = len(f"{cwd}$ ")
    move = prompt_length + cursor_position
    sys.stdout.write(f"\r\033[{move+1}C")
    sys.stdout.flush()


if __name__ == "__main__":
    # initial command is empty
    cmd = ""
    # curson position starts at 0
    cursor_position = 0
    # print the initial command prompt
    redraw_prompt(cmd, cursor_position)

    # loop forever
    while True:  
        # grab a character from the user
        char = getch()  

        # if ctrl-c or exit command is pressed, exit the program
        if char == "\x03" or cmd == "exit":
            raise SystemExit("\nBye.")

        # if backspace is pressed, remove the last character from cmd
        elif char == "\x7f":
            if cursor_position > 0:
                cmd = cmd[:cursor_position - 1] + cmd[cursor_position:]
                cursor_position -= 1
            redraw_prompt(cmd, cursor_position)

        # identify arrow keys and handle accordingly
        elif char in "\x1b":
            # detect the full excape sequence
            null = getch()
            # grab the direction character
            direction = getch()

            # if the up arrow is pressed
            if direction in "A":
                # get the previous command from history (if there is one)
                if history_index > 0:
                    history_index -= 1
                    cmd = cmd_history[history_index]
                    # set the cursor position to the end of the command line
                    cursor_position = len(cmd)

            # if the down arrow is pressed
            elif direction in "B":
                # get the next command from history (if there is one)
                if history_index < len(cmd_history) - 1:
                    history_index += 1
                    cmd = cmd_history[history_index]
                # if there is no next command, clear the command line
                else:
                    history_index = len(cmd_history)
                    cmd = ""
                # set the cursor position to the end of the command line
                cursor_position = len(cmd)
            # if the right arrow is pressed
            elif direction == "C":
                # move the cursor right, if not at the end of the command
                if cursor_position < len(cmd):
                    cursor_position += 1
            # if the left arrow is pressed
            elif direction == "D":
                # move the cursor left, if not at the beginning of the command
                if cursor_position > 0:
                    cursor_position -= 1
            
            redraw_prompt(cmd, cursor_position)

        # if enter is pressed, execute the command
        elif char in "\r":
            # move to a new line
            sys.stdout.write("\n")
            user_input = cmd.strip()

            # Executes the !x history command
            if user_input:
                list_num = exclamation(user_input)
                # if a valid history command was found, use it as the user input
                if list_num:
                    user_input = list_num
            
            # Add the command to history if it's not empty
            if user_input:
                # avoid duplicate consecutive entries
                cmd_history.append(user_input)
                # set the history index to the end of the list
                history_index = len(cmd_history)

                # parse the command into a list of commands (for piping)
                command_list = parse_cmd(user_input)
                if command_list:
                    # execute the command(s)
                    result = piping(command_list)
                    # print the output and error (if any)
                    if result["output"]:
                        print(result["output"])
                    if result["error"]:
                        print(f"Error: {result['error']}")
            
            # reset the command line and cursor position
            cmd = ""
            cursor_position = 0
            redraw_prompt(cmd, cursor_position)
        # if a regular character is pressed
        else:
            # insert the character at the current cursor position
            cmd = cmd[:cursor_position] + char + cmd[cursor_position:]
            cursor_position += 1
            redraw_prompt(cmd, cursor_position)





