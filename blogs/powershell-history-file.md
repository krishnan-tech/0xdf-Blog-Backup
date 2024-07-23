# PowerShell History File

[powershell](/tags#powershell ) [psreadline](/tags#psreadline )
[history](/tags#history )  
  
Nov 8, 2018

PowerShell History File

I came across a situation where I discovered a user’s PSReadline
ConsoleHost_history.txt file, and it ended up giving me the information I
needed at the time. Most people are aware of the `.bash_history` file. But did
you know that the PowerShell equivalent is enabled by default starting in
PowerShell v5 on Windows 10? This means this file will become more present
over time as systems upgrade.

## PSReadline

The PSReadline module started as a stand-alone module, but became the default
command line editing experience starting in PowerShell v3. A full list of the
features are available on its [GitHub
page](https://github.com/lzybkr/PSReadLine). It is responsible for, among
other things, letting us hit up arrow to see previous commands from a
PowerShell window. To do this, it records what is typed into the console. It
can save this in memory, or to a file.

**Starting in PowerShell v5 on Windows 10, the default option is to save
history to a file**. This setting gives the user the ability to start a new
session with the history from the previous session.

## History File Information

The default location for this file is
`$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt`.
You can get the location by running `Get-PSReadlineOption` and looking at the
options. There’s a few history related ones:

  * `HistorySavePath` \- The file location
  * `HistorySaveStyle` \- Options are `SaveIncrementally`, which saves after each command; `SaveAtExit`, which appends on exiting PowerShell, or `SaveNothing`, which turns off the history file.
  * `MaximumHistoryCount` \- The max number of entries to record.

You can modify the options with the `Set-PSReadlineOption` commandlet.

## What the History File Records

Everything I type into a PowerShell window. For example:

    
    
    PS C:\> cd $env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\
    PS C:\Users\sansforensics408\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine> ls
    
    
        Directory: C:\Users\sansforensics408\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine
    
    
    Mode                LastWriteTime         Length Name
    ----                -------------         ------ ----
    -a----        11/8/2018   2:11 AM             62 ConsoleHost_history.txt
    
    
    PS C:\Users\sansforensics408\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine> type .\ConsoleHost_history.txt
    cd $env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\
    ls
    type .\ConsoleHost_history.txt
    

## What It Does Not Record

Terminal-less PowerShell sessions. So if I manage to get remote code execution
on a host and have it run a [Nishang Reverse
Shell](https://github.com/samratashok/nishang) or Meterpreter, nothing done
there is recorded in the file.

## Usefulness

For the red-teamer, this is a really interesting way to get information about
the commands the user has been running, and files they interact with, and
maybe even passwords. For the forensic analyst, having a history of a
subject’s actions can be invaluable, and having it in a file is gold. For a
blue teamer, this could be useful if you are very lucky, but you’re much
better off enabling script-block logging for PowerShell. Most of the things an
attacker does in PowerShell, unless they get RDP access, are not going to be
recorded. For HackTheBox, you may find some part of an intended path, or you
may find some history from the box’s creator who didn’t think or know to clear
history.

[](/2018/11/08/powershell-history-file.html)

