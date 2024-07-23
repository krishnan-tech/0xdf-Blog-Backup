# update-alternatives

[linux](/tags#linux ) [update-alternatives](/tags#update-alternatives )
[nc](/tags#nc ) [java](/tags#java ) [namei](/tags#namei ) [bash](/tags#bash )  
  
Mar 24, 2020

update-alternatives

![](../img/Linux.png)

Debian Linux (and its derivatives like Ubuntu and Kali) has a system called
alternatives that’s designed to manage having different version of some
software, or aliasing different commands to different versions within the
system. Most of the time, this is managed by the package management system.
When you run apt install x, it may do some of this behind the scenes for you.
But there are times when it is really useful to know how to interact with this
yourself. For example, I’m currently working on a challenge that requires
using an older version of Java to interact with a file. I’ll use update-
altneratives to install the new Java version, and then to change what version
java, javac, jar, etc utilize.

## Example: nc

### Background

`nc` is the Swiss Army knife of hacking at things. There’s a more powerful
version, `ncat`, that brings in additional functionality, like SSL support,
IPv6 support, and proxy support. If you’ve ever installed ncat, you may have
noticed that running `nc` actually now runs `ncat`. This is managed by the
alternatives system.

### Before and After Install ncat

In a clean Kali install, `nc` is simply `nc` (actually `nc.traditional`, as
I’ll show in a moment). If I run `update-alternatives` with the `--display`
option, I can see that there is a symbolic link at `/bin/nc`, and it points
currently to `/bin/nc.traditional`:

    
    
    root@kali# update-alternatives --display nc
    nc - auto mode
      link best version is /bin/nc.traditional
      link currently points to /bin/nc.traditional
      link nc is /bin/nc
      slave nc.1.gz is /usr/share/man/man1/nc.1.gz
      slave netcat is /bin/netcat
      slave netcat.1.gz is /usr/share/man/man1/netcat.1.gz
    /bin/nc.traditional - priority 10
      slave nc.1.gz: /usr/share/man/man1/nc.traditional.1.gz
      slave netcat: /bin/nc.traditional
      slave netcat.1.gz: /usr/share/man/man1/nc.traditional.1.gz
    

I can run a listener, and connect to it and then exit:

    
    
    root@kali# nc -lnvp 443
    listening on [any] 443 ...
    connect to [127.0.0.1] from (UNKNOWN) [127.0.0.1] 46698
    

Now I’ll run `apt install ncat`. If I do the same thing, I get the `ncat`
status strings:

    
    
    root@kali# nc -lnvp 443
    Ncat: Version 7.80 ( https://nmap.org/ncat )
    Ncat: Listening on :::443
    Ncat: Listening on 0.0.0.0:443
    Ncat: Connection from 127.0.0.1.
    Ncat: Connection from 127.0.0.1:46710.
    

The `--display` option now shows the new alternative added:

    
    
    root@kali# update-alternatives --display nc
    nc - auto mode
      link best version is /usr/bin/ncat
      link currently points to /usr/bin/ncat
      link nc is /bin/nc
      slave nc.1.gz is /usr/share/man/man1/nc.1.gz
      slave netcat is /bin/netcat
      slave netcat.1.gz is /usr/share/man/man1/netcat.1.gz
    /bin/nc.traditional - priority 10
      slave nc.1.gz: /usr/share/man/man1/nc.traditional.1.gz
      slave netcat: /bin/nc.traditional
      slave netcat.1.gz: /usr/share/man/man1/nc.traditional.1.gz
    /usr/bin/ncat - priority 40
      slave nc.1.gz: /usr/share/man/man1/ncat.1.gz
      slave netcat: /usr/bin/ncat
      slave netcat.1.gz: /usr/share/man/man1/ncat.1.gz
    

There’s a second alternative, `ncat`, and it has a higher priority than the
previous option, and it is currently what `/bin/nc` points to.

### Tracing Links

To dig in one more level, I’ll look at what’s actually at `/bin/nc`. `namei`
is a good utility to see this:

    
    
    root@kali# namei /bin/nc
    f: /bin/nc
     d /
     l bin -> usr/bin
       d usr
       d bin
     l nc -> /etc/alternatives/nc
       d /
       d etc
       d alternatives
       l nc -> /usr/bin/ncat
         d /
         d usr
         d bin
         - ncat
    

`namei` starts at `/` in the given path, and traces down what it finds,
following links. Interestingly, this shows that `/bin` is actually a symbolic
link to `/usr/bin` (I didn’t know that before working on this post). Then it
reached `/usr/bin/nc`, which it finds is a link to `/etc/alternatives/nc`. It
will then find that is a link to `/usr/bin/ncat`.

I can see those same links with ls is that’s more familier:

    
    
    root@kali# ls -l /bin/nc
    lrwxrwxrwx 1 root root 20 Feb 21 20:57 /bin/nc -> /etc/alternatives/nc
    root@kali# ls -l /etc/alternatives/nc
    lrwxrwxrwx 1 root root 13 Mar 20 09:29 /etc/alternatives/nc -> /usr/bin/ncat
    

I wanted a slightly cleaner way to visualize the links, so I creates a small
function in my `.bashrc` file:

    
    
    function tracelnk () {
        namei $1 | grep -E -e "^\s+l " -e "^f"
    }
    

Running that just shows the root file and the links:

    
    
    root@kali# tracelnk /bin/nc
    f: /bin/nc
     l bin -> usr/bin
     l nc -> /etc/alternatives/nc
       l nc -> /usr/bin/ncat
    

### Changing Alternative

Now that I have these options install, how do I change between them? I’ll use
the `--config` option:

    
    
    root@kali# update-alternatives --config nc
    There are 2 choices for the alternative nc (providing /bin/nc).
    
      Selection    Path                 Priority   Status
    ------------------------------------------------------------
    * 0            /usr/bin/ncat         40        auto mode
      1            /bin/nc.traditional   10        manual mode
      2            /usr/bin/ncat         40        manual mode
    
    Press <enter> to keep the current choice[*], or type selection number: 1
    update-alternatives: using /bin/nc.traditional to provide /bin/nc (nc) in manual mode
    

Above, it presents three options. The first is `auto` mode, saying take the
option with the highest priority. The next two are manually setting which one
I want. I entered `1`, so it switched to `nc.traditional`. I can see the link
in `/etc` has updated:

    
    
    root@kali# tracelnk /bin/nc
    f: /bin/nc
     l bin -> usr/bin
     l nc -> /etc/alternatives/nc
       l nc -> /bin/nc.traditional
         l bin -> usr/bin
    

I’ll run it again and select option 0 to go back to auto for nc.

## Java

### Background / Starting Status

The challenge that got me on this path involved a Java Jar file that was
created with Java 8. I can see that I actually already have a version of Open
JDK 8 on Kali:

    
    
    root@kali# update-alternatives –display java 
    java - auto mode
     link best version is /usr/lib/jvm/java-11-openjdk-amd64/bin/java
     link currently points to /usr/lib/jvm/java-11-openjdk-amd64/bin/java
     link java is /usr/bin/java
     slave java.1.gz is /usr/share/man/man1/java.1.gz 
    /usr/lib/jvm/java-11-openjdk-amd64/bin/java - priority 1111
     slave java.1.gz: /usr/lib/jvm/java-11-openjdk-amd64/man/man1/java.1.gz 
    /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java - priority 1081
     slave java.1.gz: /usr/lib/jvm/java-8-openjdk-amd64/jre/man/man1/java.1.gz
    

`java` is currently in auto, with the openjdk version 11 having the highest
priority.

### Install Oracle Java 8

I could tell `update-alternatives` to use that Open JDK 8, but I want to grab
the actual Oracle Java version. I downloaded it
[here](https://www.oracle.com/java/technologies/javase-jdk8-downloads.html).
It’s a tar archive. Given the folder structure that already exists, I’ll
decompress is into `/usr/lib/jvm` with the others:

    
    
    root@kali# ls /usr/lib/jvm/
    default-java  java-1.11.0-openjdk-amd64  java-11-openjdk-amd64  java-1.8.0-openjdk-amd64  java-8-openjdk-amd64  jdk1.8.0_241
    

Now `--install` will create an alternative option for this version:

    
    
    root@kali# update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk1.8.0_241/bin/java 1082
    

The arguments there are the link file to use, the name of the command, the
path to the actual binary, and the desired priority.

This version now shows up as an alternative when I run `--config`:

    
    
    t@kali:/# update-alternatives --config java
    There are 3 choices for the alternative java (providing /usr/bin/java).
    
      Selection    Path                                            Priority   Status
    ------------------------------------------------------------
    * 0            /usr/lib/jvm/java-11-openjdk-amd64/bin/java      1111      auto mode
      1            /usr/lib/jvm/java-11-openjdk-amd64/bin/java      1111      manual mode
      2            /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java   1081      manual mode
      3            /usr/lib/jvm/jdk1.8.0_241/bin/java               1082      manual mode
    
    Press <enter> to keep the current choice[*], or type selection number:
    

There are other binaries in the JDK that I’ll want to add as well, like `jar`
and `javac`. Unfortunately, those each have to be managed independently.

## Conclusion

`update-alternatives` is a neat little utility to understand if you have to
work with some older versions of software. I hadn’t really understood how it
worked before digging in for this challenge and this post, but now I see it as
something I’ll use in the future.

[](/2020/03/24/update-alternatives.html)

