# Flare-On 2019: Memecat Battlestation [Shareware Demo Edition]

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-memecat-
battlestation](/tags#flare-on-memecat-battlestation ) [dnspy](/tags#dnspy )
[dotnet](/tags#dotnet ) [reverse-engineering](/tags#reverse-engineering )  
  
Sep 28, 2019

  * [1] Memecat Battlestation
  * [[2] Overlong](/flare-on-2019/overlong.html)
  * [[3] Flarebear](/flare-on-2019/flarebear.html)
  * [[4] DNS Chess](/flare-on-2019/dnschess.html)
  * [[5] demo](/flare-on-2019/demo.html)
  * [[6] bmphide](/flare-on-2019/bmphide.html)
  * [[7] wopr](/flare-on-2019/wopr.html)

![](https://0xdfimages.gitlab.io/img/flare2019-1-cover.png)

Memecat Battlestation [Shareware Demo Edition] was a really simple challenge
that really involved opening a .NET executable in a debugger and reading the
correct phrases from the code. It was a good beginner challenge.

## Challenge

> Welcome to the Sixth Flare-On Challenge!
>
> This is a simple game. Reverse engineer it to figure out what “weapon codes”
> you need to enter to defeat each of the two enemies and the victory screen
> will reveal the flag. Enter the flag here on this site to score and move on
> to the next level.
>
>   * This challenge is written in .NET. If you don’t already have a favorite
> .NET reverse engineering tool I recommend dnSpy
>

>
> ** If you already solved the full version of this game at our booth at
> BlackHat or the subsequent release on twitter, congratulations, enter the
> flag from the victory screen now to bypass this level.

The file is an x86 .NET binary, as the note mentioned:

    
    
    $ file MemeCatBattlestation.exe 
    MemeCatBattlestation.exe: PE32 executable (GUI) Intel 80386 Mono/.Net assembly, for MS Windows
    

## Running It

Because this is a CTF, it’s worth giving this a run (in a VM still). There’s a
splash screen:

![1566311448291](https://0xdfimages.gitlab.io/img/1566311448291.png)

And then the first challenge comes out:

![1566311466522](https://0xdfimages.gitlab.io/img/1566311466522.png)

I’ll need to figure out the correct “Weapon Arming Code”.

## RE

### Round 1

Give this is a .Net executable, I’ll open in `dnspy`. I see the following:

![1566311593007](https://0xdfimages.gitlab.io/img/1566311593007.png)

I’ll open up `MemCatBattlestation`, and see the various forms:

![1566311621853](https://0xdfimages.gitlab.io/img/1566311621853.png)

Since it’s nicely labeled, I’ll open `Stage1Form`:

![1566311666282](https://0xdfimages.gitlab.io/img/1566311666282.png)

I’ll check out `FireButton_Click`:

    
    
    // MemeCatBattlestation.Stage1Form
    // Token: 0x0600000D RID: 13 RVA: 0x000024E8 File Offset: 0x000006E8
    private void FireButton_Click(object sender, EventArgs e)
    {
    	if (this.codeTextBox.Text == "RAINBOW")
    	{
    		this.fireButton.Visible = false;
    		this.codeTextBox.Visible = false;
    		this.armingCodeLabel.Visible = false;
    		this.invalidWeaponLabel.Visible = false;
    		this.WeaponCode = this.codeTextBox.Text;
    		this.victoryAnimationTimer.Start();
    		return;
    	}
    	this.invalidWeaponLabel.Visible = true;
    	this.codeTextBox.Text = "";
    }
    

If I enter “RAINBOW” into the box and hit “Fire!”, there’s an animation of my
cat shooting a rainbow, and then the other one explodes in flames:

![1566311811670](https://0xdfimages.gitlab.io/img/1566311811670.png)

### Round 2

Next I’m presented with another challenge:

![1566311845178](https://0xdfimages.gitlab.io/img/1566311845178.png)

Now in `Stage2Form`, I see this stage has similar code for `FireButton_Click`:

    
    
    // MemeCatBattlestation.Stage2Form
    // Token: 0x06000017 RID: 23 RVA: 0x00003114 File Offset: 0x00001314
    private void FireButton_Click(object sender, EventArgs e)
    {
    	if (this.isValidWeaponCode(this.codeTextBox.Text))
    	{
    		this.fireButton.Visible = false;
    		this.codeTextBox.Visible = false;
    		this.armingCodeLabel.Visible = false;
    		this.invalidWeaponLabel.Visible = false;
    		this.WeaponCode = this.codeTextBox.Text;
    		this.victoryAnimationTimer.Start();
    		return;
    	}
    	this.invalidWeaponLabel.Visible = true;
    	this.codeTextBox.Text = "";
    }
    

Instead of a direct comparison, there’s a function, `isValidWeaponCode` that
checks if I win. I’ll check out the source:

    
    
    // Token: 0x06000016 RID: 22 RVA: 0x000030C4 File Offset: 0x000012C4
    private bool isValidWeaponCode(string s)
    {
    	char[] array = s.ToCharArray();
    	int length = s.Length;
    	for (int i = 0; i < length; i++)
    	{
    		char[] array2 = array;
    		int num = i;
    		array2[num] ^= 'A';
    	}
    	return array.SequenceEqual(new char[]
    	{
    		'\u0003',
    		' ',
    		'&',
    		'$',
    		'-',
    		'\u001e',
    		'\u0002',
    		' ',
    		'/',
    		'/',
    		'.',
    		'/'
    	});
    }
    

This function simply reads my input, xors it with ‘A’, and then compares it
against an array of bytes. So to find out the right string, I just need to xor
those bytes by ‘A’. I’ll do that in `python`:

    
    
    $ python3
    Python 3.6.8 (default, Jan 14 2019, 11:02:34) 
    [GCC 8.0.1 20180414 (experimental) [trunk revision 259383]] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> result = '\x03 &$-\x1e\x02 //./'
    >>> ''.join([chr(ord(x)^ord('A')) for x in result])
    'Bagel_Cannon'
    
    

Entering “Bagel_Cannon” shoots bagels at the opponent, and then it also bursts
into flames.

![1566312382752](https://0xdfimages.gitlab.io/img/1566312382752.png)

Then I’m given the victory screen:

![1566312230500](https://0xdfimages.gitlab.io/img/1566312230500.png)

**Flag: Kitteh_save_galixy@flare-on.com**

[](/flare-on-2019/memecat-battlestation.html)

