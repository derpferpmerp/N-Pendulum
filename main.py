import json
import random
import matplotlib.pyplot as plt
import numpy as np
from math import *
import PySimpleGUI as sg
from scipy import interpolate

sg.theme('DarkTeal12')

plt.style.use("dark_background")

GRAV = 9.81

NSEG = 10
ARMLEN = 2
XLIST = []
YLIST = []


def generateColor(bounds=None, amount=3, PLACES=2):
	if bounds is None:
		bounds = [0, 255]
	outlist = []
	for x in range(amount):
		outlist.append(random.randrange(bounds[0], bounds[1]))

	return tuple(list(map(lambda x: round(x / bounds[1], PLACES), outlist)))


def trySet(lst, ind, fval=0):
	try:
		i = lst[ind]
	except:
		return fval
	return lst[ind]


def smooth(mx, mn, xl, yl, c="blue"):
	x_new = np.linspace(mn, mx, 1000)
	a_BSpline = interpolate.make_interp_spline(xl, yl)
	y_new = a_BSpline(x_new)
	return x_new, y_new


def run(xl=None, al=None):
	if al is None:
		al = ARMLEN
	if xl is None:
		xl = XLIST
	OUT = []
	for k in range(1, len(xl)):
		p0 = GRAV

		kp1 = trySet(xl, k + 1)
		kp0 = trySet(xl, k)
		km1 = trySet(xl, k - 1)

		p21 = (NSEG - k)
		p221 = ((kp1 - kp0) / al)
		p222 = ((kp0 - km1) / al)
		p22 = p221 - p222
		p2 = p21 * p22

		p3 = ((kp0 - km1) / al)

		p1 = p2 - p3

		OUT.append(p0 * p1)
	return OUT


def graph(amt, NSEG=NSEG, ARMLEN=2):
	XLIST = []
	YLIST = []
	for x in range(NSEG):
		if not XLIST:
			gx = 0
			yc = ARMLEN * NSEG
			XLIST.append(gx)
			YLIST.append(yc)
		else:
			prev = XLIST[x - 1]
			genX = random.randrange(-ARMLEN, ARMLEN)
			yc = ((NSEG * ARMLEN) - (ARMLEN * x))
			XLIST.append(genX)
			YLIST.append(yc)
	OUT = [0] + run(xl=XLIST, al=ARMLEN)
	fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10))
	ax2.plot(XLIST, YLIST, color="red", label="Iteration 0")
	for x in range(NSEG):
		g = ARMLEN * x
		xlPLT2 = []
		ylPLT2 = []
		for h in np.linspace(min(XLIST), max(XLIST), 1000):
			xlPLT2.append(h)
			ylPLT2.append(g)
		ax2.plot(
			xlPLT2,
			ylPLT2,
			linestyle="dashed",
			alpha=0.4
		)
		OUT = max(XLIST) * (np.array(OUT) / max(OUT))
		ax2.plot(OUT, YLIST)

	dct = dict([(
		x,
		{
			"ITM": [],
			"CLR": generateColor()
		}) for x in range(amt)
	])
	labels = []
	for x in range(amt):
		rOut = [0] + run(xl=OUT)
		OUT = max(XLIST) * (np.array(rOut) / max(rOut))
		for g in range(NSEG - 1):
			try:
				dct[g]["ITM"].append(OUT[x])
			except:
				continue
		if x + 1 not in labels:
			ax2.plot(OUT, YLIST, color=generateColor(), label=f"Iteration {x + 1}")
			labels.append(x + 1)
	lk = list(dct.values())
	for v in lk:
		rx, ry = [[],[]]
		try: rx, ry = smooth(0, amt - 1, list(range(amt - 1)), v["ITM"][0:-1])
		except:
			rx, ry = [list(range(amt - 1)), v["ITM"][0:-1]]
			try:
				if lk.index(v) == len(lk) - 1:
					ax1.plot(
						rx,
						ry,
						color=v["CLR"],
						lw=3,
						alpha=0.8,
						label="Smoothed Line"
					)
					ax1.plot(
						list(range(amt - 1)),
						v["ITM"][0:-1],
						color=(220 / 255, 220 / 255, 220 / 255),
						lw=4,
						alpha=0.3,
						linestyle="dashed",
						label="Original Line"
					)
			except:
				try:
					sx, sy = smooth(0, amt - 1, list(range(amt)), lk[lk.index(v)-1]["ITM"])
					ax1.plot(
						sx,
						sy,
						color=v["CLR"],
						lw=3,
						alpha=0.8,
						label="Smoothed Line"
					)
				except:
					ax1.plot(
						list(range(amt)),
						lk[lk.index(v)-1]["ITM"],
						color=v["CLR"],
						lw=3,
						alpha=0.8,
						label="Smoothed Line"
					)
		try:
			ax1.scatter(
				list(range(amt - 1))[lk.index(v)],
				v["ITM"][0:-1][lk.index(v)],
				label=f"Step {lk.index(v)}",
				color=v["CLR"],
				alpha=1,
				zorder=2.5
			)
		except:
			continue

	ax1.legend()
	ax1.set_xlabel("$\\Delta{}\\tau$", fontsize=20, color="white")
	ax1.text(
		1 / 3,
		0.95,
		"$\\ddot{x_k}=g\\left[\\left(n-k\\"
		"right)\\left(\\frac{c_1-x_k}{a}-\\frac{"
		"x_k-x_{k-1}}{a}\\right)-\\frac{x_k-x_{k-1}}"
		"{a}\\right]$",
		transform=ax1.transAxes,
		fontsize=14,
		bbox=dict(
			boxstyle='round',
			facecolor='black',
			alpha=0.5
		),
		horizontalalignment="center"
	)
	ax1.set_ylabel("$dx$")
	ax2.legend()
	plt.show(block=False)


layout = [
	[
		sg.Text('Amount of Segments', size=(20, 1)),
		sg.Slider(
			(4, 50),
			10,
			1,
			orientation="h",
			size=(20, 15),
			key="-LINK SLIDER-",
			enable_events=True
		)
	],
	[
		sg.Text('Segment Length', size=(20, 1)),
		sg.Slider(
			(2, 100),
			5,
			1,
			orientation="h",
			size=(20, 15),
			key="-LENGTH SLIDER-",
			enable_events=True
		)
	],
	[
		sg.Text('Amount of Iterations', size=(20, 1)),
		sg.Slider(
			(1, 100),
			10,
			1,
			orientation="h",
			size=(20, 15),
			key="-ITER SLIDER-",
			enable_events=True
		)
	],
	[sg.Button("Generate Simulation")],
]
window = sg.Window(
	title="N-Pendulum-Simulator",
	layout=layout,
	margins=(100, 50)
)
currentbutton = None
hasclickedbutton = False
matplotlibWindowOpen = False

while True:
	event, values = window.read()
	if not matplotlibWindowOpen and event == sg.WIN_CLOSED:
		break
	elif event == "Generate Simulation":
		links, armlength, iterations = [values["-LINK SLIDER-"], values["-LENGTH SLIDER-"], values["-ITER SLIDER-"]]
		links = round(links)
		armlength = round(armlength)
		iterations = round(iterations)
		print(json.dumps(values,indent=4))
		graph(iterations, NSEG=links, ARMLEN=armlength)
		matplotlibWindowOpen = True
	elif matplotlibWindowOpen and event == sg.WIN_CLOSED:
		matplotlibWindowOpen = False

window.close()
