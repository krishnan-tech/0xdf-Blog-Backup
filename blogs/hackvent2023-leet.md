# Hackvent 2023 - Leet

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [crypto](/tags#crypto )
[sagemath](/tags#sagemath ) [rsa](/tags#rsa ) [bruteforce](/tags#bruteforce )  
  
Jan 2, 2024

  * [easy](/hackvent2023/easy)
  * [medium](/hackvent2023/medium)
  * [hard](/hackvent2023/hard)
  * leet

![](../img/hackvent2023-leet-cover.png)

I only got to solve one of the three leet challenges. It was a cryptography
challenge where I can brute force two parameters known to be between 0 and
1000 and then work backwards to figure out q based on a hint leaked in the
output. From there, it’s simple RSA.

## HV23.22

### Challenge

![HackVent ball22](../img/hvball-leet-22.png) | HV23.22 Secure Gift Wrapping Service  
---|---  
Categories: |  ![exploitation](../img/hv-cat-exploitation.png)EXPLOITATION   
Level: | leet  
Author: |  darkice   
  
> This year, a new service has been launched to support the elves in wrapping
> gifts. Due to a number of stolen gifts in recent days, increased security
> measures have been introduced and the gifts are being stored in a secret
> place. As Christmas is getting closer, the elves need to load the gifts onto
> the sleigh, but they can’t find them. The only hint to this secret place was
> probably also packed in one of these gifts. Can you take a look at the
> service and see if you can find the secret?
>
> * * *
>
> Please note that the libc file in the downloadable archive has been changed
> to match the one in the Docker.
>
> Exploit the Docker and get the flag!
>
> The `sha256sum` of the downloadable archive `public.tar.xz` is
> `a0a416c96fb8daa6b2d50c245ab9b914b64431f4dbad381fbbad52b782f43297`

### Not Solved

I didn’t get to solve this challenge.

## HV23.23

### Challenge

![HackVent ball23](../img/hvball-leet-23.png) | HV23.23 Roll your own RSA  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO   
Level: | leet  
Author: |  cryze   
  
> Santa wrote his own script to encrypt his secrets with RSA. He got inspired
> from the windows login where you can specify a hint for your password, so he
> added a hint for his own software. This won’t break the encryption, will
> it?The download has (some parts of) the application.

### Solve

#### Script

The download contains a Python script and an `output.txt`.

The Python script encrypts a `FLAG` constant:

    
    
    from Crypto.Util.number import *
    from sage.all import *
    from secret import FLAG, x, y
    import random
    
    # D = {x∈ℕ | 0 ≤ x ≤ 1000}
    # D = {y∈ℕ | 0 ≤ y ≤ 1000}
    
    def enc(flag, polynomial_function):
        p = getStrongPrime(512)
        q = getStrongPrime(512)
        N = p * q
        e = 65537
        hint = p**3 - q**8 + polynomial_function(x=x)
        encrypted = pow(bytes_to_long(flag), e, N)
        print(f"{N=}")
        print(f"{e=}")
        print(f"{hint=}")
        print(f"{encrypted=}")
    
    
    def generate_polynomial_function(seed):
        x = SR.var("x")
        random.seed(seed)
        grade = random.choice([2,3])
        a = random.randint(9999, 999999)
        b = random.randint(8888, 888888)
        c = random.randint(7777, 777777)
    
        if grade == 2:
            y_x = a*x**2+b*x+c
        if grade == 3:
            d = random.randint(6666, 666666)
            y_x = a*x**3+b*x**2+c*x+d
    
        print(a+b+c)
        return y_x
    
    
    y_x = generate_polynomial_function(y)
    enc(FLAG.encode(), y_x)
    

It sends several things to STDOUT, all of which is found in `output.txt`:

    
    
    1709262
    N=143306145185651132108707685748692789834391223254420921250753369412889732941905250889012412570851623535344424483564532684976892052830348014035303355261052741504390590825455129003262581199117432362073303998908141781601553213103109295898711066542593102305069363965164592663322089299134520383469241654273153506653
    e=65537
    hint=-367367861727692900288480576510727681065028599304486950529865504611346573250755811691725216308460956865709134086848666413510519469962840879406666853346027105744846872125225171429488388383598931153062856414870036460329519241754646669265989077569377130467115317299086371406081342249967666782962173513369856861858058676451390037278311316937161756731165929187543148639994660265783994439168583858109082136915810219786390452412584110468513829455001689531028969430907046738225668834761412112885772525079903072777443223873041260072918891696459905352737195384116938142788776947705026132197185926344278041831047013477983297898344933372775972141179163010102537733004410775357501267841845321271140399200044741656474378808452920297777911527159803159582800816951547394087190043792625664885536154225227819735800442814065528155407746556297892931242208688533313054308779657788077807340045465701247210553988059519291363634253248268722975827616752514688291723712069675405995149499947239454505797412122124933836396842943540518521648803348207619354854290787969076059265170474203200482079680136404766877617679652611682327535174212016390608658107555103054183393719700027186913354158961245998591486268846852581402900857595817303811471853325463202817521164757
    encrypted=72792762778232160989381071629769766489971170790967414271032682193723004039685063639675377805724567838635943988752706743932748347933013530918279285456553768626331874756049006544553546268049053833014940495217179504587162478219970564159885619559723778613379425375733026859684952880028997538045791748027936366062
    

The first number is the result of `print(a+b+c)`. The others are labeled.

#### Strategy

This is RSA encryption, so if I can get `p` and `q`, I can calculate
everything else I need to decrypt. I know `N = p*q`, but I also get this
`hint` output which is `p**3 - q**8 + polynomial_function(x)`. I don’t know
`x`, but I know it’s between 0 and 1000. If I can get the polynomial, I can
brute force x.

To get the polynomial, I’ll need to know `y`, which is also unknown, but
between 0 and 1000. Because I have the sum of `a`, `b`, and `c`, I can easily
brute force `y`.

#### Get y

`y` is an unknown value between 0 and 1000 that is used to generate a
polynomial. I’ll use code from `generate_polynomial_function` to check `y`
inputs against the `a+b+c` outputs:

    
    
    def crack_y():
        for y in range(1000):
            random.seed(y)
            random.choice([2,3])
            a = random.randint(9999, 999999)
            b = random.randint(8888, 888888)
            c = random.randint(7777, 777777)
            if a+b+c == 1709262:
                print(f"Found y: {y}")
                return y
    

#### Crack x, q

To get `x`, I just need to generate a polynomial with `y`, and then solve the
`hint` equation for each `x` between 0 and 1000, breaking when I get exactly
two answers. I’ll use SageMath to solve the equation:

    
    
    def crack_x(y):
        y_x = generate_polynomial_function(y)
        for x in range(1000):
            q = var('q')
            equation = hint == (N/q)**3 - q**8 + y_x(x=x)
            print(f"\r{x}", end="")
            try:
                roots = equation.roots()
                print(f"\rFound x: {x}")
                print(f"Found q: {roots[0][0]}")
                return x, int(roots[0][0])
            except RuntimeError:
                pass
        raise
    

#### Decrypt

With `q`, I can now get `p`, then `phi` and `d`, which is used to decrypt:

    
    
    y = crack_y()
    x, q = crack_x(y)
    p = N//q
    print(f"Found p: {p}")
    phi = (p-1)*(q-1)
    d = pow(e, -1, phi)
    pt = pow(ct, d, N)
    print(f"Flag: {long_to_bytes(pt).decode()}")
    

Getting Sagemath installed in my VM was a pain, so I just opted for Docker:

    
    
    oxdf@hacky$ docker run -it -u root -v .:/day23 sagemath/sagemath bash
    root@fbbf42ba5b86:~#
    

After running `pip install pycryptodome`, running the current script in
`/day23` solves the challenge:

    
    
    root@fbbf42ba5b86:/day23# time python3 dec.py 
    Found y: 787
    Found x: 692
    Found q: 11766238441137316218698559717070508606046977055528210983326091441049009527090037271072944725167437804861554714103321826526867364254290450294447086896338759
    Found p: 12179435756173513536974896795065942195337250662711676240184873598482470068786941630453314528951912732394640958491561461957261830568584848314092787092062267
    Flag: HV23{1t_w4s_4b0ut_t1m3_f0r_s0me_RSA_4g41n!}
    
    real    1m14.429s
    user    2m33.437s
    sys     0m2.805s
    

**Flag:`HV23{1t_w4s_4b0ut_t1m3_f0r_s0me_RSA_4g41n!}`****

## HV23.24

### Challenge

![HackVent ball24](../img/hvball-leet-24.png) | HV23.24 Santa's Shuffled Surprise  
---|---  
Categories: |  ![reverse_engineering](../img/hv-cat-reverse_engineering.png)REVERSE_ENGINEERING  
![forensic](../img/hv-cat-forensic.png)FORENSIC  
Level: | leet  
Author: |  JokerX   
  
> Santa found a dusty old floppy disk in his basement. He started the disk in
> his A500, but the QR code looks shuffled. Can you help him to read the QR
> code?

### Solution

I didn’t get to solve this challenge.

[« hard](/hackvent2023/hard)

[](/hackvent2023/leet)

