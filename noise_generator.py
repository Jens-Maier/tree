class SimplexNoiseGenerator():
    def __init__(self, treeGen, seed=None):
        self.onethird = 1.0 / 3.0
#        self.onesixth = 1.0 / 6.0

#        self.A = [0, 0, 0]
#        self.s = 0.0
#        self.u = 0.0
#        self.v = 0.0
#        self.w = 0.0
#        self.i = 0
#        self.j = 0
#        self.k = 0

#        # permutation table (T)
#        if seed is None:
#            self.T = [int((x * 0x10000) % 0xFFFFFFFF) for x in range(8)]
#        else:
#            expandedSeed = []
#            random.seed(seed)
#            self.T = [random.randint(0, 2**31 - 1) for _ in range(8)]
#            

#    def coherent_noise(self, x, y, z, octaves=2, multiplier=25, amplitude=0.5, lacunarity=2, persistence=0.9):
#        v3 = mathutils.Vector([x, y, z]) / multiplier
#        val = 0.0
#        for n in range(octaves):
#            val += self.noise(v3.x, v3.y, v3.z) * amplitude
#            v3 *= lacunarity
#            amplitude *= persistence
#        return val

#    def noise(self, x, y, z):
#        self.s = (x + y + z) * self.onethird
#        self.i = self.fastfloor(x + self.s)
#        self.j = self.fastfloor(y + self.s)
#        self.k = self.fastfloor(z + self.s)

#        self.s = (self.i + self.j + self.k) * self.onesixth
#        self.u = x - self.i + self.s
#        self.v = y - self.j + self.s
#        self.w = z - self.k + self.s

#        self.A = [0, 0, 0]

#        if self.u >= self.w:
#            if self.u >= self.v:
#                hi = 0
#            else:
#                hi = 1
#        else:
#            if self.v >= self.w:
#                hi = 1
#            else:
#                hi = 2
#                
#        if self.u < self.w:
#            if self.u < self.v:
#                lo = 0
#            else:
#                lo = 1
#        else:
#            if self.v < self.w:
#                lo = 1
#            else:
#                lo = 2
#        
#        return self.kay(hi) + self.kay(3 - hi - lo) + self.kay(lo) + self.kay(0)

#    def kay(self, a):
#        self.s = (self.A[0] + self.A[1] + self.A[2]) * self.onesixth
#        x = self.u - self.A[0] + self.s
#        y = self.v - self.A[1] + self.s
#        z = self.w - self.A[2] + self.s
#        t = 0.6 - x * x - y * y - z * z

#        h = self.shuffle(self.i + self.A[0], self.j + self.A[1], self.k + self.A[2])
#        self.A[a] += 1
#        if t < 0:
#            return 0
#        b5 = h >> 5 & 1
#        b4 = h >> 4 & 1
#        b3 = h >> 3 & 1
#        b2 = h >> 2 & 1
#        b1 = h & 3

#        p, q, r = self.get_pqr(b1, x, y, z)

#        if b5 == b3:
#            p = -p
#        if b5 == b4:
#            q = -q
#        if b5 != (b4 ^ b3):
#            r = -r
#        t *= t
#        if b1 == 0:
#            return 8 * t * t * (p + q + r)
#        if b2 == 0:
#            return 8 * t * t * (q + r)
#        return 8 * t * t * r

#    def get_pqr(self, b1, x, y, z):
#        if b1 == 1:
#            p, q, r = x, y, z
#        elif b1 == 2:
#            p, q, r = y, z, x
#        else:
#            p, q, r = z, x, y
#        return p, q, r

#    def shuffle(self, i, j, k):
#        return self.bb(i, j, k, 0) + self.bb(j, k, i, 1) + self.bb(k, i, j, 2) + self.bb(i, j, k, 3) + \
#               self.bb(j, k, i, 4) + self.bb(k, i, j, 5) + self.bb(i, j, k, 6) + self.bb(j, k, i, 7)

#    def bb(self, i, j, k, B):
#        return self.T[self.b(i, B) << 2 | self.b(j, B) << 1 | self.b(k, B)]

#    def b(self, N, B):
#        return N >> B & 1

#    def fastfloor(self, n):
#        return int(n) if n > 0 else int(n) - 1