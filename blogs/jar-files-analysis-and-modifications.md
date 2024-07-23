# Jar Files: Analysis and Modifications

[java](/tags#java ) [reverse-engineering](/tags#reverse-engineering )
[decompile](/tags#decompile ) [jar](/tags#jar ) [recompile](/tags#recompile )
[procyon](/tags#procyon ) [javac](/tags#javac )  
  
Aug 8, 2020

  * [Fatty Walkthrough](/2020/08/08/htb-fatty.html)
  * Jar File Cheat Sheet

![](https://0xdfimages.gitlab.io/img/jar-cover.png)

I recently ran into a challenge where I was given a Java Jar file that I
needed to analyze and patch to exploit. I didn’t find many good tutorials on
how to do this, so I wanted to get my notes down. For now it’s just a cheat
sheet table of commands. _Updated 8 Aug 2020_ : Now that Fatty from HackTheBox
has retired, I’ve updated this post to reflect some examples.

## Jar File Structure

A Jar (Java Archive) file is just a ZIP file that contains Java class
(compiled) files and the necessary metadata and resources (text, images). That
said, they are very picky, and it can be important how to interact with them
when pulling stuff in and out.

The Jar will have a `META-INF/` folder at the root, which contains metadata
such as signatures, license, and the `MANIFEST.MF` file. For example, in
`fatty-client.jar`:

    
    
    root@kali# ls META-INF/
    1.RSA  LICENSE      MANIFEST.MF  NOTICE      services                    spring-context.kotlin_module  spring.factories  spring.handlers  spring.tld      spring-web.kotlin_module
    1.SF   license.txt  maven        notice.txt  spring-beans.kotlin_module  spring-core.kotlin_module     spring-form.tld   spring.schemas   spring.tooling  web-fragment.xml
    

The `MANIFEST.MF` file provides the Jdk version, as well as optionally a
`Main-Class` attribute. If `Main-Class` is present, this Jar can be executed
without providing a class name, which makes it an executable Jar. The manifest
file also contains base64 format hashes of the other files in the archive.

    
    
    Manifest-Version: 1.0
    Archiver-Version: Plexus Archiver
    Built-By: root
    Sealed: True
    Created-By: Apache Maven 3.3.9
    Build-Jdk: 1.8.0_232
    Main-Class: htb.fatty.client.run.Starter
    
    Name: META-INF/maven/org.slf4j/slf4j-log4j12/pom.properties
    SHA-256-Digest: miPHJ+Y50c4aqIcmsko7Z/hdj03XNhHx3C/pZbEp4Cw=
    
    Name: org/springframework/jmx/export/metadata/ManagedOperationParameter.class
    SHA-256-Digest: h+JmFJqj0MnFbvd+LoFffOtcKcpbf/FD9h2AMOntcgw=
    ...[snip]...
    

## Initial Work

### Unpack / Repack

Before taking on something like unpack, modify, repack, I’ll start with unpack
then repack to make sure I can do that without errors. I’ll make a directory,
`unzipped`, and then unzip the Jar into it:

    
    
    root@kali# unzip -d unzipped/ fatty-client.jar
    Archive:  fatty-client.jar
      inflating: unzipped/META-INF/MANIFEST.MF
      inflating: unzipped/META-INF/1.SF
      ...[snip]...
    

Now, from within that directory, I’ll run `jar -cmf META-INF/MANIFEST.MF
../new.jar *`:

  * `-c` \- Create new jar file.
  * `-m` \- include a preexisting manifest; I had issues with the manifest coming out blank without this flag.
  * `-f`\- specifies the jar file to be created.

Now I can run `java -jar new.jar` and it works:

![image-20200320162159460](https://0xdfimages.gitlab.io/img/image-20200320162159460.png)

### Signatures

#### Updating the Manifest

One of the first things I had to do in Fatty was to modify a text file at the
root of the Jar, `beans.xml`, to get the client to connect to the right port.
I can edit that in my unzipped folder, and then recreate the Jar just like
above. I can run it, but when I try to submit something to the server, it
errors out:

    
    
    root@kali# java -jar new.jar                   
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true          
    Exception in thread "AWT-EventQueue-0" org.springframework.beans.factory.BeanDefinitionStoreException: Unexpected exception parsing XML document from class path resource [beans.xml]; nested excep
    tion is java.lang.SecurityException: SHA-256 digest error for beans.xml
            at org.springframework.beans.factory.xml.XmlBeanDefinitionReader.doLoadBeanDefinitions(XmlBeanDefinitionReader.java:419)
    ...[snip]...
    

This is the important part : `java.lang.SecurityException: SHA-256 digest
error for beans.xml`.

I need to update the hash in the manifest. If I look at the first file in the
manifest after the header info, I can see the hash format:

    
    
    Name: META-INF/maven/org.slf4j/slf4j-log4j12/pom.properties
    SHA-256-Digest: miPHJ+Y50c4aqIcmsko7Z/hdj03XNhHx3C/pZbEp4Cw=
    

That has format is different that I typically see. It looks base64 encoded.
I’ll use the following command to replicate it:

    
    
    root@kali# sha256sum META-INF/maven/org.slf4j/slf4j-log4j12/pom.properties | cut -d' ' -f1 | xxd -r -p | base64
    miPHJ+Y50c4aqIcmsko7Z/hdj03XNhHx3C/pZbEp4Cw=
    

That takes the standard hex hash output, uses `cut` to isolate it, `xxd` to
convert it to binary, and `base64` to encode it. I’ll calculate for the new
`beans.xml`:

    
    
    root@kali# sha256sum beans.xml | cut -d' ' -f1 | xxd -r -p | base64
    f/D4a+DZ53lRwjwkcYauGCDdJ5AJT0bZ9wsIBzqDdJ8=
    

#### Removing Signing

After updating and re-Jar-ing, a new error on running:

    
    
    root@kali# java -jar new2.jar 
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    Error: A JNI error has occurred, please check your installation and try again
    Exception in thread "main" java.lang.SecurityException: invalid SHA-256 signature file digest for beans.xml
    ...[snip]...
    

There are also signatures for the Jar, and I want to remove them. The easiest
way to do that is just to remove the signature files, as [this StackOverflow
post](https://stackoverflow.com/questions/8176166/invalid-sha1-signature-file-
digest) suggests.

    
    
    root@kali# ls META-INF/*.SF META-INF/*.DSA META-INF/*.RSA 2>/dev/null
     META-INF/1.RSA   META-INF/1.SF
    
    root@kali# rm META-INF/1.SF META-INF/1.RSA 
    

Now if I build the Jar, it runs fine.

## Modifying Compiled Classes

### Decompiling

#### Install Procyon

To decompile, I used the [Procyon Java
decompiler](https://bitbucket.org/mstrobel/procyon/downloads/). To “install”
it, I just downloaded the latest Jar from that link, and dropped a link into
`/usr/local/bin/` so I could just type `procyron` to use it:

    
    
    root@kali# ln -s /opt/procyron/procyon-decompiler-0.5.36.jar /usr/local/bin/procyon
    

#### Single File

With `procyon`, its simplest to operate from the root directory of the
unzipped Jar, at least if you’re going to output files. If I run `procyon
[path to class file]`, the decompiled Java will output to STDOUT, to the
terminal.

`procyon -o . [path to class]` will output that Java to a file, with a
directory structure to match how the classes are set up. For the Fatty
example, from the root of the unzipped Jar, it creates

    
    
    root@kali# find . -name *.java
    root@kali# procyon -o . htb/fatty/client/gui/ClientGuiTest.class
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    Decompiling htb/fatty/client/gui/ClientGuiTest.class...
    root@kali# find . -name *.java
    ./htb/fatty/client/gui/ClientGuiTest.java
    

The directory structure is the same, even if the output directory isn’t the
local one:

    
    
    root@kali# procyon htb/fatty/client/gui/ClientGuiTest.class -o /tmp
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    Decompiling htb/fatty/client/gui/ClientGuiTest.class...
    root@kali# find /tmp -name *.java
    /tmp/htb/fatty/client/gui/ClientGuiTest.java
    

#### Entire Jar

I can also decompile an entire Jar, with the syntax `procyon -jar [jar] -o
[output directory]`. Sites like
[javadecompiles.com](http://www.javadecompilers.com/) will do this for you,
and provide back a zip with all the source. One note of caution - This option
returns all the `.java` source files. It does not return the metadata, so to
recompile, or repackage, you’ll need to work from a unzipped version.

### ReCompiling

I’ll make some small change to the `.java` source I decompiled, and now I need
to recompile it to put it back into a Jar to run. I’ll use `javac`, which
comes in the JDK I downloaded. I’ll first run `update-alternatives` to make
sure I’m using the version that matches what was in the `MANIFEST.MF` file.

The example I’m working with from fatty first presents a login form when run.
I’ll set it so that when that form loads, the username “qtc” is already in the
username field, by adding `"qtc"` in this line in the decompiled
`ClientGuiTest.java`:

    
    
    (this.tfUsername = new JTextField("qtc")).setBounds(294, 218, 396, 27);
    

I’ll want to compile from the root of the unzipped Jar. It is not uncommon to
get errors compiling from decompiled source:

    
    
    root@kali# javac htb/fatty/client/gui/ClientGuiTest.java 
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    htb/fatty/client/gui/ClientGuiTest.java:276: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    htb/fatty/client/gui/ClientGuiTest.java:294: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    htb/fatty/client/gui/ClientGuiTest.java:313: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    htb/fatty/client/gui/ClientGuiTest.java:332: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    htb/fatty/client/gui/ClientGuiTest.java:351: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    htb/fatty/client/gui/ClientGuiTest.java:375: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    htb/fatty/client/gui/ClientGuiTest.java:393: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    htb/fatty/client/gui/ClientGuiTest.java:411: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    htb/fatty/client/gui/ClientGuiTest.java:429: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    htb/fatty/client/gui/ClientGuiTest.java:447: error: variable ex might not have been initialized
                        final Exception e2 = ex;
                                             ^
    10 errors
    

Looking in the code, there are 10 places where exception handling looks like:

    
    
                    catch (MessageBuildException | MessageParseException ex2) {
                        final Exception ex;
                        final Exception e2 = ex;
                        JOptionPane.showMessageDialog(controlPanel, "Failure during message building/parsing.", "Error", 0);
                    }
    

Neither `ex` nor `e2` are ever referenced after this, so I’ll just remove
those two lines.

Now compiling works fine:

    
    
    root@kali# javac htb/fatty/client/gui/ClientGuiTest.java 
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    

This is working from the unzipped Jar file structure, and the compilation just
replaced `htb/fatty/client/gui/ClientGuiTest.class`. Now I can re-package the
Jar just like before:

    
    
    root@kali# jar -cmf META-INF/MANIFEST.MF ../mod.jar *
    Picked up _JAVA_OPTIONS: -Dawt.useSystemAAFontSettings=on -Dswing.aatext=true
    

And on running the new Jar, the username field is filled in:

![image-20200321061428365](https://0xdfimages.gitlab.io/img/image-20200321061428365.png)

## Cheat Sheet

Here’s all the commands from this post (and a few extras that are useful with
Jars):

Task | Command  
---|---  
Run Jar | `java -jar [jar]`  
Unzip Jar | `unzip -d [output directory] [jar]`  
Create Jar | `jar -cmf META-INF/MANIFEST.MF [output jar] *`  
Base64 SHA256 | `sha256sum [file] | cut -d' ' -f1 | xxd -r -p | base64`  
Remove Signing | `rm META-INF/*.SF META-INF/*.RSA META-INF/*.DSA`  
Delete from Jar | `zip -d [jar] [file to remove]`  
Decompile class | `procyon -o . [path to class]`  
Decompile Jar | `procyon -jar [jar] -o [output directory]`  
Compile class | `javac [path to .java file]`  
  
It’s always important to track file structure and your relative directory.
I’ve found it’s easiest to work out of the root directory of the unzipped Jar.

[Procyon](https://bitbucket.org/mstrobel/procyon/wiki/Java%20Decompiler)
“installed” by downloading Jar and creating a symlink: `ln -s
/opt/procyron/procyon-decompiler-0.5.36.jar /usr/local/bin/procyon`.

[](/2020/08/08/jar-files-analysis-and-modifications.html)

