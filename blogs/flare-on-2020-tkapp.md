# Flare-On 2020: TKApp

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-tkapp](/tags#flare-on-
tkapp ) [reverse-engineering](/tags#reverse-engineering ) [tizen](/tags#tizen
) [tpk](/tags#tpk ) [dnspy](/tags#dnspy ) [dotnet](/tags#dotnet )
[emulation](/tags#emulation ) [python](/tags#python )  
  
Oct 28, 2020

  * [[1] Fidler](/flare-on-2020/fidler)
  * [[2] garbage](/flare-on-2020/garbage)
  * [[3] wednesday](/flare-on-2020/wednesday)
  * [[4] report.xls](/flare-on-2020/report)
  * [5] TKApp
  * [[6] CodeIt](/flare-on-2020/codeit)
  * [[7] RE Crowd](/flare-on-2020/recrowd)
  * [[8] Aardvark](/flare-on-2020/aardvark)
  * [[9] crackinstaller](/flare-on-2020/crackinstaller)
  * [[10] break](/flare-on-2020/break)

![tkapp](https://0xdfimages.gitlab.io/img/flare2020-tkapp-cover.png)

TKApp was a Tizen mobile application that was made to run on a smart watch.
Inside the archive, there’s a .NET dll that drives the application, so I can
break it open with dnSpy. Four variables are initialized through different
user actions or different aspects of the files on the watch, and then used to
generate a key to decrypt a buffer. I’ll show both static analysis to pull the
keys and then decrypt in Python, as well as how to emulate a watch and then go
through the steps to get it to display the flag in the gallery.

## Challenge

> Now you can play Flare-On on your watch! As long as you still have an arm
> left to put a watch on, or emulate the watch’s operating system with
> sophisticated developer tools.

The file contains `.tpk` file, which identifies as a zip archive:

    
    
    root@kali# file TKApp.tpk 
    TKApp.tpk: Zip archive data, at least v2.0 to extract
    

This is a Tizen application. [Tizen](https://en.wikipedia.org/wiki/Tizen) is
Samsung’s which has been used as a competitor to Android on phones and smart
watches.

## RE

### General Structure

Given that it’s a zip archive, I’ll unzip it and look at what’s inside:

    
    
    root@kali# find . -type f
    ./TKApp.deps.json
    ./tizen-manifest.xml
    ./res../img/tiger2.png
    ./res../img/tiger1.png
    ./res../img/img.png
    ./res../img/todo.png
    ./res/gallery/01.jpg
    ./res/gallery/02.jpg
    ./res/gallery/03.jpg
    ./res/gallery/04.jpg
    ./res/gallery/05.jpg
    ./bin/Xamarin.Forms.Core.dll
    ./bin/Xamarin.Forms.Platform.Tizen.dll
    ./bin/Tizen.Wearable.CircularUI.Forms.Renderer.dll
    ./bin/Xamarin.Forms.Platform.dll
    ./bin/TKApp.dll
    ./bin/Tizen.Wearable.CircularUI.Forms.dll
    ./bin/Xamarin.Forms.Xaml.dll
    ./bin/ExifLib.Standard.dll
    ./shared/res/TKApp.png
    ./author-signature.xml
    ./signature1.xml
    

`tizen-manifest` is interesting for a few reasons:

    
    
    <?xml version="1.0" encoding="utf-8"?>
    <manifest package="com.flare-on.TKApp" version="1.0.0" api-version="5.5" xmlns="http://tizen.org/ns/packages">
        <author href="http://www.flare-on.com" />
        <profile name="wearable" />
        <ui-application appid="com.flare-on.TKApp" exec="TKApp.dll" multiple="false" nodisplay="false" taskmanage="true" api-version="6" type="dotnet" launch_mode="single">
            <label>TKApp</label>
            <icon>TKApp.png</icon>
            <metadata key="http://tizen.org/metadata/prefer_dotnet_aot" value="true" />
            <metadata key="its" value="magic" />
            <splash-screens />
        </ui-application>
        <shortcut-list />
        <privileges>
            <privilege>http://tizen.org/privilege/location</privilege>
            <privilege>http://tizen.org/privilege/healthinfo</privilege>
        </privileges>
        <dependencies />
        <provides-appdefined-privileges />
    </manifest>
    

  * The UI for the application is `TKApp.dll`. It is marked as a type “dotnet”.
  * There’s a metadata value with `key` “its” and `value` “magic”. I’ll need that later.

### Identify Buffer Decryption

Given that it’s a .NET application, I opened the `.tpk` file in dnSpy. There’s
a bunch of classes in the `TKApp` namespace, as well as some resources:

![image-20200918222405350](https://0xdfimages.gitlab.io/img/image-20200918222405350.png)

I spent some time clicking through the various classes, and the `GetString`
function in `TKApp.Util` caught my eye:

    
    
    // TKApp.Util
    // Token: 0x06000052 RID: 82 RVA: 0x00003694 File Offset: 0x00001894
    public static string GetString(byte[] cipherText, byte[] Key, byte[] IV)
    {
      string result = null;
      using (RijndaelManaged rijndaelManaged = new RijndaelManaged())
      { 
        rijndaelManaged.Key = Key;
        rijndaelManaged.IV = IV; 
        ICryptoTransform cryptoTransform = rijndaelManaged.CreateDecryptor(rijndaelManaged.Key, rijndaelManaged.IV);
        using (MemoryStream memoryStream = new MemoryStream(cipherText))
        {   
          using (CryptoStream cryptoStream = new CryptoStream(memoryStream, cryptoTransform, 0))
          {     
            using (StreamReader streamReader = new StreamReader(cryptoStream))
            {       
              result = streamReader.ReadToEnd();
            }       
          }     
        }   
      } 
      return result;
    }
    

This function is a basic decryption function. I’ll right click on `GetString`
and select “Analyze”, and it shows up in the Analyzer window:

![image-20200918222626826](https://0xdfimages.gitlab.io/img/image-20200918222626826.png)

As it is used by `TKApp.MainPage.GetImage()`, I’ll check out that function:

    
    
    private bool GetImage(object sender, EventArgs e)
    {
        if (string.IsNullOrEmpty(App.Password) || string.IsNullOrEmpty(App.Note) || string.IsNullOrEmpty(App.Step) || string.IsNullOrEmpty(App.Desc))
        {
            this.btn.Source = "img/tiger1.png";
            this.btn.Clicked -= this.Clicked;
            return false;
        }
        string text = new string(new char[]
                                 {
                                     App.Desc[2],
                                     App.Password[6],
                                     App.Password[4],
                                     App.Note[4],
                                     ...[snip]...
                                     App.Step[4],
                                     ...[snip]....
                                     App.Desc[3]
                                 });
        byte[] key = SHA256.Create().ComputeHash(Encoding.ASCII.GetBytes(text));
        byte[] bytes = Encoding.ASCII.GetBytes("NoSaltOfTheEarth");
        try
        {
            App.ImgData = Convert.FromBase64String(Util.GetString(Runtime.Runtime_dll, key, bytes));
            return true;
        }
        catch (Exception ex)
        {
            Toast.DisplayText("Failed: " + ex.Message, 1000);
        }
        return false;
    }
    
    

This function checks that four variables are not null or empty:
`App.Password`, `App.Note`, `App.Step`, and `App.Desc`. When they all have
values, it creates a string `text` using characters out of these four
variables. It takes a SHA256 hash of the resulting string, which is the
32-byte key. It has a static IV, “NoSaltOfTheEarth”, which is 16 bytes. AES
CBC 128 will take a 32-byte key and a 16 byte block-size including the IV. The
ciphertext is retrieved from `Runtime.Runtime_dll`.

If I can find the values for the four variables and the ciphertext, I should
be able to decrpyt it using Python easily.

### Find Four Keys

#### Password

Inside the `App` class, each of the variables I care about have a `get` and a
`set` method:

![image-20200918223316469](https://0xdfimages.gitlab.io/img/image-20200918223316469.png)

I’ll use Analyze on `set_Password` to find the it us used in
`TKApp.UnlockPage.OnLoginButtonClicked`:

    
    
    private async void OnLoginButtonClicked(object sender, EventArgs e)
    {
        if (this.IsPasswordCorrect(this.passwordEntry.Text))
        {
            App.IsLoggedIn = true;
            App.Password = this.passwordEntry.Text;
            base.Navigation.InsertPageBefore(new MainPage(), this);
            await base.Navigation.PopAsync();
        }
        else
        {
            Toast.DisplayText("Unlock failed!", 2000);
            this.passwordEntry.Text = string.Empty;
        }
    }
    

`App.Password` is set to the entered text if `IsPasswordCorrect` returns true.
`IsPasswordCorrect` is a simple wrapper checking that the text matches a
stored decoded password:

    
    
    private bool IsPasswordCorrect(string password)
    {
        return password == Util.Decode(TKData.Password);
    }
    

`Util.Decode` is a simple one byte XOR:

    
    
    public static string Decode(byte[] e)
    {
        string text = "";
        foreach (byte b in e)
        {
            text += Convert.ToChar((int)(b ^ 83)).ToString();
        }
        return text;
    }
    

`TKData.Password` is a static byte array:

    
    
    public static byte[] Password = new byte[]
    {
        62,
        38,
        63,
        63,
        54,
        39,
        59,
        50,
        39
    };
    

I can decode that easily:

    
    
    >>> x = [62, 38, 63, 63, 54, 39, 59, 50, 39]
    >>> ''.join([chr(c^83) for c in x])
    'mullethat'
    

#### Note

Analyze shows that `set_Note` is called by `TKApp.TodoPage.SetupList()`:

    
    
    private void SetupList()
    {
        List<TodoPage.Todo> list = new List<TodoPage.Todo>();
        if (!this.isHome)
        {
            list.Add(new TodoPage.Todo("go home", "and enable GPS", false));
        }
        else
        {
            TodoPage.Todo[] collection = new TodoPage.Todo[]
            {
                new TodoPage.Todo("hang out in tiger cage", "and survive", true),
                new TodoPage.Todo("unload Walmart truck", "keep steaks for dinner", false),
                new TodoPage.Todo("yell at staff", "maybe fire someone", false),
                new TodoPage.Todo("say no to drugs", "unless it's a drinking day", false),
                new TodoPage.Todo("listen to some tunes", "https://youtu.be/kTmZnQOfAF8", true)
            };
            list.AddRange(collection);
        }
        List<TodoPage.Todo> list2 = new List<TodoPage.Todo>();
        foreach (TodoPage.Todo todo in list)
        {
            if (!todo.Done)
            {
                list2.Add(todo);
            }
        }
        this.mylist.ItemsSource = list2;
        App.Note = list2[0].Note;
    }
    

This functions sets some todos in `list`, and then loops over them, adding the
ones that aren’t done to `list2`. `list2[0].Note` is saved as `App.Note`. The
constructor for `Todo` showed me that the three inputs were `Name`, `Note`,
and `Done`.

I wasn’t totally confident about the `if` at the top, and if the true or the
false would be called, or both and in what order. Because only todos with
`Done` false could be saved in `list2`, the first item’s `Note` had to be
either “and enable GPS” or “keep steaks for dinner”. I cheated a bit and
looked back at `GetImage` to see a reference to `App.Note[18]`, which wouldn’t
exist in the former option. So I went with “keep steaks for dinner”.

#### Desc

`set_Desc` is called by `TKApp.GalleryPage.IndexPage_CurrentPageChanged`:

    
    
    private void IndexPage_CurrentPageChanged(object sender, EventArgs e)
    {
        if (base.Children.IndexOf(base.CurrentPage) == 4)
        {
            using (ExifReader exifReader = new ExifReader(Path.Combine(Application.Current.DirectoryInfo.Resource, "gallery", "05.jpg")))
            {
                string desc;
                if (exifReader.GetTagValue<string>(ExifTags.ImageDescription, out desc))
                {
                    App.Desc = desc;
                }
                return;
            }
        }
        App.Desc = "";
    }
    

It is reading the EXIF “Image Description” from `gallery/05.jpg`, which I can
also do:

    
    
    root@kali# exiftool extracted/res/gallery/05.jpg | grep Description
    Image Description               : water
    

#### Step

`set_Step` is called from `TKApp.MainPage.PedDataUpdate`:

    
    
    private void PedDataUpdate(object sender, PedometerDataUpdatedEventArgs e)
    {
        if (e.StepCount > 50U && string.IsNullOrEmpty(App.Step))
        {
            App.Step = Application.Current.ApplicationInfo.Metadata["its"];
        }
        if (!string.IsNullOrEmpty(App.Password) && !string.IsNullOrEmpty(App.Note) && !string.IsNullOrEmpty(App.Step) && !string.IsNullOrEmpty(App.Desc))
        {
            HashAlgorithm hashAlgorithm = SHA256.Create();
            byte[] bytes = Encoding.ASCII.GetBytes(App.Password + App.Note + App.Step + App.Desc);
            byte[] first = hashAlgorithm.ComputeHash(bytes);
            byte[] second = new byte[]
            {
                50,
                148,
                76,
                ...[snip]...
                181,
                139,
                104,
                56
            };
            if (first.SequenceEqual(second))
            {
                this.btn.Source = "img/tiger2.png";
                this.btn.Clicked += this.Clicked;
                return;
            }
            this.btn.Source = "img/tiger1.png";
            this.btn.Clicked -= this.Clicked;
        }
    }
    

At the start of the function, assuming the step count is greater than 50, it
will set `App.Step` to `Application.Current.ApplicationInfo.Metadata["its"]`.
I noted above that this is “magic”.

There’s also this other interesting check where it takes a SHA256 of
`App.Password + App.Note + App.Step + App.Desc`, and compares it against a
static value, loading an image based on if it matches. II have all four now:

Var | Value  
---|---  
App.Desc | water  
App.Password | mullethat  
App.Note | keep steaks for dinner  
App.Step | magic  
  
So I can try the hash:

    
    
    root@kali# echo -n "mullethatkeep steaks for dinnermagicwater" | sha256sum 
    32944ce96ec7e44872e34e8a5dbdbd939f4642df7b892c4965eb8110b58b6838  -
    

It matches! 0x32 == 50, 0x94 == 148, 0x4c == 76, etc. That’s a good sign that
I have the right password.

## Solutions

There are two ways to dump out the flag. When I solved during the competition,
I used the first method below to dump and decrypt the buffer in `Runtime.dll`.
But I can also emulate the software and go through the steps, which I’ll show
at the end.

### Decryption

The last thing I need is a copy of `Runtime.dll` from the resources. I’ll
right click on it and select “Save Runtime.dll”:

![image-20200918225425983](https://0xdfimages.gitlab.io/img/image-20200918225425983.png)

Just taking a quick look, it’s not a Windows exe format (would start with MZ):

    
    
    root@kali# file Runtime.dll 
    Runtime.dll: data
    
    root@kali# xxd Runtime.dll | head
    00000000: 369b 5194 aa87 457e 6e0d 4648 1384 83e5  6.Q...E~n.FH....
    00000010: d2e4 18ac 94e1 0aea 553a 5b22 66c8 3ae1  ........U:["f.:.
    00000020: 83b6 e4a0 b9bc 3d7e 76a1 cdac de93 71d9  ......=~v.....q.
    00000030: 96b9 836f bbd6 351b 295e c044 3630 6489  ...o..5.)^.D60d.
    00000040: a96a 7f97 be0c fcea 642b 0104 f4f1 4943  .j......d+....IC
    00000050: 28ca 6f02 fe3f a01a 2f45 1de9 a0e7 21bb  (.o..?../E....!.
    00000060: cee1 6333 f237 cd88 82d9 c2dd 46f1 73c8  ..c3.7......F.s.
    00000070: 4126 c3b9 2592 7529 827c 2e07 bd0b 0633  A&..%.u).|.....3
    00000080: d5af efe1 7890 93c5 bb36 861f aad7 3efb  ....x....6....>.
    00000090: 10cb 2267 95af f6a3 5582 8d65 ecd9 639b  .."g....U..e..c.
    

I started a Python script to do the decrpytion. First, I needed to build the
key from the four strings:

    
    
    #!/usr/bin/env python3
    
    import hashlib
    from Crypto.Cipher import AES
    from py3rijndael import RijndaelCbc, ZeroPadding
    
    
    Desc = "water"
    Password = "mullethat"
    Note = "keep steaks for dinner"
    Step = "magic"
    
    text = ''.join([Desc[2], Password[6], Password[4], Note[4], Note[0], Note[17], Note[18], Note[16], Note[11], Note[13], Note[12], Note[15], Step[4], Password[6], Desc[1], Password[2], Password[2], Password[4], Note[18], Step[2], Password[4], Note[5], Note[4], Desc[0], Desc[3], Note[15], Note[8], Desc[4], Desc[3], Note[4], Step[2], Note[13], Note[18], Note[18], Note[8], Note[4], Password[0], Password[7], Note[0], Password[4], Note[11], Password[6], Password[4], Desc[4], Desc[3]])
    
    print(text)
    

On running, it prints a message:

    
    
    root@kali# python3 ./getImage.py 
    the kind of challenges we are gonna make here
    

It makes sense, another good sign that I’m on the right track.

Now I’ll have it hash `text`, set the IV, read in the ciphertext, and decrypt:

    
    
    #!/usr/bin/env python3
    
    import hashlib
    from Crypto.Cipher import AES
    
    
    Desc = "water"
    Password = "mullethat"
    Note = "keep steaks for dinner"
    Step = "magic"
    
    text = ''.join([Desc[2], Password[6], Password[4], Note[4], Note[0], Note[17], Note[18], Note[16], Note[11], Note[13], Note[12], Note[15], Step[4], Password[6], Desc[1], Password[2], Password[2], Password[4], Note[18], Step[2], Password[4], Note[5], Note[4], Desc[0], Desc[3], Note[15], Note[8], Desc[4], Desc[3], Note[4], Step[2], Note[13], Note[18], Note[18], Note[8], Note[4], Password[0], Password[7], Note[0], Password[4], Note[11], Password[6], Password[4], Desc[4], Desc[3]])
    
    key = hashlib.sha256(text.encode()).digest()
    iv = b"NoSaltOfTheEarth"
    
    with open('Runtime.dll', 'rb') as f:
        ciphertext = f.read()
    
    aes = AES.new(key, AES.MODE_CBC, iv)
    plain = aes.decrypt(ciphertext)
    

As I don’t know what the plaintext will be, I’ll just stop here, and run with
`-i` to get an interactive shell at the end:

    
    
    root@kali# python3 -i ./getImage.py 
    >>> plain[:100]
    b'/9j/4AAQSkZJRgABAQEBLAEsAAD/4R2qRXhpZgAASUkqAAgAAAAFABoBBQABAAAASgAAABsBBQABAAAAUgAAACgBAwABAAAAAgAA'
    

The resulting plaintext looks to be base64-encoded. I’ll see if it decodes:

    
    
    >>> import base64
    >>> base64.b64decode(plain)[:100]
    b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x01,\x01,\x00\x00\xff\xe1\x1d\xaaExif\x00\x00II*\x00\x08\x00\x00\x00\x05\x00\x1a\x01\x05\x00\x01\x00\x00\x00J\x00\x00\x00\x1b\x01\x05\x00\x01\x00\x00\x00R\x00\x00\x00(\x01\x03\x00\x01\x00\x00\x00\x02\x00\x00\x001\x01\x02\x00\x0c\x00\x00\x00Z\x00\x00\x002\x01\x02\x00\x14\x00\x00\x00f\x00\x00\x00'
    

I’ll quickly recognize the `JFIF` as part of the jpg metadata. `FF D8 FF E0 00
10 4A 46 49 46 00 01` represents the [magic
bytes](https://en.wikipedia.org/wiki/List_of_file_signatures) for a jpg file.

I’ll add the decode to the script and then write the results to a file. The
complete script is:

    
    
    #!/usr/bin/env python3
    
    import base64
    import hashlib
    from Crypto.Cipher import AES
    
    
    Desc = "water"
    Password = "mullethat"
    Note = "keep steaks for dinner"
    Step = "magic"
    
    text = ''.join([Desc[2], Password[6], Password[4], Note[4], Note[0], Note[17], Note[18], Note[16], Note[11], Note[13], Note[12], Note[15], Step[4], Password[6], Desc[1], Password[2], Password[2], Password[4], Note[18], Step[2],        Password[4], Note[5], Note[4], Desc[0], Desc[3], Note[15], Note[8], Desc[4], Desc[3], Note[4], Step[2], Note[13], Note[18], Note[18], Note[8], Note[4], Password[0], Password[7], Note[0], Password[4], Note[11], Password[6],             Password[4], Desc[4], Desc[3]])
    
    key = hashlib.sha256(text.encode()).digest()
    iv = b"NoSaltOfTheEarth"
    
    with open('Runtime.dll', 'rb') as f:
        ciphertext = f.read()
    
    aes = AES.new(key, AES.MODE_CBC, iv)
    plain = aes.decrypt(ciphertext)
    
    with open('flag.jpg', 'wb') as f:
        f.write(base64.b64decode(plain))
    

After running, `flag.jpg` provides the flag:

![](https://0xdfimages.gitlab.io/img/flare7-tkapp-flag.jpg)

**Flag: n3ver_go1ng_to_recov3r@flare-on.com@flare-on.com**

### Emulation

I can also get the flag through emulation. I’ll install the Tizen Studio, and
go into the Emulator Manager. I created a device, a wearable circle using with
5.5 to match the api version from the config. On booting, i get a watchface:

![image-20201027133851299](https://0xdfimages.gitlab.io/img/image-20201027133851299.png)

I can hit the bottom button to get the apps list. Now i need to load the app,
which I’ll do with `sdb`:

    
    
    C:\tizen-studio\tools>sdb install c:\TKApp.tpk
    WARNING: Your data are to be sent over an unencrypted connection and could be read by others.
    pushed                      TKApp.tpk   100%       1709KB           0KB/s
    1 file(s) pushed. 0 file(s) skipped.
    c:\TKApp.tpk                     2935KB/s (1750641 bytes in 0.582s)
    path is /home/owner/share/tmp/sdk_tools/TKApp.tpk
    __return_cb req_id[1] pkg_type[tpk] pkgid[com.flare-on.TKApp] key[start] val[install]
    __return_cb req_id[1] pkg_type[tpk] pkgid[com.flare-on.TKApp] key[install_percent] val[12]
    __return_cb req_id[1] pkg_type[tpk] pkgid[com.flare-on.TKApp] key[install_percent] val[15]
    ...[snip]...
    __return_cb req_id[1] pkg_type[tpk] pkgid[com.flare-on.TKApp] key[install_percent] val[100]
    __return_cb req_id[1] pkg_type[tpk] pkgid[com.flare-on.TKApp] key[end] val[ok]
    spend time for pkgcmd is [847]ms
    

Now there’s a new app in the menu that wasn’t there previously on the second
page:

![image-20201027134200071](https://0xdfimages.gitlab.io/img/image-20201027134200071.png)

Opening it prompts for the password. I’ll enter “mullethat”, which both let’s
me in and sets the variable for the password. It then asks for permissions to
access sensors, which I’ll allow, knowing it needs that to get to the flag.
Now I’m at the home-screen for the app:

![image-20201027134310892](https://0xdfimages.gitlab.io/img/image-20201027134310892.png)

Clicking on the dots on the right, there’s a menu with ToDos and Gallery.
ToDos wants my location (which is strange, but makes sense given the RE done
above), and I’ll allow it. The only task at this point is to “go home”.

![image-20201027134808848](https://0xdfimages.gitlab.io/img/image-20201027134808848.png)

I know to get the flag, I need the ToDo list set to the second set of options.
Above I saw that relied `this.isHome` being true. That variable is set in
`ToDoPAge.CheckHome`:

    
    
    Location location = TodoPage._locator.GetLocation();
    if (this.GetHowFar(TKData.lat, TKData.lon, location.Latitude, location.Longitude) < num)
    {
        this.isHome = true;
    }
    else
    {
        this.isHome = false;
    }
    

`TKData.lat` and `TKData.long` are set by the app to the EXIF data from
`04.jpg`:

    
    
    double[] coordinates = TKData.GetCoordinates(Path.Combine(Application.Current.DirectoryInfo.Resource, "gallery", "04.jpg"));
    TKData.lat = coordinates[0];
    TKData.lon = coordinates[1];
    

I can get the EXIF data from that image to see that I need to set the location
to [34.625194,
-97.211694](https://www.google.com/maps/place/34%C2%B037'30.7%22N+97%C2%B012'42.1%22W/@34.6251061,-97.2125098,17z/data=!4m5!3m4!1s0x0:0x0!8m2!3d34.6252!4d-97.2117).
By right-clicking on the watch, I can access the Emulation Control Panel,
where I can set the location. When I inject the location, the ToDo page
immediately changes:

![image-20201027134906660](https://0xdfimages.gitlab.io/img/image-20201027134906660.png)

Now the note variable should be set as well. I’ll go back into the control
panel and find the Pedometer settings, and set it to Run, to start logging
some steps. This should eventually trigger the setting of the step variable.

Setting the `Desc` variable is done in the
`GalleryPage.IndexPage_CurrentPageChanged` function:

    
    
    private void IndexPage_CurrentPageChanged(object sender, EventArgs e)
    {
        if (base.Children.IndexOf(base.CurrentPage) == 4)
        {
            using (ExifReader exifReader = new ExifReader(Path.Combine(Application.Current.DirectoryInfo.Resource, "gallery", "05.jpg")))
            {
                string desc;
                if (exifReader.GetTagValue<string>(ExifTags.ImageDescription, out desc))
                {
                    App.Desc = desc;
                }
                return;
            }
        }
        App.Desc = "";
    }
    

I need to switch to the page with index 4. When I visit the Gallery and look
at the images, making sure to hit the ones at the end, and then come back to
the main page, assuming enough time has gone by for 50 steps, the image is
different:

![image-20201027141721372](https://0xdfimages.gitlab.io/img/image-20201027141721372.png)

This indicates that all four keys are in place, and the hash of their
combination matched the static hash identified above where the Step was set:

    
    
    if (first.SequenceEqual(second))
    {
        this.btn.Source = "img/tiger2.png";
        this.btn.Clicked += this.Clicked;
        return;
    }
    this.btn.Source = "img/tiger1.png";
    this.btn.Clicked -= this.Clicked;
    

The function I need to call to activate the decryption is `MainPage.Clicked`:

    
    
    private void Clicked(object sender, EventArgs e)
    {
        if (this.GetImage(null, null))
        {
            Toast.DisplayText("Roaaaarrrr", 3000);
        }
    }
    

It calls `MainPage.GetImage` where the decryption happens if the circumstances
are right and loads it into the gallery. Double-clicking the open mouthed
tiger pops a message “Roaaaarrrr”, and then returns to the home-screen. On
visiting the gallery, there’s a new picture:

![image-20201027152853387](https://0xdfimages.gitlab.io/img/image-20201027152853387.png)

[](/flare-on-2020/tkapp)

