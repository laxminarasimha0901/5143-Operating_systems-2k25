# 5143 Advanced Operating Systems
#### Shell Project - Implementation of a Basic Shell
#### Group Members: Jadyn Dangerfield, Andrew Huff, Laxminarasimha Soma
#### jadangerfield0515@my.msutexas.edu
#### adhuff0205@my.msutexas.edu
#### lsoma0109@my.msutexas.edu

## Overview
##### In this project, we implemented a basic shell using Python. Below, we have listed the assignment rubric which includes who worked on each command, and whether or not they were completed.
|    #    | Item                                                   |  Who Worked on it  | Done? |
| :-----: | ------------------------------------------------------ | :----------------: | :---: |
| **_1_** | **_Commands_**                                         ||        |
|    1    | _ls -lah_                                              |Jadyn|✔      |
|    2    | _mkdir bananas_                                        |Andrew|✔       |
|    3    | _cd bananas_                                           |Jadyn|✔        |
|    4    | _cd .._                                                |Jadyn|✔        |
|    5    | _cd ~_                                                 |Jadyn|✔        |
|    6    | _pwd_                                                  |Jadyn|✔      |
|    7    | _mv somefile.txt bananas_                              |Soma| ✔       |
|    8    | _cp bananas/somefile.txt somefile/otherfile.txt_       |Andrew|✔      |
|    9    | _rm -rf bananas_                                       |Andrew| ✔      |
|   10    | _cat file(s)_                                          |Soma|  ✔      |
|   11    | _less somefile_                                        |Soma|   ✔     |
|   12    | _head somefile -n 10_                                  |Jadyn|✔        |
|   13    | _tail somefile -n 10_                                  |Jadyn|✔        |
|   14    | _grep -lic bacon bacon.txt , ham.txt_                  |Andrew|   ✔    |
|   15    | _wc -w bacon.txt_                                      |Soma| ✔       |
|   16    | _history_                                              |Andrew|  ✔     |
|   17    | _!x_                                                   |Andrew|  ✔     |
|   18    | _chmod 777 somefile.txt_                               |Soma|     ✔   |
|   19    | _sort bacon.txt_                                       |Soma|✔       |
|   20    | _Command of your choice_                               |Andrew|✔        |
| **_2_** | **_Piping_**                                           |Andrew|   ✔     |
|         | Similar to (but open for me to choose command):        ||        |
|         | _grep bacon bacon.txt \| wc -l_                        ||        |
| **_3_** | **_Redirection_**                                      |Andrew|   ✔     |
|         | Similar to (but open for me to choose):                ||        |
|         | _cat file1 file2 > file0_                              ||        |
| **_4_** | **_General_**                                          |All Members|
|         | Prompt line acts correct (cleans command etc.)         ||        |
|         | Arrow keys work                                        ||        |
|         | Items were not printed to the screen unnecessarily     ||        |
|         | Too many messages (like successful .....) weren't used ||        |
|         | Program did not crash or need restarted                ||        |

## Instructions
#### To run this shell, you must execute the following:
#### 1. Ensure access to the repository
#### 2. Switch over to the Files directory
#### 3. Type the command "python shell.py"
#### 
#### Now that the program is running, similarly use it to navigate the emulated terminal!

## Incomplete Features
#### In this project, we had a couple of incomplete features.
#### 1. Not all commands have their appropriate flags running
#### 2. Arrow keys do not navigate to previous commands, and vice versa
#### 3. Help command does not print the actual command, but rather displays its associated docstring

## References
#### Our references used were as follows:
#### 1. GeeksforGeeks
#### 2. Stackoverflow (whoami)
#### 3. Chatgpt
