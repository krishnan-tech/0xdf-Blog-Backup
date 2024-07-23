# Commando VM: Lessons Learned

[home-lab](/tags#home-lab ) [commando](/tags#commando )
[fireeye](/tags#fireeye ) [smb](/tags#smb ) [net-view](/tags#net-view ) [net-
use](/tags#net-use ) [firewall](/tags#firewall ) [python](/tags#python )
[winrm](/tags#winrm ) [responder](/tags#responder ) [htb-ethereal](/tags#htb-
ethereal )  
  
Apr 15, 2019

  * [Installation](/2019/04/09/commando-vm-installation.html)
  * [Looking Around](/2019/04/10/commando-vm-overview.html)
  * Lessons Learned

![](https://0xdfimages.gitlab.io/img/commando-lessons-cover.png) I worked a
HackTheBox target over the last week using CommandoVM as my attack station. I
was pleasantly surprised with how much I liked it. In fact, only once on this
box did I need to fire up my Kali workstation. Because the target was Windows,
there we parts that were made easier (and in one case made possible!). There
were a couple additional struggles that arose, and I’m still in search of a
good tmux equivalent. I’ll walk through some of the lessons learned from
working in this distro.

## SMB

### Enumeration

On Linux, I use all sorts of tools to enumerate SMB (in fact my [blog post on
SMB enum](/2018/12/02/pwk-notes-smb-enumeration-checklist-update1.html) is the
most visited page on this site). But none of them were on Commando. Then I
realized I can use the Windows native tools.

#### net

I can use `net view [ip]` to get a listing of shares. For example, on one
host, where I can’t list any shares without auth, I get this:

    
    
    C:\>net view [ip]
    System error 5 has occurred.
    
    Access is denied.
    

On another machine, I get:

    
    
    C:\>net view [ip]
    Shared resources at [ip]
    
    Share name         Type  Used as  Comment
    
    -------------------------------------------------------------------------------
    CertEnroll         Disk           Active Directory Certificate Services share
    Department Shares  Disk
    NETLOGON           Disk           Logon server share
    Operations         Disk
    SYSVOL             Disk           Logon server share
    The command completed successfully.
    

I can use `net use` to connect to shares as well.

#### Explorer

I could also use Windows Explorer. I enter `\\[ip]` into the location bar. For
the first one that denied me access, I get a prompt for creds:

![1555361561609](https://0xdfimages.gitlab.io/img/1555361561609.png)

For the second one above, I get a list of shares:

![1555361673368](https://0xdfimages.gitlab.io/img/1555361673368.png)

### Transport

I also really like [SMB as a transport to and from target](2018-10-11-pwk-
notes-post-exploitation-windows-file-transfers). From Kali, I’d do that with a
temporary SMB server with `smbserver.py`. From Windows, I can set up an actual
SMB share.

#### Setup

First, because I run as administrator in my VM, I want to use a different user
to connect to this share. So I created another user, dummy, in control panel.
I gave dummy a good password.

Next, I created a folder in `c:\` called `share`. I opened the folder
properties, and first, under security, made sure both administrators (me) and
dummy had full control over the folder.

![1555362445818](https://0xdfimages.gitlab.io/img/1555362445818.png)

Then I went into “Sharing” -> “Advanced Sharing” and checked “Share this
folder”. I left the name as “share”, and clicked “Permissions”. I removed all
users, and added dummy:

![1555362515417](https://0xdfimages.gitlab.io/img/1555362515417.png)

Now the share is ready to go. I can drop `nc.exe` or other tools in there I
may want to move to target.

#### Connecting

With a shell on target, I can now connect to the share on CommandoVM with `net
use`. I’ll just make sure to include dummy’s username and password:

    
    
    [hostname]: PS C:\Users\[username]\Documents> net use /u:dummy \\10.10.14.14\share [password]
    The command completed successfully.
    

Now I can check out the share, and copy to and from it:

    
    
    [hostname]: PS C:\Users\[username]\Documents> dir \\10.10.14.14\share
    
    
        Directory: \\10.10.14.14\share
    
    
    Mode                LastWriteTime         Length Name
    ----                -------------         ------ ----
    -a----        4/10/2019  10:44 PM        7613952 chisel_windows_amd64.exe
    -a----        9/17/2011  12:52 AM          38616 nc.exe
    -a----        9/17/2011  12:52 AM          45272 nc64.exe
    -a----        4/12/2019   1:54 PM          37641 powercat.ps1
    

## Windows Firewall

I spent a long time thinking the box I was working was locked down like
[Ethereal](/2019/03/09/htb-ethereal.html) because I couldn’t get anything to
connect to my `python -m http.server`. In reality, connections were getting
out fine, but it was my firewall blocking them. Many programs will prompt when
I start to listen on a new port to ask if I want to open the firewall. But
something like `python -m http.server` typically doesn’t (also note, as I
mentioned in the previous, `python` runs version 3, so `http.server` instead
of `SimpleHTTPServer`). So I need to make sure that the firewall is open (this
cost me more hours than I’m proud to admit).

I decided to just add my own rule in the Advanced Settings that allows 80 and
443 in:

![1555363073912](https://0xdfimages.gitlab.io/img/1555363073912.png)

If I were working a box like Ethereal, where I needed to try to connect out on
every port with the hopes of finding one, I would take the firewall down all
together for that test. If you’re feeling paranoid, take a snapshot, take the
firewall down, run the test, then revert once you the results.

## WinRM

I’ve typically used [Alamot’s WinRM ruby
scripts](https://github.com/Alamot/code-snippets/tree/master/winrm) to get a
WinRM shell from Kali. They are fine, and `rlwrap` makes the experience
livable. That said, the experience is _so_ much better in a true PowerShell
connection.

### Setup

In order to connect over WinRM to another computer, there is some setup and
configuration that must be done. Much of this is to tell Windows you’re ok
trusting this computer.

  1. Add host to `c:\windows\system32\drivers\etc\hosts`. Windows is used to doing things by hostname.
  2. I’ll need to start the “Windows Remote Management Service” if it isn’t already running. Running `winrm quickconfig` from `cmd` is a simple way to take care of this.
  3. Add all hosts to the trusted hosts list with `winrm set winrm/config/client @{TrustedHosts="*"}`. This would be a terrible configuration for any real life box, but will be fine for my hacking box. If I wanted to be more secure, I could replace `*` with the hostname.
  4. Enable CredSSP. This will allow me to connect with `-authentication CredSSP` later. In PowerShell, run `Enable-WSManCredSSP -Role "Client" -DelegateComputer "*"`. Another case where I could replace`*` with the hostname in a real situation.
  5. Open local group policy (`gpedit.msc`) and got to “Computer Configuration” -> “Administrative Templates” -> “System” -> “Credential Delegation” -> “Allow delegating fresh credentials with NTLM only server authentication”. Make sure it’s enabled, and then click “Show” and add “WSMAN/[hostname]”.

The last two steps were specific to CredSSP authentication, so if I’m not
going to use that, I don’t need them. That said, CredSSP allows me access to
additional things like EFS encrypted files, so I’m going to want it.

### Connection

To connect, I just run `Enter-PSSession`, and give it the password when it
prompts:

    
    
    PS C:\ > Enter-PSSession -ComputerName [hostname] -Credential [hostname]\[username]
    
    Windows PowerShell credential request
    Enter your credentials.
    Password for user [hostname]\[username]: ******************
    
    [hostname]: PS C:\Users\[username]\Documents>
    

This shell has tab completion and up arrow for history. It’s quite pleasant to
work from. Tab-completion is especial useful in PowerShell, since it has such
verbose commandlet names. The shell can lag from time to time, not nothing too
unusual.

If I’m going to be connecting multiple times, or want to script connection, I
can also create a PowerShell `PSCredential` object using the following
template, assuming `$username` and `$password` are already set:

    
    
    $secure = ConvertTo-SecureString -AsPlainText $Password -Force
    $user = New-Object -TypeName System.Management.Automation.PSCredential
    -ArgumentList $username,$secure
    Enter-PSSession -ComputerName [hostname] -Credential $user
    

This is useful working a box over the course of a couple days and not wanting
to look up the user’s password over and over.

There’s also the ability to create a stateful session with something like
`$session = New-Pssession -ComputerName [host] -Credential [credential]`. Then
you can `Enter-PSSession` that session. You can also load local scripts into
that session, and other cool stuff.

## Tools

### Additional Installs

There will definitely be more tools to bring. I started creating more folders
in `c:\tools\` and adding things there. Some stuff to consider:

  * `nc` \- <https://eternallybored.org/misc/netcat/>
  * `powercat.ps1` \- <https://github.com/besimorhino/powercat>
  * `chisel` \- <https://github.com/jpillora/chisel/releases>

For git repos, downloading is as simple as Kali - just go to the directory the
folder should live in, and `git clone [url from GitHub]`.

### Stuff Already There

I was excited a couple of times where I went to get something off the internet
only to realize it was already there (like
[Nishang](https://github.com/samratashok/nishang)).

I also really liked having access to Visual Studio. I wanted to try the [COR
Profiler](/2019/03/15/htb-ethereal-cor.html) technique, but needed a new dll.
It felt like kind of a long shot, and having to boot into a different VM might
have caused me to put off trying. But having Visual Studio right there made it
such that I had a dll reverse shell 2 minutes later!

## Responder

There is a version of [responder that runs on
Windows](https://github.com/lgandx/Responder-Windows), but in a less than
exhaustive effort, I couldn’t get it to run. Eager to see if it was even going
to be useful on the box I was working, I switched over to Kali (and found it
wasn’t). I may revisit at some point. I’d be curious if anyone has
successfully run this thing. I couldn’t find any writing about it other than
the GitHub page.

[@mcohmi](https://twitter.com/mcohmi) pointed out that
[Inveigh](https://github.com/Kevin-Robertson/Inveigh) does this, and it is
already installed on CommandoVM. I’ll check that out sometime soon hopefully.

## Conclusion

### Overall Experience

I was quite surprised by how much I liked working a HTB target from a Windows
VM. I might try it again next Windows machine I work. The biggest thing I
didn’t like was the terminal situation. I miss `tmux` so much. `cmder` just
isn’t doing it for me yet, and I spent most of my time working out of
individual PowerShell and Cmd windows. That said, having tab completion on a
WinRM session was _huge_. So nice. I’d definitely recommend giving this a try
if you have time to build the VM and play with it.

### Next Steps

Moving forward, I may be jumping back and forth between Kali and CommandoVM.
Having a Windows machine as part of the tool set I use regularly will make
life easier. It would be nice if I could have both connected to HTB at the
same time. I might have to investigate if there’s a way to set up one of my
VMs (I’m assuming Kali) as a router that I can then have the other route
traffic through, including into the VPN. If I do, I’ll certainly write about
it. If you have ideas, please comment or hit me up on Twitter/Slack/NSF.

[« Looking Around](/2019/04/10/commando-vm-overview.html)

[](/2019/04/15/commando-vm-lessons.html)

