import numpy as np
from scipy import optimize

#0
def proportion(x,a):
	return a*x

#1
def func_c1(x,a,b):
	return a*x+b

#2
def func_c2(x,a,b,c):
	return a*x**2+b*x+c

#3
def func_c3(x,a,b,c,d):
	return a*x**3+b*x**2+c*x+d

#4
def func_c4(x,a,b,c,d,e):
	return a*x**4+b*x**3+c*x**2+d*x+e

#5
def func_tanh(x,a,b,c):
	return a*np.tanh(b*x+c)

#6
def func_gauss(x,a,mu,sigma):
	return a*np.exp(-(x-mu)**2/(2*sigma**2))

#7
def func_exp(x,a,b):
	return a*np.exp(x*b)

def el(p,x,y):
	a=p[0]
	b=p[1]
	if a == 0:
		return -np.inf
	r=np.log(y)-(np.log(a)+b*x)
	return r

#8
def func_log(x,a,b,c):
	return a*np.log(b*x)+c

func_list = {
	0:proportion,
	1:func_c1, 
	2:func_c2, 
	3:func_c3, 
	4:func_c4, 
	5:func_tanh,
	6:func_gauss,
	7:func_exp,
	8:func_log
}

def fit_func(xdata,ydata,x,f=-1):
	
	err=2**100
	if f== -1:
		for i in range(len(func_list)):
			popt,pocv=optimize.curve_fit(func_list[i],xdata,ydata, check_finite=False)

			errors = ydata-func_list[i](xdata,*popt)
			error = np.sum(errors**2)
			if err>error:
				err=error
				f=i
				opt=popt
	elif f == 7:
		p0=[1,1]
		opt,pcov=optimize.leastsq(el,p0,args=(xdata,ydata))
	else:
		opt,ocv=optimize.curve_fit(func_list[f],xdata,ydata, check_finite=False)
	return func_list[f](x,*opt)