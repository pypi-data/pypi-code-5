# Password-Based Key Derivation from PKCS#12

# Copyright (C) 2014-2018 koha <kkoha@msn.com>

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import hashlib
import binascii

# Constants
def SHA1_DIGEST_BLOCKLEN():
        return 64

def SHA1_DIGEST_VALUELEN():
        return 20

# Functions
def PBKDF_Adjust(a, aOffset, b):
        x = (b[len(b) - 1] & 0xff) + (a[aOffset + len(b) - 1] & 0xff) + 1
        a[aOffset + len(b) - 1] = x & 0xff

        x = x >> 8

        for i in range(len(b) - 2, -1, -1):
                x = x + (b[i] & 0xff) + (a[aOffset + i] & 0xff)
                a[aOffset + i] = x & 0xff
                x = x >> 8

        
def PBKDF_PKCS12v1(iteration, password, salt, keylen):

        v = SHA1_DIGEST_BLOCKLEN()
        u = SHA1_DIGEST_VALUELEN()
        r = iteration
        c = 0

        digest = bytearray(SHA1_DIGEST_VALUELEN())
        B = bytearray(SHA1_DIGEST_BLOCKLEN())
        key = bytearray(keylen)


        # Step 1
        Dlen = v
        D = bytearray(Dlen)

        for i in range(0, 64):
                D[i] = 1

        # Step 2
        Slen = v * ((len(salt) + v -1) / v)
        S = bytearray(Slen)

        i = 0
        while (i != v * ((len(salt) + v - 1) / v)):
                S[i] = salt[i % len(salt)]
                i = i + 1
        
        # Step 3
        Plen = v * ((len(password) + v - 1) / v)
        P = bytearray(Plen)

        i = 0
        while (i != v * ((len(salt) + v - 1) / v)):
                P[i] = password[i % len(password)]
                i = i + 1

        # Step 4
        Ilen = Slen + Plen
        I = S + P

        # Step 5
        c = (keylen + u - 1) / u

        # Step 6
        for i in range(1, c + 1):
                # Step 6 - a
                sha1Alg = hashlib.sha1()
                sha1Alg.update(D)
                #sha1Alg.update(S)
                #sha1Alg.update(P)
                sha1Alg.update(I)

                digest = sha1Alg.digest()
                #print("- digest[1] : " + binascii.hexlify(digest).upper())

                for j in range(0, r - 1):
                        sha1Alg = hashlib.sha1()
                        sha1Alg.update(digest)
                        digest = sha1Alg.digest()
                        #print("- digest[" + str(j + 2) + "] : " +  binascii.hexlify(digest).upper())

                # Step 6 - b
                for k in range(0, SHA1_DIGEST_BLOCKLEN()):
                        B[k] = digest[k % SHA1_DIGEST_VALUELEN()]

                # Strp 6 - c
                for j in range(0, Ilen / v):
                        PBKDF_Adjust(I, j * v, B)

                if (i == c):
                        for j in range(0, keylen - ((i - 1) * u)):
                                key[(i - 1) * u + j] = digest[j]
                else:
                        for j in range(0, SHA1_DIGEST_VALUELEN()):
                                key[(i - 1) * u + j] = digest[j]
                                
        key = binascii.hexlify(key)
        key = binascii.unhexlify(key)
        return key


def REMOVE_PKCS7_PADDING(argBuf):
        buf = bytearray(argBuf)
        pos = len(buf) - 1

        val = buf[pos]

        while ((0x01 <= val) and (val <= 0x10)):
                buf[pos] = 0x00
                pos = pos - 1
                if (val != buf[pos]):
                        break

        if (pos != len(buf) - 1):
                length = len(buf) - pos - 1
                buf = buf[0:len(buf) - length]

        return buf

def TestPBKDF12():
        # Test
        passwd = "1234"
        salt = "123456789"
        key = PBKDF_PKCS12v1(2, passwd , salt, 32)
        print key
        key=binascii.hexlify(key)
        print key
        # EE A7 6F A6 02 26 EF 7B E5 96 3A 58 40 3B 13 9B A4 AB B3 10 DF C1 51 85 27 6E 0D D5 82 0B 69 AE

        
if __name__ == '__main__':
        TestPBKDF12()



