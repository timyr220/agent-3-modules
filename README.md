instruction on how to run the program on rasberri py 
1. add the program to the file you need 
2. Run the command - nohup python3 /path/to/script.py &
nohup - command to start a process that will not terminate when you close the terminal.
& - starts the process in the background.
The program logs will be written to the nohup.out file if you do not specify your own file for output:

then use this command nohup python3 /path/to/script.py > mylogfile.log 2>&1 &
To see the running processes, you can use the command: ps aux | grep python

After all these steps, use these commands to restart the process
tail -f nohup.out 
nohup python your_file &

Translated with DeepL.com (free version)
