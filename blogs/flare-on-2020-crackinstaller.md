# Flare-On 2020: crackinstaller

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-
crackinstaller](/tags#flare-on-crackinstaller ) [reverse-
engineering](/tags#reverse-engineering ) [capcom-sys](/tags#capcom-sys )
[driver](/tags#driver ) [kernel-debug](/tags#kernel-debug )  
  
Nov 1, 2020

  * [[1] Fidler](/flare-on-2020/fidler)
  * [[2] garbage](/flare-on-2020/garbage)
  * [[3] wednesday](/flare-on-2020/wednesday)
  * [[4] report.xls](/flare-on-2020/report)
  * [[5] TKApp](/flare-on-2020/tkapp)
  * [[6] CodeIt](/flare-on-2020/codeit)
  * [[7] RE Crowd](/flare-on-2020/recrowd)
  * [[8] Aardvark](/flare-on-2020/aardvark)
  * [9] crackinstaller
  * [[10] break](/flare-on-2020/break)

![crackinstaller](https://0xdfimages.gitlab.io/img/flare2020-crackinstaller-
cover.png)

crackinstaller.exe was a complicated binary that installed the Capcom.sys
driver, and then exploited it to load another driver into memory. It also
dropped and installed another DLL, a credential helper. I used kernel
debugging to see how the second driver is loaded, and eventually find a
password, which I can feed into the credential helper to get the flag. I spent
over two of the six weeks working crackinstaller.exe, and unfortunately, I
stopped taking meaningful notes very early in that process, so this won’t be
much of a writeup, but rather a high level overview.

## Challenge

> What kind of crackme doesn’t even ask for the password? We need to work on
> our COMmunication skills.
>
>   * Bug Notice: Avoid a possible blue-screen by debugging this on a single
> core VM
>

    
    
    root@kali# file ttt2.exe 
    ttt2.exe: PE32+ executable (GUI) x86-64, for MS Windows
    

## Running It

I happened to be on a fresh Windows VM when I started this challenge, and on
trying to run this, Windows Defender blocked it. Looking at the logs, it is
calling this HackTool:Win64/CapRoot.A:

![image-20201001071135692](https://0xdfimages.gitlab.io/img/image-20201001071135692.png)

It also calls out `crackinstaller.exe` as a containerfile, with the file in
question being `cfs.dll`.

Once I disable defender, running it pops a blank terminal for a second, and
then it disappears.

## General Notes

### crackinstaller.exe

This binary drops a bunch of things. It has an init function that runs pre-
main that will drop the famous [Capcom.sys driver](https://www.exploit-
db.com/exploits/40451).

[![image-20201003065732553](https://0xdfimages.gitlab.io/img/image-20201003065732553.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201003065732553.png)

It then invokes the IOCTL call that basically loads user code into the kernel
and runs it. I worked through both videos in [this
post](http://www.fuzzysecurity.com/tutorials/28.html) and really learned a
ton. Highly recommend.

For this binary, after installing the vulnerable driver, it uses it to load
call code back in `crackinstaller.exe`:

    
    
    FUN_140002a10(?, 22B00BA7E00h, 5800h, 3170h)
    

In this function, there’s a lot of kernel memory pools functions to put a new
driver into memory and an array of kernel functions into a second pool. these
are passed to `PsCreateSystemThread`:

    
    
    PsCreateSystemThread(&hThread, GENERIC_ALL, 0x30, 0, 0, driver_in_memory.DriverBootloader, args[])
    

`DriverBootloader` basically does some memory re-arrangements and calls
`IoCreateDriver(NULL, entry)`.

After installing the driver, it continues in `main`, where it drops
`credhelper.dll` to disk:

[![image-20201003065412829](https://0xdfimages.gitlab.io/img/image-20201003065412829.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201003065412829.png)

Then it invokes the `DllRegisterServer` export.

### Unnamed Driver

I had to set up kernel debugging to see into the driver and what was
happening. To do this, as I’m on a Linux host, I created two Windows VMs, and
configured them according to [this
post](https://blahcat.github.io/2017/08/07/setting-up-a-windows-vm-lab-for-
kernel-debugging/).

The driver calls `CmRegisterCallbackEx` which will register a callback
function that will be invoked when the kernel conducts registry operations. It
took a bunch of documentation reading to understand the various structs passed
to this function, but eventually I figured out where the function that was
invoked would be.

The callback handler checks that the operation is happening on a path
containing `{CEEACC6E-CCB2-4C4F-BCF6-D2176037A9A7}\Config`. It’s not totally
clear to me what happens next, but a buffer is decrypted, and it contains what
I’ll find is the password, `H@n $h0t FiRst!` (a Star Wars reference).

Then it unloads the driver.

### credhelper.dll

This DLL exports four functions and a `main`:

![image-20201101123056018](https://0xdfimages.gitlab.io/img/image-20201101123056018.png)

The function called by `crackinstaller.exe` is `DllRegisterServer`. It
basically creates a COM server with the following API calls:

    
    
    RegCreateKeyExW(HKEY_CLASSES_ROOT, "CLSID\{CEEACC6E-CCB2-4C4F-BCF6-D2176037A9A7}", 0x0, 0x0, 0xf003f, 0x0, handle,)
    RegSetValueExW(handle, NULL, 0, REG_SZ (1), "CredHelper", )
    RegCreateKeyExW(handle, "InProcServer32", 0, 0, 0, 0xf003f, 0, hKey_InProcServer32, 0)
    RegCreateKeyExW(handle, "Config", 0, 0, 0, 0xf003f, 0, hKey_Config, 0)
    RegSetValue(hKey_InProcServer, NULL, 0, REG_SZ (1), fullpath_credhelper.dll, len(fullpath_credhelper.dll))
    RegSetValue(hKey_InProcServer, "ThreadingModel", 0, REG_SZ (1), "Apartment", len("Apartment"))
    

It then creates two more keys:

    
    
    RegSetValue(hKey_Config, "Password", 0, REG_SZ (1), [garbage], 2)
    RegSetValue(hKey_Config, "Flag", 0, REG_SZ (1), [garbage], 2)
    

I spent some time playing with and understanding these functions. There’s a
`getPassword` function (offset 153c) that reads the password out of the
password registry key, and generates crypto buffers in a global variable.
There’s also a `setFlag` function (offset 16d8) that uses the crypto buffer to
decrypt something, and then writes that to the flag registry key.

The fastest way to get a flag is to debug in `x64dbg` using `rundll32.exe`
(like [here](https://tomrocc.medium.com/reverse-engineering-tip-analyzing-a-
dll-in-x64dbg-b3005d516049)). It’s a bit hacky, but here’s the steps I took:

  * Set debug to break on DLL load and run through loading `credHelper.dll`.
  * Run through `DllRegisterServer` by setting RIP manually and breaking on the return.
  * Manually set the Password registry key to using `regedit.exe`.
  * Set RIP to `getPassword`, set RCX to 0, and RDX to some address way up on the stack that’s not currently in use. As I step through this, I see how the 256 bytes of crypto stuff is generated at the address I set into RDX.
  * Set RIP to `setFlag`, RCX to 0, and RDX to that buffer address on the stack. Step for a bit, and the flag pops out:

[![image-20201101125758217](https://0xdfimages.gitlab.io/img/image-20201101125758217.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201101125758217.png)

**Flag: S0_m@ny_cl@sse$_in_th3_Reg1stry@flare-on.com**

[](/flare-on-2020/crackinstaller)

