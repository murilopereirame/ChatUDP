from secrets import randbits, randbelow
from math import gcd


class RSA:
    def __init__(self):
        self.primes(16)
        self.calcVars()

    def isPrime(self, num):
        if num <= 1:
            return False        
        elif num <= 3:
            return True
        elif num % 2 == 0 or num % 3 == 0:
            return False        
        i = 5        
        while i**2 <= num:
            if num % i == 0 or num % (i + 2) == 0:
                return False            
            i += 6            
        return True

    def calcEGCD(self, a, b):
        if a == 0:
            return b, 0, 1
        g, x, y = self.calcEGCD(b % a, a)
        return g, y - (b // a) * x, x

    def modInverse(self, a, m):
        g, x, y = self.calcEGCD(a, m)

        if g != 1:
            return 0

        return x % m

    def getPublicKey(self):
        return self.n, self.e

    def getPrivateKey(self):
        return self.p, self.q, self.d

    def primes(self, bits):
        self.p = randbits(bits)
        self.q = randbits(bits)

        while not self.isPrime(self.p):
            self.p = randbits(bits)

        while self.p == self.q or not self.isPrime(self.q):
            self.q = randbits(bits)

    def calcVars(self):
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)
        self.generateE()
        self.d = self.modInverse(self.e, self.phi)

    def generateE(self):
        self.e = randbelow(self.phi)
        if self.e < 2 or gcd(self.e, self.phi) != 1:
            self.generateE()


    def encryptString(self, message, public):
        n, e = public
        msg = [ord(cc) for cc in list(message)]
        ct = [str(pow(asc, e, n)) for asc in msg]

        return ' '.join(ct)

    def decryptString(self, message, private):
        p, q, d = private

        message = message.split(' ')        
        asc = [str(pow(int(cc), d, p * q)) for cc in message]
        msg = [chr(int(ac)) for ac in asc]

        return ''.join(msg)
