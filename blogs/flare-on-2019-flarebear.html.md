# Flare-On 2019: Flarebear

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-
flarebear](/tags#flare-on-flarebear ) [apk](/tags#apk )
[genymotion](/tags#genymotion ) [android](/tags#android ) [jadx](/tags#jadx )
[algebra](/tags#algebra ) [reverse-engineering](/tags#reverse-engineering )  
  
Oct 2, 2019

  * [[1] Memecat Battlestation](/flare-on-2019/memecat-battlestation.html)
  * [[2] Overlong](/flare-on-2019/overlong.html)
  * [3] Flarebear
  * [[4] DNS Chess](/flare-on-2019/dnschess.html)
  * [[5] demo](/flare-on-2019/demo.html)
  * [[6] bmphide](/flare-on-2019/bmphide.html)
  * [[7] wopr](/flare-on-2019/wopr.html)

![](https://0xdfimages.gitlab.io/img/flare2019-3-cover.png)

Flarebear wsa the first Android challenge, and I’m glad to see it at the
beginning while it’s still not too hard. I’ll use GenyMotion cloud to emunlate
the application, and then jadx to decompile it and see what the win condition
is. Once I find that, I can get the flag.

## Challenge

> We at Flare have created our own Tamagotchi pet, the flarebear. He is very
> fussy. Keep him alive and happy and he will give you the flag.

The file is an Android apk, which is a zip file with a specific file structure
inside:

    
    
    $ file flarebear.apk 
    flarebear.apk: Zip archive data, at least v?[0] to extract
    

## Enumlation

I created a trial account at [GenyMotion
Cloud](https://www.genymotion.com/cloud/), which allows me to quickly emulate
Android apps, and offers 1000 minutes free run time. Since I won’t need nearly
that much, it’s a good quick solution here. Alternatively, I could have set up
Android Studio or another local emulator.

After uploading and starting it, I see the app:

![1567257016512](https://0xdfimages.gitlab.io/img/1567257016512.png)

I can create a bear, feed it, play with it, clean up after it.

![1567260429188](https://0xdfimages.gitlab.io/img/1567260429188.png)
![1567260456662](https://0xdfimages.gitlab.io/img/1567260456662.png)

## RE

I’ll use the `jadx` decompiler to get the Java source for the `.apk`:

    
    
    $ jadx flarebear.apk 
    INFO  - loading ...
    INFO  - processing ...
    ERROR - finished with errors, count: 1
    

Next, I’ll look at the `AndroidManifest.xml` file, which will tell me the
functions that are called by the program:

    
    
    $ cat AndroidManifest.xml
    <?xml version="1.0" encoding="utf-8"?>
    <manifest xmlns:android="http://schemas.android.com/apk/res/android" android:versionCode="1" android:versionName="1.0" android:compileSdkVersion="28" android:compileSdkVersionCodename="9" package="com.fireeye.flarebear" platformBuildVersionCode="28" platformBuildVersionName="9">
        <uses-sdk android:minSdkVersion="23" android:targetSdkVersion="28"/>
        <application android:theme="@style/AppTheme" android:label="@string/app_name" android:icon="@mipmap/ic_launcher" android:allowBackup="true" android:supportsRtl="true" android:roundIcon="@mipmap/ic_launcher_round" android:appComponentFactory="android.support.v4.app.CoreComponentFactory">
            <activity android:name="com.fireeye.flarebear.FlareBearActivity"/>
            <activity android:name="com.fireeye.flarebear.NewActivity" android:noHistory="true"/>
            <activity android:name="com.fireeye.flarebear.CreditsActivity"/>
            <activity android:name="com.fireeye.flarebear.MainActivity">
                <intent-filter>
                    <action android:name="android.intent.action.MAIN"/>
                    <category android:name="android.intent.category.LAUNCHER"/>
                </intent-filter>
            </activity>
        </application>
    </manifest>
    

The action seems to be going on in `com.fireeye.flarebare`. I’ll go into that
directory, and find `FlareBearActivity.java`, which is where I’ll find
everything I need to solve the challenge. As I look through the source, I’ll
find the `setMood` function, which contains a call to `danceWithFlag`:

    
    
        public final void setMood() {
            if (isHappy()) {
                ((ImageView) _$_findCachedViewById(R.id.flareBearImageView)).setTag("happy");
                if (isEcstatic()) {
                    danceWithFlag();
                    return;
                }
                return;
            }
            ((ImageView) _$_findCachedViewById(R.id.flareBearImageView)).setTag("sad");
        }
    

That certainly sounds like a call I want to make. For it to happen, I need
`isEcstatic` to return true. I’ll find that code:

    
    
        public final boolean isEcstatic() {
            int state = getState("mass", 0);
            int state2 = getState("happy", 0);
            int state3 = getState("clean", 0);
            if (state == 72 && state2 == 30 && state3 == 0) {
                return true;
            }
            return false;
        }
    

So I need at some point in time the bear’s mass to be 72, its happy to be 30,
and it’s clean to be 0. How are those changed? These three functions:

    
    
        public final void changeMass(int i) {
            setState("mass", getState("mass", 0) + i);
        }
    
        public final void changeHappy(int i) {
            setState("happy", getState("happy", 0) + i);
        }
    
        public final void changeClean(int i) {
            setState("clean", getState("clean", 0) + i);
        }
    

Next I’ll find where those are called. It turns out in the three functions
that match up with buttons in the game, `feed`, `play`, and `clean`:

    
    
        public final void feed(@NotNull View view) {
            Intrinsics.checkParameterIsNotNull(view, "view");
            saveActivity("f");
            changeMass(10);
            changeHappy(2);
            changeClean(-1);
            incrementPooCount();
            feedUi();
        }
    
        public final void play(@NotNull View view) {
            Intrinsics.checkParameterIsNotNull(view, "view");
            saveActivity("p");
            changeMass(-2);
            changeHappy(4);
            changeClean(-1);
            playUi();
        }
        
        public final void clean(@NotNull View view) {
            Intrinsics.checkParameterIsNotNull(view, "view");
            saveActivity("c");
            removePoo();
            cleanUi();
            changeMass(0);
            changeHappy(-1);
            changeClean(6);
            setMood();
        }
    

So pushing `feed` will increase the bear’s mass by 10, its happy by 2, and
decrease its clean by 1. `play` will decrease its mass by 2, increase its
happy by 4, and decrease its clean by 1. `clean` will decrease its happy by 1
but increase its clean by 6. This is just a linear system of equations. I’ll
let `f` be the number of times I push Feed, `p` be the number of times I push
Play, and `c` be the number of times I push Clean. The bears total mass is
defined by:

\\[mass=10f-2p\\]

Similarly, I can write equations for happiness and clean:

\\[happiness=2f+4p-c\\] \\[clean=-f-p+6c\\]

As a matrix, that would look like:

\\[\begin{bmatrix} 10 & -2 & 0 \\\ 2 & 4 & -1 \\\ -1 & -1 & 6\end{bmatrix}
*\begin{bmatrix} f\\\p\\\c \end{bmatrix} = \begin{bmatrix} 72 \\\ 30 \\\ 0
\end{bmatrix}\\]

I can solve these by hand by calculating the inverse of the 3x3 matrix, but
there are sites that will do it for me. I’ll put it in
[here](https://www.hackmath.net/en/calculator/solving-system-of-linear-
equations?input=72%3D10x-2y%0D%0A30%3D2x%2B4y-z%0D%0A0%3D-x-y%2B6z&submit=Calculate):

![1567260560942](https://0xdfimages.gitlab.io/img/1567260560942.png)

Based on that result, I went back to the emulator, where I’ll push feed 8
times, play 4 times, and clean 2 times. When I do, I get the flag:

![1567260394495](https://0xdfimages.gitlab.io/img/1567260394495.png)

**flag: th4t_was_be4rly_a_chall3nge@flare-on.com**

[](/flare-on-2019/flarebear.html)

