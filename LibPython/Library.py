"""
Author: Spandan Anupam
As part of the Computational Physics course at NISER
"""
# Calls numpy for basic array functionality. See julia code in ../LibJulia for a more fleshed out (mostly) dependency free code
import numpy as np
from sys import exit
class MatInv:
    def __init__(self):
        pass

    def gauss_jordan(self, M, m):
        """
        Gauss Jordan
        """
        A = np.copy(M)
        b = np.copy(m)
        rows = range(A.shape[0])
        for row in rows:
            rng = list(np.copy(rows))
            rng.pop(row)
            for other in rng:
                mult = A[other, row] / A[row, row]
                A[other, :] -= A[row, :] * mult
                b[other] -= b[row] * mult
        
        norm = A.sum(axis=1)
        return b / norm
    
    def sub_helper(self, A, b, prop="forward"):
        n = A.shape[0]
        x = np.zeros(n)
        if prop=="forward":
            for i in range(n):
                x[i] = (b[i] - np.dot(A[i, :i], x[:i])) / A[i, i]
        else:
            for i in reversed(range(n)):
                x[i] = (b[i] - np.dot(A[i, i+1:], x[i+1:])) / A[i, i]
        return x

    def lu_decom(self, A, b, returnlu=False):
        """
        LU decomposition
        """
        nn = A.shape
        L = np.identity(nn[0])
        U = np.copy(A)
        for i in range(nn[0]):
            for j in range(i+1,nn[1]):
                L[j, i] = U[j, i] / U[i, i]
                U[j, :] -= L[j, i] * U[i, :]

        y = self.sub_helper(L, b)
        x = self.sub_helper(U, y, "backward")
        if returnlu:
            return x, L, U
        else:
            return x

    def chol_decom(self, A, b, returnch=False):
        """
        Cholesky decomposition
        """
        nn = A.shape
        L = np.identity(nn[0])
        for i in range(nn[0]):
            for j in range(i+1):
                a = 0
                for k in range(j):
                    a += L[i, k] * L[j, k]

                if (i == j):
                    L[i, j] = np.sqrt(A[i, i] - a)
                else:
                    L[i, j] = (1.0 / L[j, j] * (A[i, j] - a))

        y = self.sub_helper(L, b)
        x = self.sub_helper(L.T, y, "backward")
        if returnch:
            return x, L, L.T
        else:
            return x

    def jacobi(self, A, b, stop=1e-9, residue=False):
        """
        Jacobi Iteration
        """
        x = np.ones((A.shape[0], ))
        oldx = np.zeros((A.shape[0], ))
        res = []
        while np.linalg.norm(oldx - x) > stop:
            res.append(np.linalg.norm(oldx - x))
            if np.linalg.norm(oldx - x) > 1e2: 
                raise Exception("Did not converge, make sure coefficient matrix is diagonal heavy")
            oldx = np.copy(x)
            for i in range(len(b)):
                summ = np.dot(A[i, :i], x[:i]) + np.dot(A[i, i+1:], x[i+1:])
                x[i] = (1/A[i, i]) * (b[i] - summ)
        if residue:
            return x, res
        else:
            return x

    def gauss_siedel(self, A, b, stop=1e-9, residue=False):
        """
        Gauss Siedel
        """
        x = np.ones((A.shape[0], ))
        oldx = np.zeros((A.shape[0], ))
        res = []
        while np.linalg.norm(oldx - x) > stop:
            res.append(np.linalg.norm(oldx - x))
            if np.linalg.norm(oldx - x) > 1e2: 
                raise Exception("Did not converge, make sure coefficient matrix is diagonal heavy")
            oldx = np.copy(x)
            for i in range(len(b)):
                summ = np.dot(A[i, :i], x[:i]) + np.dot(A[i, i+1:], oldx[i+1:])
                x[i] = (1/A[i, i]) * (b[i] - summ)
        if residue:
            return x, res
        else:
            return x
            
    def conjugate_gradient(self, A, b, stop=1e-9, residue=False):
        """
        Conjugate Gradient
        """

        x = np.random.random(A.shape[0])
        d = b - A@x
        r = np.copy(d)
        con = 0
        res = []

        for i in range(A.shape[0]):
            Ad = A@d
            modr = r@r

            α = (r@r) / (d@Ad)
            x += α * d
            β = 1 / modr
            r -= α * (Ad)

            modr = r@r
            res.append(np.sqrt(modr))

            if (np.sqrt(modr) < stop):
                break 
            β *= modr
            d = r + β * d
            con += 1
            
        if con == A.shape[0]:
            raise Exception("Passed n loops, possibly did not converge")
        if residue:
            return x, res
        else:
            return x

    def inverse(self, A, func, residue=False):
        n = A.shape[0]
        amat = np.identity(n)
        reslist = []
        for i in range(n):
            a = amat[:, i]
            if residue:
                amat[:, i], res = func(A, a, residue=residue)
                reslist.append(res)
            else:
                amat[:, i] = func(A, a)
        if residue:
            return amat, reslist
        else:
            return amat

class Eigen:
    def __init__(self):
        pass

    def power(self, M, stop=1e-3):
        """
        Power Method
        """
        N = M.shape[0]
        A = np.copy(M)
        eiglist = []
        veclist = []

        for i in range(N):
            x =  np.ones((N, 1))
            v = x 
            vold = np.zeros(N)
            λold = 0.0; λ = -1.0
            while abs(λ - λold) > stop:
                vold = v; v = np.dot(A, v)
                λold = λ; λ = np.dot(v.T, x)/np.dot(vold.T, x)
            
            v /= np.linalg.norm(v)
            eiglist.append(np.sum(λ))
            veclist.append(np.squeeze(v))
            R = λ * np.dot(v, v.T)
            A = A - R
        return eiglist, veclist

    def givens(self, A, k, l):
        """
        Givens Rotation
        """
        β = (A[l, l] - A[k, k]) / (2*A[k, l])
        t = np.sign(β) / (np.abs(β) + np.sqrt(β**2 + 1))
        c = 1/np.sqrt(t**2+1)
        s = c * t
        return c, s

    def jacobi(self, M):
        """
        Jacobi Rotation
        """
        A = np.copy(M)
        n = A.shape[0]
        I = np.identity(n)
        for l in range(n):
            for k in range(l+1, n):
                s, c = self.givens(A, k, l)
                B = np.copy(A)

                for i in range(n):
                    for j in range(n):
                        if (i,j)==(k,k):
                            A[i,j] = c**2*B[k, k] + s**2*B[l, l] - 2*s*c*B[k, l]
                        elif (i,j)==(l,l):
                            A[i,j] = c**2*B[k, k] + s**2*B[l, l] + 2*s*c*B[k, l]
                        elif ((i,j)==(k,l) or (i,j)==(l,k)):
                            A[i, j] = 0
                        elif (i==k or j==k):
                            A[i, j] = c*B[i, k] - s*B[i, l]
                        elif (i==l or j==l):
                            A[i, j] = c*B[i, l] + s*B[i, k]
        return A

class Statistics:
    def __init__(self):
        pass

    def jackknife(self, x):
        """
        Jackknife Resampling
        """
        n = x.shape[0]
        xlist = []
        for i in range(n):
            xlist.append(np.copy(x).pop(i))
        return xlist

    def linear_regression(self, x, y, yerr, errfull=False):
        """
        Linear Regression
        """
        S =  np.sum(1 / (yerr**2))
        Sx = np.sum(x / (yerr**2))
        Sy = np.sum(y / (yerr**2))
        Sxx = np.sum((x**2) / (yerr**2))
        Syy = np.sum((y**2) / (yerr**2))
        Sxy = np.sum((x*y) / (yerr**2))

        Δ = S*Sxx - (Sx)**2
        c = (Sxx*Sy - Sx*Sxy)/Δ
        m = (S*Sxy - Sx*Sy)/Δ
        yfit = c + m*x

        σ2c = Sxx/Δ
        σ2m = S/Δ
        cov = -Sx/Δ
        r2 = Sxy/(Sxx*Syy)

        if errfull:
            return yfit, m, c, σ2m, σ2c, cov, r2
        else:
            return yfit, m, c

    def chisq(self, yexp, yfit, yerr):
        """
        Chi Sq Goodness
        """
        χsq = np.sum(((yexp-yfit)/yerr)**2)
        χsqn = χsq / (yexp.shape[0]-2)
        return χsq, χsqn

    def polynomial(self, n, x):
        return x**n

    def chebyshev(self, n, x):
        if n == 0:
            return 1
        elif n == 1:
            return (2*x - 1)
        elif n == 2:
            return (8*x**2 - 8*x + 1)
        elif n == 3:
            return (32*x**3 - 48*x**2 + 18*x - 1)
        elif n == 4:
            return (128*x**4 - 256*x**3 + 160*x**2 - 32*x + 1)

    def legendre(self, n, x):
        if n == 0:
            return 1
        elif n == 1:
            return x
        elif n == 2:
            return 0.5*(3*x**2 - 1)
        elif n == 3:
            return 0.5*(5*x**3 - 3*x)
        elif n == 4:
            return 0.125*(35*x**4 - 30*x**2 + 3)
        elif n == 5:
            return 0.125*(63*x**5 - 70*x**3 + 15*x)
        elif n == 6:
            return 0.0625*(231*x**6 - 315*x**4 + 105*x**2 - 5)

    def polyfit(self, x, y, yerr, n=2, basis="polynomial"):
        """
        Polynomial Fitting
        """
        if basis == "polynomial":
            base = self.polynomial
        elif basis == "chebyshev":
            base = self.chebyshev
        elif basis == "legendre":
            base = self.legendre

        A = np.zeros((n+1, n+1))
        a = np.zeros(n+1)
        for i in range(n+1):
            for j in range(n+1):
                a[j] = sum((base(j, x) * y) / yerr**2)
                A[i, j] = np.sum(base(i, x)*base(j, x) / yerr**2)
        return MatInv().gauss_siedel(A, a)

class Fourier:
    def __init__(self):
        pass

    def discrete(self, x):
        """
        Discrete Fourier Transform
        """
        n = x.shape[0]
        X = complex(np.zeros((n,)))
        for k in range(n):
            for i in range(n):
                X[k] += x[i] * np.exp(-(2j*np.pi*i*k)/n)
        return X

class UnloadedMatrix:
    """
    Matrix class to facilitate storage-less computation. 
    * Matrix multiplication implemented only for Matrix, Vector
    * __mult__ works only in one direction (Matrix * const)
    Requires: size, shape, args
    Returns: UnloadedMatrix
    """
    def __init__(self, N, mu, m):
        self.size = N**2
        self.shape = (self.size, self.size)
        self.mu = mu
        self.m = m
        self.mul = 1
    
    def delta(self, i, j):
        return float(i==j)
    
    def __getitem__(self, idx):
        i = idx[0]
        j = idx[1]
        mu = self.mu
        x1 = i // np.sqrt(self.shape[0])
        x2 = i % np.sqrt(self.shape[1])
        y1 = j // np.sqrt(self.shape[0])
        y2 = j % np.sqrt(self.shape[1])

        first = self.delta(x1 - mu[0][0], y1) * self.delta(x2 - mu[0][1], y2) + self.delta(x1 - mu[1][0], y1) * self.delta(x2 - mu[1][1], y2)
        second = self.delta(x1 + mu[0][0], y1) * self.delta(x2 + mu[0][1], y2) + self.delta(x1 + mu[1][0], y1) * self.delta(x2 + mu[1][1], y2)
        third = (self.m**2 - 1) * self.delta(x1, y1) * self.delta(x2, y2)

        return self.mul * (0.5 * (first + second) + third)

    def __str__(self):
        start = "UnloadedMatrix(["
        for i in range(self.size):
            for j in range(self.size):
                if (i==0 and j==0):
                    start += "["+str(self.__getitem__((i, j)))+", "
                elif (j==0):
                    start += "\t\t["+str(self.__getitem__((i, j)))+", "
                elif (j==(self.size-1) and i!=(self.size-1)):
                    start += str(self.__getitem__((i, j)))+"],\n"
                elif (j==(self.size-1) and i==(self.size-1)):
                    start += str(self.__getitem__((i, j)))+"]"
                else:
                    start += str(self.__getitem__((i, j)))+", "
        end = "])"
        return start+end

    def __mul__(self, other):
        self.mul = other
        return self

    def __matmul__(self, other):
        if self.shape[1] != other.shape[0]:
            raise ValueError("Matrices not compatible")
        
        if len(other.shape) == 2:
            cols = []
            for col in other.T:
                dotval = np.zeros_like(col)
                for i in range(self.shape[0]):
                    for j in range(self.shape[1]):
                        dotval[i] += self.__getitem__((i, j)) * col[j]
                cols.append(dotval)
            
            return np.c_[cols]

        dotval = np.zeros_like(other)
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                dotval[i] += self.__getitem__((i, j)) * other[j]

        return dotval

class DiffEq:
    def __init__(self, function, t, yinit, paramlist):
        self.func = function
        self.h = t[1] - t[0]
        self.t = t
        self.l = len(yinit)
        self.y = np.reshape(np.array(yinit), (1, self.l))
        self.params = paramlist

    def forward_euler(self):
        for n in range(len(self.t)):
            tn = self.t[n]
            yn = self.y[-1]
            h = self.h
            params = self.params
            yfin = yn + h*(self.func(tn, yn, params))
            ynext = np.reshape(yfin, (1, self.l))
            self.y = np.concatenate((self.y, ynext), axis=0)

        return self.y

    def predictor_corrector(self):
        for n in range(len(self.t)):
            tn = self.t[n]
            yn = self.y[-1]
            h = self.h
            params = self.params
            guess = yn + h*(self.func(tn, yn, params))
            yfin = yn + 0.5*h*(self.func(tn, yn, params) + self.func(tn+h, guess, params))
            ynext = np.reshape(yfin, (1, self.l))
            self.y = np.concatenate((self.y, ynext), axis=0)

        return self.y

    def runge_kutta(self):
        for n in range(len(self.t)):
            tn = self.t[n]
            yn = self.y[-1]
            h = self.h
            params = self.params
            k1 = self.func(tn, yn, params)
            k2 = self.func(tn + 0.5*h, yn + 0.5*h*k1, params)
            k3 = self.func(tn + 0.5*h, yn + 0.5*h*k2, params)
            k4 = self.func(tn + h, yn + h*k3, params)
            ynext = np.reshape(yn + (h/6)*(k1 + 2*k2 + 2*k3 + k4), (1, self.l))
            self.y = np.concatenate((self.y, ynext), axis=0)

        return self.y

class PartDiffEq:
    def __init__(self, dt, dx, k, u):
        self.alp = k*dt/(dx)**2
        self.u = u

    def implicit_back(self):
        u = self.u
        for i in range(1, np.shape(u)[0]-1):
            for j in range(np.shape(u)[1]-1, 0, -1):
                u[i, j-1] = -self.alp * (u[i+1, j] + u[i-1, j]) + (1 + 2*self.alp)*u[i, j]
        return u

    def implicit(self):
        u = self.u
        A = np.zeros((np.shape(u)[0], np.shape(u)[0]))
        for i in range(np.shape(A)[0]):
            for j in range(np.shape(A)[1]):
                A[i,j] = -self.alp*((i+1)==j + (i-1)==j) + (1+2*self.alp)*(i==j)
        A[0, 0] = A[-1, -1] = 1
        m = MatInv()
        invA = m.inverse(A, m.gauss_siedel)

        for j in range(1, np.shape(u)[1]):
            print(u[:, j-1])
            u[:, j] = np.dot(invA, u[:, j-1])
        return u

    def explicit(self):
        u = self.u
        for j in range(np.shape(u)[1]-1):
            for i in range(1, np.shape(u)[0]-1):
                u[i, j+1] = self.alp*(u[i+1, j] + u[i-1, j]) + (1 - 2*self.alp)*u[i, j]
        return u

          
class Random:
    def __init__(self):
        import time
        self.seed = time.time()

    def mlcg(self, a=572, m=16381):
        self.seed = (a * self.seed) % m
        return self.seed / m

    def normal(self, center=0.0, sigma=1.0):
        u = [self.mlcg(), self.mlcg()]
        u1 = (np.sqrt(-2*np.log(u[0])))*np.cos(2*np.pi*u[0])
        u2 = (np.sqrt(-2*np.log(u[1])))*np.sin(2*np.pi*u[1])
        u = u2
        return sigma*u + center

    def walk(self, start):
        vec = np.zeros_like(start)
        vals = [-1, 1]
        num = self.mlcg()//(1/(2*np.shape(start)[0]))
        vec[int(num//2)] = vals[int(num%2)]
        return vec

class Integrate:
    def __init__(self, func):
        self.function = func
    
    def weights(self, numweights):
        if numweights == 1:
            return [[0, 2]]
        elif numweights == 2:
            return [[1/np.sqrt(3), 1], [-1/np.sqrt(3), -1]]
        elif numweights == 3:
            return [[0, 8/9], [np.sqrt(3/5), 5/9], [-np.sqrt(3/5), 5/9]]
        elif numweights == 4:
            return [[0.339981043, 0.652145154], [-0.339981043, 0.652145154], [0.861136311, 0.347854845], [-0.861136311, 0.347854845]] 
        elif numweights == 5:
            return [[0, 0.568888889], [0.53846931, 0.478628670], [-0.53846931, 0.478628670], [0.906179845, 0.236926885], [0.906179845, 0.236926885]] 
        elif numweights == 6:
            return [[0.932469514, 0.171324492], [0.661209386, 0.360761573], [0.238619186, 0.467913934], [-0.932469514, 0.171324492], [-0.661209386, 0.360761573], [-0.238619186, 0.467913934]]
    
    def gaussian_quadrature(self, lims: tuple, numweights):
        a, b = lims
        weights = np.array(self.weights(numweights))
        x = np.squeeze(weights[:, 0])
        w = np.squeeze(weights[:, 1])
        vals = np.array(list(map(self.function, 0.5*(b-a)*x+0.5*(a+b))))
        return 0.5*(b-a)*np.sum(np.dot(w, vals))

    def monte_carlo(self, lims: tuple, iter, importance=None):
        a, b = lims
        integ = np.array([])
        r = Random()
        for i in range(iter):
            random = r.mlcg()*(np.abs(b-a)) + np.min(lims)
            integ = np.append(integ, random)
        if importance:
            integ = np.abs(b-a)*(np.array(list(map(self.function, integ))))/(np.array(list(map(importance, integ))))
        else:
            integ = np.abs(b-a)*(np.array(list(map(self.function, integ))))
        return np.average(integ)

# class BVP:
#     def __init__(self, function, t, boundaries, paramlist, tol=1e-4):
#         self.func = function
#         self.h = t[1] - t[0]
#         self.t = t
#         self.params = paramlist
#         self.bounds = np.array(boundaries)
#         self.tol = tol

#     def shooting(self):
#         x1 = self.bounds[0,0]
#         y1 = self.bounds[0,1]
#         x2 = self.bounds[1,0]
#         y2 = self.bounds[1,1]
#         diff = 100
#         guess_energy = (y2-y1)/(x2-x1)

#         d = DiffEq(function, self.t, [0.0, 0.0], self.params)
#         while diff > self.tol:
#             d.y = np.reshape(np.array([y1, guess_slope]), (1, d.l))
#             y = d.runge_kutta()
#             y_gen1 = y[-1, 0]
#             d.y = np.reshape(np.array([y1, guess_slope]), (1, d.l))
#             y = d.runge_kutta()
#             y_gen2 = y[-1, 0]
#         return None