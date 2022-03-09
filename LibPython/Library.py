"""
Author: Spandan Anupam
As part of the Computational Physics course at NISER
"""
# Calls numpy for basic array functionality. See julia code in ../LibJulia for a more fleshed out (mostly) dependency free code
import numpy as np
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
        if str(type(A)) == "<class 'LibPython.Library.UnloadedMatrix'>":
            func = A.dot
        else:
            func = np.dot
        x= np.ones((A.shape[0], ))
        d = np.copy(b - np.squeeze(func(A, x)))
        r = np.copy(b - np.squeeze(func(A, x)))
        con = 0
        res = []
        for i in range(A.shape[0]):
            Ad = func(A, d)
            modr = np.linalg.norm(r)
            α = modr / np.dot(d.T, Ad)
            x += α * d
            β = 1 / modr
            r -= α * (Ad)
            modr = np.linalg.norm(r)
            res.append(modr)
            if (modr < stop):
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

    def inverse(self, A, func):
        n = A.shape[0]
        amat = np.identity(n)
        for i in range(n):
            a = amat[:, i]
            amat[:, i] = func(A, a)
        return amat

class Eigen:
    def __init__(self):
        pass

    def power(self, A, stop=1e-3):
        """
        Power Method
        """
        x =  np.ones((A.shape[1], ))
        v = x 
        vold = np.zeros(np.shape(x))
        λold = 0.0; λ = -1.0
        while abs(λ - λold) > stop:
            vold = v; v = np.dot(A, v)
            λold = λ; λ = np.dot(v, x)/np.dot(vold, x)
        return λ, v / np.linalg.norm(v)

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

    def polyfit(self, x, y, yerr, n=2):
        """
        Polynomial Fitting
        """
        A = np.zeros(n+1, n+1)
        a = np.zeros(n)
        for i in range(n+1):
            for j in range(n+1):
                a[j] = sum((x**j * y) / yerr**2)
                A[i, j] = np.sum(x**(i+j) / yerr**2)
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
    def __init__(self, size, mu, m):
        self.size = size
        self.shape = (size, size)
        self.mu = mu
        self.m = m
        self.mul = 1
    
    def delta(self, i, j):
        return float(i==j)

    def __getitem__(self, idx):
        i = idx[0]
        j = idx[1]
        return self.mul*(0.5*(self.delta(i+self.mu, j) + self.delta(i-self.mu, j) - 2*self.delta(i, j)) + (self.m**2)*(self.delta(i, j)))

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

    def dot(self, A, other):
        assert(self.size == other.shape[0])
        dotval = np.zeros_like(other)
        for i in range(self.size):
            for j in range(self.size):
                dotval[i] += self.__getitem__((i, j)) * other[j]
        return dotval

    
