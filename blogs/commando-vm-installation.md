# Commando VM: Installation

[home-lab](/tags#home-lab ) [commando](/tags#commando )
[fireeye](/tags#fireeye ) [youtube](/tags#youtube )  
  
Apr 9, 2019

  * Installation
  * [Looking Around](/2019/04/10/commando-vm-overview.html)
  * [Lessons Learned](/2019/04/15/commando-vm-lessons.html)

![](https://0xdfimages.gitlab.io/img/commando-install-cover.png)Ever since
Fireeye announced their new CommandoVM, the “Complete Mandiant Offensive VM”,
I’d figured next time I had an occasion to target a Windows host, I would try
to build a VM and give it a spin. This post is focused on getting up and
running. I suspect additional posts on how it works out will follow.

## Background

### Why?

So what is Commando VM? From the Fireeye [release
blog](https://www.fireeye.com/blog/threat-research/2019/03/commando-vm-
windows-offensive-distribution.html):

> For penetration testers looking for a stable and supported Linux testing
> platform, the industry agrees that Kali is the go-to platform. However, if
> you’d prefer to use Windows as an operating system, you may have noticed
> that a worthy platform didn’t exist. As security researchers, every one of
> us has probably spent hours customizing a Windows working environment at
> least once and we all use the same tools, utilities, and techniques during
> customer engagements. Therefore, maintaining a custom environment while
> keeping all our tool sets up-to-date can be a monotonous chore for all.
> Recognizing that, we have created a Windows distribution focused on
> supporting penetration testers and red teamers.

Kali has been my go to for HackTheBox and CTFs because it has a lot of the
tools I need already configured. But when you target a Windows host, there are
times it is just more natural to use Windows.

### What?

So what is Commando-VM? It’s not actually a VM. You have to bring your own
Windows VM (7 or 10, preferably 10), and then use their scripts to download
and configure the VM to include the tools and resources that you might expect
as a Pentester / Red Teamer / CTF participant.

## Prerequisite

### Windows Install

I’m working out of VirtualBox, and I created a new VM, gave it 100GB harddrive
and 4 GB of ram.

To start, but made a Windows 10 VM. After install, I went into Windows update
and applied all updates, rebooted, repeated that cycle until Windows tells me
I’m up to date:

![1554751248458](https://0xdfimages.gitlab.io/img/1554751248458.png)

Once I’m finally there, my `winver` pop-up shows I’m running the 1809 update:

![1554750954065](https://0xdfimages.gitlab.io/img/1554750954065.png)

### Minor Customizations

I changed the computer name to “commando”.

I also installed the VirtualBox Guest Additions, so that I could map drives
and share my clipboard. After a reboot, I can verify that I can copy and paste
between my linux host and the VM.

While on any other Windows VM, I would immediate now jump to pinning `cmd` and
`powershell`, and installing Firefox, I want to give Commando a chance to do
it’s thing, so I’m going to leave that for later.

I’m going to make a snapshot here in case any thing breaks.

## Installation

### Download

I’ll open Edge and go to the [GitHub page for
Commando](https://github.com/fireeye/commando-vm). I’ll click on the green
“Clone or download” button, and select “download zip”. I’ll tell it to save in
my downloads, open Windows Explorer, right click on the file, and extract the
zip there.

### Set Execution Policy

Now I’ll open a PowerShell window by going to start, typing powershell, right
clicking on it, and selecting “Run as administrator”.

Now I need to set PowerShell so that I can run scripts. I’ll do that by
changing the execution policy:

    
    
    PS C:\users\0xdf\Downloads\commando-vm-master> Set-ExecutionPolicy Unrestricted
    
    Execution Policy Change
    The execution policy helps protect you from scripts that you do not trust. Changing the execution policy might expose
    you to the security risks described in the about_Execution_Policies help topic at
    https:/go.microsoft.com/fwlink/?LinkID=135170. Do you want to change the execution policy?
    [Y] Yes  [A] Yes to All  [N] No  [L] No to All  [S] Suspend  [?] Help (default is "N"): Y
    

### Run Commodo

I’ll `cd` into my downloads directory, and into the `commando-vm-master`
directory:

    
    
    PS C:\users\0xdf\Downloads\commando-vm-master> ls
    
    
        Directory: C:\users\0xdf\Downloads\commando-vm-master
    
    
    Mode                LastWriteTime         Length Name
    ----                -------------         ------ ----
    d-----         4/8/2019   8:25 PM                .github
    d-----         4/8/2019   8:25 PM                commandovm.win10.config.fireeye
    d-----         4/8/2019   8:25 PM                commandovm.win10.installer.fireeye
    d-----         4/8/2019   8:25 PM                commandovm.win10.preconfig.fireeye
    d-----         4/8/2019   8:25 PM                commandovm.win7.config.fireeye
    d-----         4/8/2019   8:25 PM                commandovm.win7.installer.fireeye
    -a----         4/8/2019   8:25 PM          81218 Commando.png
    -a----         4/8/2019   8:25 PM          10548 install.ps1
    -a----         4/8/2019   8:25 PM           9138 License.txt
    -a----         4/8/2019   8:25 PM          11801 README.md
    

I’ll run `install.ps`, which takes care of the configuration and installation.

    
    
    PS C:\users\0xdf\Downloads\commando-vm-master> .\install.ps1
    
    Security warning
    Run only scripts that you trust. While scripts from the internet can be useful, this script can potentially harm your
    computer. If you trust this script, use the Unblock-File cmdlet to allow the script to run without this warning
    message. Do you want to run C:\users\0xdf\Downloads\commando-vm-master\install.ps1?
    [D] Do not run  [R] Run once  [S] Suspend  [?] Help (default is "D"): R
    [+] Beginning install...
     ____________________________________________________________________________
    |                                                                            |
    |                                                                            |
    |        _________                                           .___            |
    |        \_   ___ \  ____   _____   _____ _____    ____    __| _/____        |
    |        /    \  \/ /  _ \ /     \ /     \\__  \  /    \  / __ |/  _ \       |
    |        \     \___(  <_> )  Y Y  \  Y Y  \/ __ \|   |  \/ /_/ (  <_> )      |
    |         \______  /\____/|__|_|  /__|_|  (____  /___|  /\____ |\____/       |
    |                \/             \/      \/     \/     \/      \/             |
    |                       C O M P L E T E  M A N D I A N T                     |
    |                            O F F E N S I V E   V M                         |
    |                                                                            |
    |                                  Version 1.0                               |
    |____________________________________________________________________________|
    |                                                                            |
    |                                  Developed by                              |
    |                                 Jake  Barteaux                             |
    |                               Proactive Services                           |
    |                                 Blaine Stancill                            |
    |                                   Nhan Huynh                               |
    |                    FireEye Labs Advanced Reverse Engineering               |
    |____________________________________________________________________________|
    
    [+] Checking if script is running as administrator..
            phenomenal cosmic powers
    [+] Checking to make sure Operating System is compatible
            Microsoft Windows 10 Pro supported
    [+] Checking if host has been configured with updates
            updates appear to be in order
    [+] Checking if host has enough disk space
            > 60 GB hard drive. looks good
    [-] Do you need to take a snapshot before continuing? Y/N N
            Continuing...
    [ * ] Getting user credentials ...
    
    Windows PowerShell credential request
    Enter your credentials.
    Password for user 0xdf:
    

It asks for my password here, which it needs because it will reboot several
times, and it wants to make this as seamless as possible, so that I can start
it, walk away, and not have to enter my password periodically.

### Commando Finishes

The install scripts took just under two hours for my VM (1:55). I recorded a
video speed up 30 times of the entire install:

At the end, it looks like this, with the PowerShell prompt remains open
waiting for you to exit (which is the expected behavior stated in the [blog
post](https://www.fireeye.com/blog/threat-research/2019/03/commando-vm-
windows-offensive-distribution.html)):

![1554814639683](https://0xdfimages.gitlab.io/img/1554814639683.png)

The Fireeye [blog post](https://www.fireeye.com/blog/threat-
research/2019/03/commando-vm-windows-offensive-distribution.html) shows a
CommandoVM desktop wallpaper, but mine didn’t get set. However, they recommend
a reboot, and on reboot, the wallpaper is set:

![1554815338281](https://0xdfimages.gitlab.io/img/1554815338281.png)

I also pinned Firefox to the taskbar, as a matter of personal preference.

One more snapshot, and time to get to work.

## Next Steps

I’m going to try to solve a box from [HackTheBox](https://www.hackthebox.eu/)
using this VM, and I’ll follow up with additional posts.

[Looking Around »](/2019/04/10/commando-vm-overview.html)

[](/2019/04/09/commando-vm-installation.html)

