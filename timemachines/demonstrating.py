import matplotlib.pyplot as plt
import numpy as np
from timemachines.synthetic import brownian_with_exogenous, brownian_with_noise
from timemachines.iterative import prior


def prior_plot(f, ys=None, k=None, ats=None, ts=None, e=None, r=0.5, x0=np.nan, n=150, n_plot=25):
    if ys is None:
       ys = brownian_with_noise(n=n)

    if ts is None:
        ts = range(len(ys))

    xs = prior(f=f,ys=ys, k=k, ats=ats, ts=ts, e=e, r=r, x0=x0 )
    ysf = [ [y_] for y_ in ys ]
    exog_plot(ts=ts, xs=xs, ys=ysf, n_plot=n_plot)


def prior_plot_exogenous(f, ys=None, k=None, ats=None, ts=None, e=None, r=0.5, x0=np.nan, n=150, n_plot=25):
    if ys is None:
       ys = brownian_with_exogenous(n)

    if ts is None:
       ts = range(len(ys))

    xs = prior(f=f, ys=ys, k=k, ats=ats, ts=ts, e=e, r=r, x0=x0)
    exog_plot(ts=ts,xs=xs,ys=ys,n_plot=n_plot)


def exog_plot(ts,xs,ys,n_plot):
    try:
        ys0 = [y_[0] for y_ in ys]
    except:
        ys0 = ys
    plt.plot(ts[-n_plot:], ys0[-n_plot:], 'b*')
    lgnd = ['target']
    for j in range(1,len(ys[0])):
        ysj = [y_[j] for y_ in ys]
        plt.plot(ts[-n_plot:], ysj[-n_plot:], 'r+')
        lgnd.append('exogenous '+str(j))
    plt.pause(0.1)

    # Run the model
    plt.plot(ts[-n_plot:], xs[-n_plot:], 'g-')
    lgnd.append('prediction')
    plt.legend(lgnd)
    plt.show()


