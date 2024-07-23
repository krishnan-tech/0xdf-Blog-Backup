# Flare-On 2021: known

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-known](/tags#flare-on-
known ) [reverse-engineering](/tags#reverse-engineering )
[youtube](/tags#youtube ) [crypto](/tags#crypto ) [ghidra](/tags#ghidra )
[python](/tags#python )  
  
Nov 1, 2021

  * [[1] credchecker](/flare-on-2021/credchecker)
  * [2] known
  * [[3] antioch](/flare-on-2021/antioch)
  * [[4] myaquaticlife](/flare-on-2021/myaquaticlife)
  * [[5] FLARE Linux VM](/flare-on-2021/flarelinuxvm)
  * [[6] PetTheKitty](/flare-on-2021/petthekitty)
  * [[7] spel](/flare-on-2021/spel)
  * [[8] beelogin](/flare-on-2021/beelogin)
  * [9] evil - no writeup :(
  * [[10] wizardcult](/flare-on-2021/wizardcult)

![known](https://0xdfimages.gitlab.io/img/flare2021-known-cover.png)

known presented a ransomware file decrypter, as well as a handful of encrypted
files. If I can figure out the key to give the decrypter, it will decrypt the
files, one of which contains the flag. I’ll use Ghidra to determine the
algorithm, then recreate it in Python, and brute force all possible keys to
find the right one.

## Challenge

> We need your help with a ransomware infection that tied up some of our
> critical files. Good luck.

The [archive](/files/flare2021-02_known.7z) contains a Windows executable:

    
    
    $ file UnlockYourFiles.exe 
    02-known/UnlockYourFiles.exe: PE32 executable (console) Intel 80386, for MS Windows
    

It also contains a `Files` directory with six files each with a second
extension of `.encrypted`:

    
    
    $ ls Files/
    capa.png.encrypted  cicero.txt.encrypted  commandovm.gif.encrypted  critical_data.txt.encrypted  flarevm.jpg.encrypted  latin_alphabet.txt.encrypted
    

## Video Solve

A couple people reached out and asked for a video walkthrough of this
challenge, so I’ve done that here as well:

It’ll show a bit more of the how on getting the functions cleaned up to where
they make sense.

## Running It

In a Windows VM, running the binary pops a `cmd` instance with a message and a
prompt:

![image-20210911101050618](https://0xdfimages.gitlab.io/img/image-20210911101050618.png)

The message has some base64 just before the last line. It decodes to a hint:

    
    
    $ echo "KD4wXzApPiBJdCdzIGRhbmdlcm91cyB0byBhZGQrcm9yIGFsb25lISBUYWtlIHRoaXMgPCgwXzA8KQo=" | base64 -d
    (>0_0)> It's dangerous to add+ror alone! Take this <(0_0<)
    

A nice [Zelda
meme](https://en.wikipedia.org/wiki/It%27s_dangerous_to_go_alone!).

If I enter a key, it prints the names of the files in the folder and claims to
be decrypting them:

![image-20210911101148044](https://0xdfimages.gitlab.io/img/image-20210911101148044.png)

The files without the `.encrypted` extension exist, but they don’t open
(probably because they were decrypted with the wrong key).

## RE

### Entry

Opening this in Ghidra, there’s a handful of functions. I’ll start at the
`entry` and start trying to rename as many variables / functions / constants
as I can, as doing so will make clear what the function is doing.

[GetStdHandle](https://docs.microsoft.com/en-us/windows/console/getstdhandle)
is used to open both the `STD_INPUT_HANDLE` and `STD_OUTPUT_HANDLE` for the
console. Ghidra doesn’t like showing negative ints in the Decompile window,
but they show up nicely in the Listing matching what’s in the MS docs:

![image-20210911105028629](https://0xdfimages.gitlab.io/img/image-20210911105028629.png)

It calls `SetConsoleTestAttribute` to change the color, and then prints the
message, and reads the key. It passes that key to a function I’ll name
`decrypt`, and then exits.

    
    
    void entry(void)
    
    {
      bool res;
      undefined3 extraout_var;
      undefined4 user_key;
      undefined4 null;
      DWORD bytes_read;
      HANDLE console_stdin_h;
      
      user_key = 0;
      null = 0;
      console_stdin_h = GetStdHandle(4294967286);
      console_stdout_h = GetStdHandle(4294967285);
      SetConsoleTextAttribute(console_stdout_h,0xce);
      WriteConsoleA(console_stdout_h,s_**********_Attention!_**********_00403000,0x70a,(LPDWORD)0x0,
                    (LPVOID)0x0);
      ReadConsoleA(console_stdin_h,&user_key,8,&bytes_read,(PCONSOLE_READCONSOLE_CONTROL)0x0);
      res = decrypt((int)&user_key);
                        /* WARNING: Subroutine does not return */
      ExitProcess(CONCAT31(extraout_var,res));
    }
    

### decrypt

I’ll spend a few minutes looking at the MS docs and the `decrypt` function,
and pretty quickly it becomes clear what’s going on here:

    
    
    bool __cdecl decrypt(int key)
    
    {
      BOOL res;
      DWORD lasterr;
      _WIN32_FIND_DATAA file_info;
      CHAR out_filename [64];
      int in_filename_len;
      HANDLE enc_handle;
      uint num_files_decrypted;
      
      num_files_decrypted = 0;
      res = SetCurrentDirectoryA(s_Files_00403758);
      if (res == 0) {
        print_error(s_SetCurrentDirectory("Files")_00403738);
      }
      enc_handle = FindFirstFileA(s_*.encrypted_0040372c,(LPWIN32_FIND_DATAA)&file_info);
      if (enc_handle == (HANDLE)0xffffffff) {
        print_error(s_FindFirstFile_0040371c);
      }
      while( true ) {
        do {
          in_filename_len = gen_out_filename((int)out_filename,(int)file_info.cFileName);
          file_info.cAlternateFileName[in_filename_len + 6] = '\0';
          decrypt_file(file_info.cFileName,out_filename,key);
          num_files_decrypted = num_files_decrypted + 1;
          res = FindNextFileA(enc_handle,(LPWIN32_FIND_DATAA)&file_info);
        } while (res != 0);
        lasterr = GetLastError();
        if (lasterr == 0x12) break;
        print_error(s_FindNextFile_0040370c);
      }
      print_num_files_decrypted(num_files_decrypted);
      return num_files_decrypted != 0;
    }
    

It goes into a `Files` directory, and finds the first file that matches
`*.encrypted`. Then it loops, creating a new file name (without `.encrypted`),
and passing both filenames and the key into another function I call
`decrypt_file`. Then it gets the next file, and loops. It keeps a count of the
number of files decrypted, and prints that at the end.

### decrypt_file

The next function can be figured out roughly the same way:

    
    
    void __cdecl decrypt_file(LPCSTR in_file_name,LPCSTR out_file_name,int key)
    
    {
      BOOL res;
      undefined contents [8];
      DWORD local_14;
      HANDLE f_in_handle;
      HANDLE f_out_handle;
      DWORD num_bytes;
      
      f_in_handle = CreateFileA(in_file_name,GENERIC_READ,FILE_SHARE_READ,(LPSECURITY_ATTRIBUTES)0x0,
                                OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,(HANDLE)0x0);
      if (f_in_handle == (HANDLE)0xffffffff) {
        print_error(in_file_name);
      }
      f_out_handle = CreateFileA(out_file_name,GENERIC_WRITE,0,(LPSECURITY_ATTRIBUTES)0x0,CREATE_ALWAYS,
                                 FILE_ATTRIBUTE_NORMAL,(HANDLE)0x0);
      if (f_out_handle == (HANDLE)0xffffffff) {
        print_error(out_file_name);
      }
      while( true ) {
        res = ReadFile(f_in_handle,contents,8,&num_bytes,(LPOVERLAPPED)0x0);
        if (res == 0) {
          print_error(in_file_name);
        }
        if (num_bytes == 0) break;
        decrypt_buffer((int)contents,key);
        res = WriteFile(f_out_handle,contents,num_bytes,&local_14,(LPOVERLAPPED)0x0);
        if (res == 0) {
          print_error(out_file_name);
        }
      }
      CloseHandle(f_out_handle);
      CloseHandle(f_in_handle);
      num_bytes = strlen((int)in_file_name);
      out_file_name[num_bytes - 10] = '\n';
      WriteConsoleA(console_stdout_h,in_file_name,num_bytes,(LPDWORD)0x0,(LPVOID)0x0);
      WriteConsoleA(console_stdout_h,&arrow_str,4,(LPDWORD)0x0,(LPVOID)0x0);
      WriteConsoleA(console_stdout_h,out_file_name,num_bytes - 9,(LPDWORD)0x0,(LPVOID)0x0);
      return;
    }
    

It opens both the input and output files, and then reads the contents of the
input file eight bytes at a time. It passes those eight bytes and the key to
another function I’ll call `decrypt_buffer`, and then writes the results to
the output file, looping until the file is done. At the end, it prints a line
to the console `[in] -> [out]` like was observed above.

### decrypt_buffer

Finally the math comes out. This function takes an eight byte block and
scrambles (or unscrambles it) in a loop:

    
    
    void __cdecl decrypt_buffer(int buffer,int key)
    
    {
      byte val;
      byte j;
      uint i;
      
      i = 0;
      while (j = (byte)i, (char)j < 8) {
        val = *(byte *)(i + buffer) ^ *(byte *)(i + key);
        *(byte *)(i + buffer) = (val << (j & 7) | val >> 8 - (j & 7)) - j;
        i = (uint)(byte)(j + 1);
      }
      return;
    }
    

It will xor the byte with the corresponding byte in the key. Then it will
rotate right by `j` bytes, where `j` is the byte number, zero through seven.
Then it will subtract `j`. I don’t see any place where `i` and `j` are
different, so they really could be handled by one variable.

## Crack Key

### Recreate Algorithm

I’ll recreate this algorithm in Python, using the `<<` and `>>` operators to
do bit shifts:

    
    
    #!/usr/bin/env python3    
        
    import sys    
        
        
    def decrypt(key, buf):    
        res = b""    
        for i in range(8):    
            x = ord(key[i]) ^ ord(buf[i])    
            if i > 0:    
                x = ((x << i) + (x >> (8-i)) - i) % 256    
            res += x.to_bytes(1, 'big')    
        return res    
        
        
    key = sys.argv[1]    
    buf = sys.argv[2]    
        
    print(decrypt(key, buf)) 
    

I can check this by creating a file called `test.txt.encrypted` in the file
folder and putting a bunch of capital A in it. Then I’ll run the decrypter,
give it a password of “0xdf0xdf”, and look at the resulting file, `test.txt`:

    
    
    $ xxd test.txt.encrypted 
    00000000: 4141 4141 4141 4141 4141 4141 4141 4141  AAAAAAAAAAAAAAAA
    00000010: 4141 4141 4141 4141 4141 4141 4141 4141  AAAAAAAAAAAAAAAA
    00000020: 4141 4141 4141 4141 4141 4141 4141 4141  AAAAAAAAAAAAAAAA
    00000030: 4141 41                                  AAA
    $ xxd test.txt
    00000000: 7171 9236 1322 438c 7171 9236 1322 438c  qq.6."C.qq.6."C.
    00000010: 7171 9236 1322 438c 7171 9236 1322 438c  qq.6."C.qq.6."C.
    00000020: 7171 9236 1322 438c 7171 9236 1322 438c  qq.6."C.qq.6."C.
    00000030: 7171 92                                  qq.
    

I’ll try my decrypter with the same buffer:

    
    
    $ python3 decrypt.py AAAAAAAA 0xdf0xdf
    b'qq\x926\x13"C\x8c'
    

It makes the same output.

### Brute Force Key

#### Strategy

I’ve learned a few important points about this algorithm:

  1. It expects an eight byte key;
  2. It works in eight byte blocks;
  3. Changing one byte in the key changes only the corresponding byte in the output.

This means that if I know the expected plaintext, I can try all 256 possible
options for a key and see which one produces that.

I’m also in luck that one of the files is a PNG, as those files have [constant
eight-byte
headers](https://en.wikipedia.org/wiki/Portable_Network_Graphics#File_header).

The encrypted PNG has the following initial bytes:

    
    
    $ xxd capa.png.encrypted | head -1
    00000000: c7c7 251d 630d f356 4eef b156 a61f 5ac6  ..%.c..VN..V..Z.i
    

#### Script

I’ll update the script to brute the entire key:

    
    
    #!/usr/bin/env python3    
        
    import sys    
    
        
    def decrypt(key, buf):    
        res = b""    
        for i in range(8):    
            x = key[i] ^ buf[i]    
            if i > 0:
                x = ((x << i) + (x >> (8-i)) - i) % 256
            res += x.to_bytes(1, 'big')
        return res
    
    
    # $ xxd capa.png.encrypted | head -1
    # 00000000: c7c7 251d 630d f356 4eef b156 a61f 5ac6  ..%.c..VN..V..Z."
    enc_png = bytearray([0xc7,0xc7,0x25,0x1d,0x63,0x0d,0xf3,0x56])
    dec_png = bytearray([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a])
    key = bytearray(8)
    
    for i in range(8):
        for j in range(256):
            key[i] = j
            res = decrypt(key, enc_png)
            if res[i] == dec_png[i]:
                break
    
    print(key.decode())
    

I’ll work with `bytearray` objects (the only change to the `decrypt` function
is to remove the call to `ord` on each character). There are two loops. The
first will walk down each of the eight characters in the key. The inner loop
tries each value from 0-255 in that key position, and calls `decrypt`. If the
byte in the current position matches what I expect for a PNG, then that key
byte is correct, the inner loop breaks, and then it moves to the next byte in
the key. Once it’s done, it prints all eight bytes:

    
    
    $ python3 brute-decrypt.py
    No1Trust
    

### Decrypt Files

I’ll run the program again, and enter the correct key:

    
    
    Z:\flareon-2021\02-known>.\UnlockYourFiles.exe
    **********
    Attention!
    **********
    
    Your documents, photos, and other important files have been encrypted with a strong algorithm.
    
    Don't try and change file extensions! It can be dangerous for the encrypted information!
    
    The only way to recover (decrypt) your files is to run this decryptor with the unique private key.
    Attention! Only we can recover your files! If someone tell you that he can do this, kindly ask him to proof!
    
    Below you will see a big base64 blob, you will need to email us and copy this blob to us.
    You must pay all but 1 BTC to 48 hours for recover it. After 48 hours we will leaked all your data!
    
    KD4wXzApPiBJdCdzIGRhbmdlcm91cyB0byBhZGQrcm9yIGFsb25lISBUYWtlIHRoaXMgPCgwXzA8KQo=
    
    Enter the decryption key and press Enter: No1Trust
    capa.png.encrypted -> capa.png
    commandovm.gif.encrypted -> commandovm.gif
    cicero.txt.encrypted -> cicero.txt
    flarevm.jpg.encrypted -> flarevm.jpg
    latin_alphabet.txt.encrypted -> latin_alphabet.txt
    critical_data.txt.encrypted -> critical_data.txt
    Number of files decoded: 6
    

The flag is in `critical_data.txt`:

    
    
    Z:\flareon-2021\02-known>type files\critical_data.txt
    (>0_0)> You_Have_Awakened_Me_Too_Soon_EXE@flare-on.com <(0_0<)
    

**Flag: You_Have_Awakened_Me_Too_Soon_EXE@flare-on.com**

[](/flare-on-2021/known)

