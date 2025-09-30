#!/usr/bin/env python
"""
This file is about using getch to capture input and handle certain keys 
when the are pushed. The 'command_helper.py' was about parsing and calling functions.
This file is about capturing the user input so that you can mimic shell behavior.

Andrew's sources used - geeksforgeeks, chatgpt (redirection, piping())

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

getch = Getch()  # create instance of our getch class
prompt = "$"  # set default prompt
# global variable to store current directory
current_directory = "/"

'''
parse_cmd:
parses the command line input into a list of dictionaries
'''
def parse_cmd(cmd_input):
    command_list = []
    cmds = cmd_input.split("|") # split piping on the | character
    for cmd in cmds:
        # add in/outfile and append to our dictionary
        parts = {"input":None,"cmd":None,"params":[],"flags":None, "infile": None, "outfile": None, "append": None}
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
            elif part.startswith("-"):
                parts["flags"] = part[1:]
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
    sys.stdout.write("\r" + prompt + cmd)
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
- lists the entire working directory
'''
def ls(parts):
    '''
    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    input = parts.get("input",None)
    flags = parts.get("flags",None) or ""
    params = parts.get("params",None) or []

    # determine which directory to list
    if len(params) > 0:
        # use a specified directory
        directory = params[0]
    else:
        # use the current directory
        directory = "."

    try:
        # get a list of files in the current directory
        files = os.listdir(directory)

        # handles -a flag
        if 'a' in flags:
            # show all files, including hidden ones
            files = os.listdir(directory)
        else:
            # hide files that start with a dot
            files = os.listdir(directory)
            files = [f for f in files if not f.startswith('.')]

        # sorts the files alphabetically
        files.sort()

        # handles -l flag
        if 'l' in flags:
            # long format with file details
            output_lines = []
            for file in files:
                filepath = os.path.join(directory, file)
                try:
                    stat_info = os.stat(filepath)
                    size = stat_info.st_size

                    if 'h' in flags:
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

                    # deternmine if it is a directory or file
                    file_type = "d" if os.path.isdir(filepath) else "-"
                    output_lines.append(f"{file_type}rwxr-xr-x {size_str:>8} {file}")
                except OSError:
                    output_lines.append(f"?--------- {'?':>8}  {file}")
            ouput = "\n".join(output_lines)
        else:
            # short format with just file names
            ouput = "  ".join(files)

        return {"output":ouput, "error":None}

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
    '''
    allows the user to delete a file/directory by passing its name.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    params = parts.get("params",None) or []
    flags = parts.get("flags",None) or ""

    if not params:
        return {"output": None, "error": "rm: missing operand"}

    try:
        for path in params:
            # remove a single file, stand-alone or within a directory
            if os.path.isfile(path):
                os.remove(path)

            # recursive rm, with -r flag set
            elif os.path.isdir(path): # if the parameter is a directory, recursively delete
                if 'r' in flags:
                    for files in os.listdir(path):
                        shutil.rmtree(path) # removes entire "tree" of files

            # if the file/directory doesn't exits, print error message
            else: 
                return {"output": None, "error": f"rm: cannot remove '{path}': No such file or directory"}

            return {"output":None, "error":None}

    except FileNotFoundError:
        return {"output":None, "error":f"rm:{source}: There is no such file exixts"}
    except PermissionError:
        return{"output":None, "error":f"rm:permission denied"}
    except Exception as e:
        return{"output":None, "error":f"rm:{str(e)}"} 

'''
cat:
allows the user to view the contents of a file
'''
def cat(parts):
    """
    cat command: prints the contents of a file
    """
    params = parts.get("params") or []
    if not params:
        return {"output": None, "error": "cat: missing file operand"}
    
    filename = params[0]
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return {"output": f.read(), "error": None}
    except FileNotFoundError:
        return {"output": None, "error": f"cat: {filename}: No such file"}
    except PermissionError:
        return {"output": None, "error": f"cat: {filename}: Permission denied"}
    except Exception as e:
        return {"output": None, "error": f"cat: {str(e)}"}


'''
mv:
moves files/directories to a different location and renames files
'''
def mv(parts):
    '''
    moves files/directories to a different location and renames files.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
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

def wc(parts):
    '''
    counts the total number of words in a file.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    params = parts.get("params") or []

    if not params:
        return{"output": None, "error": "wc:missing the command"}

    filename = params[0]

    try: 
        with open(filename, "r", encoding="utf -8")as f:
            text = f.read()
            word_count = len(text.split())
            return{"output": f"{word_count} of {filename} is :", "error": None}
    except FileNotFoundError:
        return{"output":None, "error":f"wc:{filename}: no such file or file does not exists"}
    except PermissionError:
        return{"output":None, "error": f"wc:{filename}:Permission denied"}                

'''sort:
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

    params =parts.get("parts") or[] 

    if not params:
        return {"output": None, "error":"less:missing file operand"}
    
    filename =params[0]

    try:
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()

        #show file content 20 lines at a time
        page_size = 20

        for i in range(0,len(lines), page_size):
            chunk = lines[i:i +page_size]
            for line in chunk:
                print(line.rstrip())  #it prints without extra newlines

            user_input =input("--for more-- (enter to continue, press'q' to quit)")
            
            if user_input.lower() == "q":
                
                break 
        return {"output": None, "error": None}
    
    except FileNotFoundError:
        return {"output": None, "error":f"cat:{filename} No such file"}
    except PermissionError:
        return{"output":None, "error":f"rm:permission denied"}
    except Exception as e:
        return{"output":None, "error":f"rm:{str(e)}"}
    

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
    '''
    runs a search on a file or through input.

    input: dict: {"input":string,"cmd":string,"params":list,"flags":string}
    output dict: {"output":string,"error":string}
    '''
    params = parts.get("params") or []
    input_text = parts.get("input")

    # if grep doesn't have parameters, error message
    if not params:
        return {"output": None, "error": "grep: missing search pattern"}

    # the string to match
    to_match = params[0]
    output_lines = []

    # if there is input text
    if input_text:
        # split the lines
        lines_to_search = input_text.splitlines()
        for line in lines_to_search:
            # if the string to match is in a line, append it
            if to_match in line:
                output_lines.append(line)

    elif len(params) > 1:
        # grab the next parameter
        filename = params[1]
        try:
            with open(filename, "r", encoding = "utf-8") as f:
                # for each line in the file
                for line in f:
                    # if the string matches in a line
                    if to_match in line:
                        # append to the output
                        output_lines.append(line.rstrip("\n"))
        except FileNotFoundError:
            return {"output": None, "error": f"grep: {filename}: No such file or directory"}
    else:
        return {"output": None, "error": "grep: no input or file specified"}

    return {"output": "\n".join(output_lines), "error": None}
    


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
piping: 
handles piping of commands as well as redirects
'''
def piping(command_list):
    prev_output = None
    results = []

    # handles redirection if requested
    for cmd_dict in command_list:
        if cmd_dict.get("infile"):
            try:
                with open(cmd_dict["infile"], "r", encoding = "utf-8") as f:
                    cmd_dict["input"] == f.read()
            except FileNotFoundError:
                return {"output": None, "error": f"{cmd_dict['cmd']}: {cmd_dict['input_file']}: No such file"}

        # piping the last output command
        if prev_output is not None:
            cmd_dict["input"] = prev_output
    
    # executes the command
    result = execute_command(cmd_dict)

    # grab the outfile
    if cmd_dict.get("outfile"):
        # grab the output
        if cmd_dict.get("output"):
            # change to append mode
            mode = "a"
        else:
            # change to write mode
            mode = "w"
        # open the output file
        with open(cmd_dict["outfile"], mode, encoding = "utf-8") as f:
            if result.get("output"):
                # write to the output file
                f.write(result["output"] + "\n")
    else:
        prev_output = result["output"]

    results.append(result)

    # return the results
    if results:
        return results[-1]
    else:
        return {"output": None, "error": None}

'''
execute_command(command_dict)
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



if __name__ == "__main__":
    cmd_list = parse_cmd("ls Assignments -lah | grep '.py' | wc -l > output")
    print(cmd_list)
    cmd = ""  # empty cmd variable

    cmd_history = []    # list containing commands previously used

    print_cmd(cmd)  # print to terminal

    while True:  # loop forever

        char = getch()  # read a character (but don't print)

        if char == "\x03" or cmd == "exit":  # ctrl-c
            raise SystemExit("\nBye.")

        elif char == "\x7f":  # back space pressed
            cmd = cmd[:-1]
            print_cmd(cmd)

        elif char in "\x1b":  # arrow key pressed
            null = getch()  # waste a character
            direction = getch()  # grab the direction

            if direction in "A":  # up arrow pressed
                # get the PREVIOUS command from your history (if there is one)
                # prints out 'up' then erases it (just to show something)
                cmd += "\u2191"
                print_cmd(cmd)
                sleep(0.3)
                # cmd = cmd[:-1]

            if direction in "B":  # down arrow pressed
                # get the NEXT command from history (if there is one)
                # prints out 'down' then erases it (just to show something)
                cmd += "\u2193"
                print_cmd(cmd)
                sleep(0.3)
                # cmd = cmd[:-1]

            if direction in "C":  # right arrow pressed
                # move the cursor to the right on your command prompt line
                # prints out 'right' then erases it (just to show something)
                cmd += "\u2192"
                print_cmd(cmd)
                sleep(0.3)
                # cmd = cmd[:-1]

            if direction in "D":  # left arrow pressed
                # moves the cursor to the left on your command prompt line
                # prints out 'left' then erases it (just to show something)
                cmd += "\u2190"
                print_cmd(cmd)
                sleep(0.3)
                # cmd = cmd[:-1]

            print_cmd(cmd)  # print the command (again)

        elif char in "\r":  # return pressed
            # Save the current command before processing
            user_input = cmd.strip()

            # Executes the !x command
            if user_input:
                list_num = exclamation(user_input)
                if list_num:
                    user_input = list_num

            # Save command entered to history list
            cmd_history.append(user_input)

            if user_input:  # Only process if there's actually a command
                # Show execution message
                cmd = "Executing command...."
                print_cmd(cmd)
                sleep(0.5)
                
                # Parse the command into structured format
                command_list = parse_cmd(user_input)
                
                # Handles piping, when it didn't before
                if command_list:
                    result = piping(command_list)
                    
                    # Display the result
                    print()  # New line after command
                    if result["output"]:
                        print(result["output"])
                    if result["error"]:
                        print(f"Error: {result['error']}")

            cmd = ""  # reset command to nothing (since we just executed it)
            print_cmd(cmd)  # now print empty cmd prompt
        else:
            cmd += char  # add typed character to our "cmd"

            print_cmd(cmd)  # print the cmd out


