# Home Lab On The Super Cheap - ESXi

[macpro](/tags#macpro ) [home-lab](/tags#home-lab ) [esxi](/tags#esxi )  
  
Jan 15, 2018

  * [Home Lab: The Hardware](/2018/01/15/home-lab-on-the-super-cheap-the-hardware.html)
  * Home Lab: ESXi

Getting the hypervisor installed is the next step.

## ESXI

I’ve selected ESXi because it’s free, and it allows me to manage multiple VMs
from a headless machine. I’ll be learning about it in future posts. But now
it’s time to get it running on my 2006 MacPro.

## Challenges with old MacPro

Were this some shiny new hardware, the post would be short. Download the iso,
burn it to disk, pop that disk and a USB drive into the machine, turn it on,
and install.

But while the MacPro 1,1 is a 64-bit machine, it runs off a 32-bit EFI
architecture, and unfortunately, ESXi stopped supporting 32-bit EFI a few
releases ago. There are several posts out there about how to do this that I
leaned on (1, 2 primarily).

## Installing ESXi on a 2006 MacPro

The general approach:

  1. Install ESXi on the USB using a VM
  2. Modify some of the boot files to work in the 32-bit EFI
  3. Move the USB over to the Mac Pro to boot

### Installing ESXi on the USB

While I typically use VirtualBox for almost everything, I actually had much
better luck getting the USB drive recognized in VMWare Player, so that’s what
I’ll show here.

In VMWare Player, Player -> New Virtual Machine. In the wizard, we’ll select
the ESXi 6.5 ISO.

![wiz](https://0xdfimages.gitlab.io/img/vmware-newvm-wiz1.png)

Continuing through the rest of the dialogs, making sure to give the machine at
least 4GB of ram. Hard disk size is irrelevant. When you’re done, boot the
machine.

While the machine is booting, we need to get our USB drive to be recognized by
the VM, by going to Player -> Removable Devices -> [USB Drive] -> Connect
(Disconnect from host). ![removable
media](https://0xdfimages.gitlab.io/img/removeable-media.png)

Then, when the ESXi installer boots, the USB drive should be one of the
options: ![install
drive](https://0xdfimages.gitlab.io/img/select_install_drive.png)

Select the USB drive, and continue with the installation, selecting a keyboard
layout and setting a good password. When you get to the reboot screen, hit
enter to let the VM shutdown. Once it restarts, you can shutdown (and delete)
the VM.

### Modifying the Boot Files

We’re going to mount the USB so we can interact with the files. First we’ll
use fdisk to find the device:

    
    
    $ sudo fdisk -l
    [snip...]
    Disk /dev/sdf: 14.3 GiB, 15376000000 bytes, 30031250 sectors
    Units: sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disklabel type: gpt
    Disk identifier: 016CA5E2-FC26-49B9-A82B-306F199BD187
    
    Device Start End Sectors Size Type
    /dev/sdf1 64 8191 8128 4M EFI System
    /dev/sdf5 8224 520191 511968 250M Microsoft basic data
    /dev/sdf6 520224 1032191 511968 250M Microsoft basic data
    /dev/sdf7 1032224 1257471 225248 110M unknown
    /dev/sdf8 1257504 1843199 585696 286M Microsoft basic data
    /dev/sdf9 1843200 7086079 5242880 2.5G unknown
    

We’ll grab the modified boot files from here:
https://communities.vmware.com/servlet/JiveServlet/download/2183936-108290/macpro%20efi%20boot%20files.zip

Mount the partition labeled EFI System. We’ve got 4 files to replace, from the
unzipped file:

    
    
    $ find . -type f
    ./EFI-BOOT/BOOTx64.EFI
    ./EFI-BOOT/BOOTIA32.EFI
    ./EFI-VMWARE/mboot64.efi
    ./EFI-VMWARE/mboot32.efi
    
    $ sudo mount /dev/sdf1 /mnt/
    $ ls /mnt/EFI/
    BOOT VMware
    
    $ sudo cp EFI-BOOT/* /mnt/EFI/BOOT/
    $ sudo cp EFI-VMWARE/* /mnt/EFI/VMware/
    

Make sure the files copied correctly:

    
    
    $ find . -type f -exec md5sum {} \;
    40e5ca413f3a9f9a0d70acc004d9c21b ./EFI-BOOT/BOOTx64.EFI
    c1c2a7593bf0a81210f04d0bba5b9678 ./EFI-BOOT/BOOTIA32.EFI
    e8ab21b08a119b14598e6ecd53698cf9 ./EFI-VMWARE/mboot64.efi
    e8d519aa27495ad8d483c25e23b878d3 ./EFI-VMWARE/mboot32.efi
    
    $ find /mnt/EFI/ -type f -exec md5sum {} \;
    c1c2a7593bf0a81210f04d0bba5b9678 /mnt/EFI/BOOT/BOOTIA32.EFI
    40e5ca413f3a9f9a0d70acc004d9c21b /mnt/EFI/BOOT/BOOTx64.EFI
    e8d519aa27495ad8d483c25e23b878d3 /mnt/EFI/VMware/mboot32.efi
    e8ab21b08a119b14598e6ecd53698cf9 /mnt/EFI/VMware/mboot64.efi
    
    $ sudo umount /mnt
    

### Boot Mac Pro from USB in ESXi

I’ve removed the MacOS hard drive from the tower, and replaced it with an old
500GB drive I have laying around. Plug in the USB drive, and boot. It’s pretty
slow to start up. But just let it go. Success means you’ve reached this page:
![esxi
running](https://0xdfimages.gitlab.io/img/img_20180115_132808-e1516041039882.jpg)

Now we can visit that ip given and log in to manage. But that’s a later post.

## Notes

  * “24GB? I thought you said 32?”. When you go to power on a MacPro and it doesn’t boot but instead the light above the power button blinks, it means bad ram. One of my 4GB DIMMs went bad, and they need to be installed in pairs. 
    * In troubleshooting this, I had some very strange results. Turns out the MacPro is picked about how you seat the ram. Use this guide: https://manuals.info.apple.com/MANUALS/0/MA430/en_US/MacPro_Early2008_MemoryDIMM_DIY.pdf
  * ESXi 6.5 shouldn’t work on this machine. According to the ESXi 6.5 release notes, vSphere 6.5 no longer supports the Intel Xeon 53XX series processor. This may cause me problems down the road. I could always roll back to 6.0.
  * Now is a good time to configure the ESXi server. I like to use DHCP, but with a static mapping at my EdgeRouterX gateway/DHCP server. The server is also VLAN aware, so I’ll have to figure that out at a later date.

[« Home Lab: The Hardware](/2018/01/15/home-lab-on-the-super-cheap-the-
hardware.html)

[](/2018/01/15/home-lab-on-the-super-cheap-esxi.html)

