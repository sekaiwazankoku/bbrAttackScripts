import math
from tkinter import font
from turtle import color
import matplotlib
from matplotlib.pyplot import box
import numpy as np

from pubplot import Document
from plot_config.figure_type_creator import FigureTypeCreator as FTC

import os
import sys

script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))

ftc = FTC(paper_use_small_font=True, use_markers=False)
doc: Document = ftc.get_figure_type()

ppt: Document = FTC(pub_type='presentation', use_markers=False).get_figure_type()

minclambda = 1
D = 1
T = 1


def network_model():
    fig, ax = doc.subfigures(xscale=1/3, yscale=1/3)

    xx = np.linspace(0, 5, 100)
    yy1 = xx*1.4
    yy2 = yy1 - 2.7*D
    ax.plot(xx, yy1, color='k', linestyle='-')
    ax.plot(xx, yy2, color='k', linestyle='-')
    ax.fill_between(xx, yy1, yy2, color='red', alpha=0.2)

    ax.set_ylabel('Bytes')
    ax.set_xlabel('Time')

    ax.grid(False)
    ax.set_xlim(0, 4.5)
    ax.set_ylim(0, 4.5)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.xaxis.labelpad = 0
    ax.yaxis.labelpad = 0
    ax.plot(4.5, 0, ">k", clip_on=False)
    ax.plot(0, 4.5, "^k", clip_on=False)
    ax.spines[["top", "right"]].set_visible(False)

    ax.annotate("$\mathit{S}(t)$", (1.8, 1.8))

    fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
    fig.savefig(os.path.join(script_directory, "./network-model.svg"))


# def observations():
#     fig, ax = ppt.subfigures(xscale=1/3, yscale=1/3)
#     # ax.fill_between(xx, yy1, yy2, color='red', alpha=0.2)

#     da = np.array([10, 12, 10, 12])
#     dt = np.array([1, 2, 1, 2])
#     ax.plot(dt.cumsum(), 5 + da.cumsum(), label='Send')

#     ds = np.array([0, 10, 0, 10, 20, 0, 10])
#     dt = np.array([1, 0.2, 1, 0.2, 2, 0.2, 1])

#     ax.plot(dt.cumsum(), ds.cumsum(), label='Recv', ls='--')

#     import ipdb; ipdb.set_trace()

#     ax.set_ylabel('Sequence')
#     ax.set_xlabel('Time')

#     ax.grid(False)
#     # ax.set_xlim(0, 4.5)
#     # ax.set_ylim(0, 4.5)
#     ax.set_xticks([])
#     ax.set_yticks([])

#     ax.xaxis.labelpad = 0
#     ax.yaxis.labelpad = 0
#     ax.plot(4.5, 0, ">k", clip_on=False)
#     ax.plot(0, 4.5, "^k", clip_on=False)
#     ax.spines[["top", "right"]].set_visible(False)

#     ax.legend()

#     fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
#     fig.savefig(os.path.join(script_directory, "./observations.svg"))


def belief_inversion():
    fig, [ax2, ax3, ax1] = doc.subfigures(1, 3)

    minclambda = 1
    maxclambda = 2.5
    D = 1
    T = 1

    # First plot
    xx = np.linspace(0, 5, 100)
    yy1 = minclambda + 0*xx
    ax1.plot(xx, yy1, color='k', linestyle='-')

    yy2 = -1/T * xx + minclambda * (T+D)/T
    ax1.plot(xx, yy2, color='k', linestyle='-')

    yy_lo = np.maximum(yy1, yy2)
    yy_hi = xx * 0 + 3
    ax1.fill_between(xx, yy_lo, yy_hi, color='blue', alpha=0.2, edgecolor='white')

    ax1.set_xlim(0, 4.5)
    ax1.set_ylim(0.5, 3)
    ax1.set_xlabel("$\\beta$")
    ax1.set_ylabel("$\mathit{C}$")
    ax1.grid(False)
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.annotate("Belief set", (1.3, 1.8))

    # Second plot
    yy1 = 2 + 0*xx
    ax2.plot(xx, yy1, color='k', linestyle='-')

    yy_lo = 0 * xx
    yy_hi = yy1
    ax2.fill_between(xx, yy_lo, yy_hi, color='blue', alpha=0.2)

    ax2.set_xlim(0, 4.5)
    ax2.set_ylim(0.5, 3)
    ax2.set_xlabel("$\\beta$")
    ax2.set_ylabel("$\mathit{C}$")
    ax2.grid(False)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.annotate("$qdel>\mathit{D}$", (1.3, 2.5))

    # Second plot
    yy1 = -1/T * xx + maxclambda/T
    ax3.plot(xx, yy1, color='k', linestyle='-')

    yy_lo = 0 * xx
    yy_hi = yy1
    ax3.fill_between(xx, yy_lo, yy_hi, color='blue', alpha=0.2)

    ax3.set_xlim(0, 4.5)
    ax3.set_ylim(0.5, 3)
    ax3.set_xlabel("$\\beta$")
    ax3.set_ylabel("$\mathit{C}$")
    ax3.grid(False)
    ax3.set_xticks([])
    ax3.set_yticks([])
    ax3.annotate("Loss", (1.8, 2.5))

    for ax in [ax1, ax2, ax3]:
        ax.xaxis.labelpad = 0
        ax.yaxis.labelpad = 0

        # for direction in ['left', 'bottom']:
        #     ax.axis[direction].set_axisline_style("-|>")
        # for direction in ['right', 'top']:
        #     ax.axis[direction].set_visible(False)

        ax.plot(4.5, 0.5, ">k", clip_on=False)
        ax.plot(0, 3, "^k", clip_on=False)
        ax.spines[["top", "right"]].set_visible(False)

    fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
    fig.savefig(os.path.join(script_directory, "./inversion.svg"))


def cbr_delay_beliefs_2plots():

    fig, [ax, ax2] = doc.subfigures(1, 2, xscale=1, yscale=1)

    # First plot
    xx = np.linspace(0, 5, 100)
    yy1 = minclambda + 0*xx
    ax.plot(xx, yy1, color='k', linestyle='-')

    yy2 = -1/T * xx + minclambda * (T+D)/T
    ax.plot(xx, yy2, color='k', linestyle='-')

    yy_lo = np.maximum(yy1, yy2)
    yy_hi = xx * 0 + 3
    ax.fill_between(xx, yy_lo, yy_hi, color='blue', alpha=0.2, edgecolor='white')

    ax.set_xlim(0, 4.5)
    ax.set_ylim(0.5, 3)
    ax.set_xlabel("$\\beta$")
    ax.set_ylabel("$\mathit{C}$")
    ax.grid(False)
    # ax.set_xticks([minclambda*D])
    # ax.set_yticks([minclambda, minclambda * (T+D)/T])
    # ax.set_yticklabels(["$\mathit{C}_{L, \lambda}$", "$\mathit{C}_{L, \lambda}\\frac{\mathit{T}+\mathit{D}}{\mathit{T}}$"])
    # ax.set_xticklabels(["$\mathit{C}_{L, \lambda}\mathit{D}$"])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.annotate("Belief set", (2.8, 2.2))

    ax.minorticks_off()

    ax.xaxis.labelpad = 0
    ax.yaxis.labelpad = 0

    ax.plot(4.5, 0.5, ">k", clip_on=False)
    ax.plot(0, 3, "^k", clip_on=False)
    ax.spines[["top", "right"]].set_visible(False)

    ax.plot(D*minclambda, minclambda, "ok", clip_on=False)
    ax.annotate("$(\mathit{C}_{L, \lambda}\mathit{D}, \mathit{C}_{L, \lambda})$",
                (D * minclambda+0.3, minclambda-0.3))

    ax.plot(0, minclambda*(T+D)/T, "ok", clip_on=False)
    ax.annotate(
        "$\\left(0, \mathit{C}_{L, \lambda}\\frac{\mathit{T^*}+\mathit{D}}{\mathit{T^*}}\\right)$",
        (0.1, minclambda * (T+D)/T))

    ax.annotate("$\\text{slope}=\\frac{-1}{\mathit{T^*}}$", xy=(minclambda * D / 2, minclambda * (2*T+D)/(2*T)),
                xytext=(D * minclambda+0.2, minclambda * (2*T+D)/(2*T)), arrowprops=dict(arrowstyle="<-"))

    ax2.set_xlim(0, 4.5)
    ax2.set_ylim(0.5, 3)
    ax2.set_xlabel("$\\beta$")
    ax2.set_ylabel("$\mathit{C}$")

    ax2.set_xticks([])
    ax2.set_yticks([])

    ax2.minorticks_off()

    ax2.xaxis.labelpad = 0
    ax2.yaxis.labelpad = 0

    xx = np.linspace(0, 5, 100)
    yy1 = minclambda + 0*xx
    ax2.plot(xx, yy1, color='k', linestyle='-')

    yy2 = -1/T * xx + minclambda * (T+D)/T
    ax2.plot(xx, yy2, color='k', linestyle='-')

    yy_lo = np.maximum(yy1, yy2)
    yy_hi = xx * 0 + 3
    ax2.fill_between(xx, yy_lo, yy_hi, color='blue', alpha=0.2, edgecolor='white')

    ax2.plot(4.5, 0.5, ">k", clip_on=False)
    ax2.plot(0, 3, "^k", clip_on=False)

    ax2.spines["right"].set_visible(False)

    ax2.annotate("$L_1$", (3.8, minclambda+0.1))
    ax2.annotate("$L_2$", (minclambda * D / 2-0.5, minclambda * (2*T+D)/(2*T)-0.1))

    with matplotlib.rc_context(doc.style):
        ax3 = ax2.twiny()
        ax3.set_xlabel("$q_B = C_{L, \\lambda} \\cdotp (T+D) + \\alpha - CT$", color=ftc.colors[0])
        ax3.set_xticks([])
        ax3.xaxis.labelpad = 0
        ax3.set_xlim(0, 4.5)
        ax3.set_ylim(0.5, 3)

        alpha = minclambda/3

        yy2 = -1/T * xx + minclambda * (T+D)/T + alpha/T
        ax3.plot(xx, yy2, linestyle='-', label='Prb 1 $(T=T^*)$', zorder=1)

        ax3.plot(4.5, 3, ">", clip_on=False, color=ftc.colors[0])

        T2 = T/2
        yy2 = -1/T2 * xx + minclambda * (T2+D)/T2 + alpha/T2
        ax3.plot(xx, yy2, color=ftc.colors[0], linestyle='--', label='Prb 2 $(T < T^*)$', zorder=1)
        ax3.spines['top'].set_color(ftc.colors[0])
        ax3.spines['right'].set_visible(False)
        l = ax3.legend()
        l.set_frame_on(False)

    Ym = minclambda * (T+D)/T
    Xm = minclambda * (T2 + D) + alpha - Ym * T2
    xx = np.linspace(0, Xm, 100)
    yy = xx * 0 + Ym
    ax2.plot(xx, yy, color=ftc.colors[2], linestyle='-', zorder=10)
    ax2.annotate("$q_B-\\beta$", xy=(Xm/2, Ym), xytext=(2.2, Ym/1.5),
                arrowprops=dict(
                    arrowstyle="<-",
                    color=ftc.colors[2],
                    connectionstyle="arc3,rad=-0.3"), color=ftc.colors[2], zorder=10)

    fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
    fig.savefig(os.path.join(script_directory, "./cbr_delay_beliefs-probe.pdf"))
                # bbox_inches='tight', pad_inches=0.01)


def cbr_delay_beliefs():

    # fig, ax = ppt.subfigures(1, 1, xscale=0.3, yscale=0.3)
    fig, ax = ppt.subfigures(1, 1, xscale=0.3, yscale=0.3)

    # First plot
    xx = np.linspace(0, 5, 100)
    yy1 = minclambda + 0*xx
    ax.plot(xx, yy1, color='k', linestyle='-')

    yy2 = -1/T * xx + minclambda * (T+D)/T
    ax.plot(xx, yy2, color='k', linestyle='-')

    yy_lo = np.maximum(yy1, yy2)
    yy_hi = xx * 0 + 3
    ax.fill_between(xx, yy_lo, yy_hi, color='blue', alpha=0.2, edgecolor='white')

    ax.set_xlim(0, 4.5)
    ax.set_ylim(0.5, 3)
    # ax.set_xlabel("$\\beta$")
    ax.set_xlabel("$\mathit{B}$")
    ax.set_ylabel("$\mathit{C}$")
    ax.grid(False)
    # ax.set_xticks([minclambda*D])
    # ax.set_yticks([minclambda, minclambda * (T+D)/T])
    # ax.set_yticklabels(["$\mathit{C}_{L, \lambda}$", "$\mathit{C}_{L, \lambda}\\frac{\mathit{T}+\mathit{D}}{\mathit{T}}$"])
    # ax.set_xticklabels(["$\mathit{C}_{L, \lambda}\mathit{D}$"])
    ax.set_xticks([])
    ax.set_yticks([])
    # ax.annotate("Belief set", (2.8, 2.2))

    ax.minorticks_off()

    ax.xaxis.labelpad = 5
    ax.yaxis.labelpad = 2

    ax.plot(4.5, 0.5, ">k", clip_on=False)
    ax.plot(0, 3, "^k", clip_on=False)
    ax.spines[["top", "right"]].set_visible(False)

    # ax.plot(D*minclambda, minclambda, "ok", clip_on=False)
    # ax.annotate("$(\mathit{C}_{L, \lambda}\mathit{D}, \mathit{C}_{L, \lambda})$",
    #             (D * minclambda+0.3, minclambda-0.3))

    # ax.plot(0, minclambda*(T+D)/T, "ok", clip_on=False)
    # ax.annotate(
    #     "$\\left(0, \mathit{C}_{L, \lambda}\\frac{\mathit{T^*}+\mathit{D}}{\mathit{T^*}}\\right)$",
    #     (0.1, minclambda * (T+D)/T))

    # ax.annotate("$\\text{slope}=\\frac{-1}{\mathit{T^*}}$", xy=(minclambda * D / 2, minclambda * (2*T+D)/(2*T)),
    #             xytext=(D * minclambda+0.2, minclambda * (2*T+D)/(2*T)), arrowprops=dict(arrowstyle="<-"))

    fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
    fig.savefig(os.path.join(script_directory, "./cbr_delay_beliefs-ppt.svg"))
                # bbox_inches='tight', pad_inches=0.01)


def cbr_delay_beliefs2():

    # fig, ax = ppt.subfigures(1, 1, xscale=0.3, yscale=0.3)
    fig, ax = ppt.subfigures(1, 1, xscale=0.4, yscale=0.4)

    xx = np.linspace(0, 5, 100)
    yy2 = -1/T * xx + minclambda * (T+D)/T
    ax.plot(xx, yy2, color='k', linestyle='-')

    yy3 = -1/T * xx + minclambda * (T+D)/T + 0.4
    ax.plot(xx, yy3, color=ftc.colors[2], linestyle='-')

    yy_lo = yy2
    yy_hi = xx * 0 + 3
    ax.fill_between(xx, yy_lo, yy_hi, color='blue', alpha=0.2, edgecolor='white')

    ax.set_xlim(0, 4.5)
    ax.set_ylim(0.5, 3)
    # ax.set_xlabel("$\\beta$")
    ax.set_xlabel("$\mathit{q}$")
    ax.set_ylabel("$\mathit{C}$")
    ax.grid(False)
    # ax.set_xticks([minclambda*D])
    # ax.set_yticks([minclambda, minclambda * (T+D)/T])
    # ax.set_yticklabels(["$\mathit{C}_{L, \lambda}$", "$\mathit{C}_{L, \lambda}\\frac{\mathit{T}+\mathit{D}}{\mathit{T}}$"])
    # ax.set_xticklabels(["$\mathit{C}_{L, \lambda}\mathit{D}$"])
    ax.set_xticks([])
    ax.set_yticks([])
    # ax.annotate("Belief set", (2.8, 2.2))

    ax.minorticks_off()

    ax.xaxis.labelpad = 5
    ax.yaxis.labelpad = 2

    ax.plot(4.5, 0.5, ">k", clip_on=False)
    ax.plot(0, 3, "^k", clip_on=False)
    ax.spines[["top", "right"]].set_visible(False)

    # ax.plot(D*minclambda, minclambda, "ok", clip_on=False)
    # ax.annotate("$(\mathit{C}_{L, \lambda}\mathit{D}, \mathit{C}_{L, \lambda})$",
    #             (D * minclambda+0.3, minclambda-0.3))

    # ax.plot(0, minclambda*(T+D)/T, "ok", clip_on=False)
    # ax.annotate(
    #     "$\\left(0, \mathit{C}_{L, \lambda}\\frac{\mathit{T^*}+\mathit{D}}{\mathit{T^*}}\\right)$",
    #     (0.1, minclambda * (T+D)/T))

    # ax.annotate("$\\text{slope}=\\frac{-1}{\mathit{T^*}}$", xy=(minclambda * D / 2, minclambda * (2*T+D)/(2*T)),
    #             xytext=(D * minclambda+0.2, minclambda * (2*T+D)/(2*T)), arrowprops=dict(arrowstyle="<-"))

    fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
    fig.savefig(os.path.join(script_directory, "./cbr_delay_beliefs-ppt4.svg"))
                # bbox_inches='tight', pad_inches=0.01)


def beliefs_narrow():

    # fig, ax = ppt.subfigures(1, 1, xscale=0.3, yscale=0.3)
    fig, ax = ppt.subfigures(1, 1, xscale=0.3, yscale=0.3)

    # First plot
    xx = np.linspace(0, 5, 100)
    yy1 = minclambda + 0*xx
    ax.plot(xx, yy1, color='k', linestyle='-')

    yy2 = -1/T * xx + minclambda * (T+D)/T + 0.6
    ax.plot(xx, yy2, color='k', linestyle='-')

    T2 = T + 0.5
    yy3 = -1/T2 * xx + minclambda * (T+D)/T + 0.8
    ax.plot(xx, yy3, color='k', linestyle='-')

    yy_lo = np.maximum(yy1, yy2)
    yy_hi = yy3
    end = (minclambda * (T+D)/T + 0.8 - minclambda) * T2
    ax.fill_between(xx, yy_lo, yy_hi, where=xx<=end, color='blue', alpha=0.2, edgecolor='white')

    ax.set_xlim(0, 4.5)
    ax.set_ylim(0.5, 3)
    # ax.set_xlabel("$\\beta$")
    ax.set_xlabel("$\mathit{B}$")
    ax.set_ylabel("$\mathit{C}$")
    ax.grid(False)
    # ax.set_xticks([minclambda*D])
    # ax.set_yticks([minclambda, minclambda * (T+D)/T])
    # ax.set_yticklabels(["$\mathit{C}_{L, \lambda}$", "$\mathit{C}_{L, \lambda}\\frac{\mathit{T}+\mathit{D}}{\mathit{T}}$"])
    # ax.set_xticklabels(["$\mathit{C}_{L, \lambda}\mathit{D}$"])
    ax.set_xticks([])
    ax.set_yticks([])
    # ax.annotate("Belief set", (2.8, 2.2))

    ax.minorticks_off()

    ax.xaxis.labelpad = 5
    ax.yaxis.labelpad = 2

    ax.plot(4.5, 0.5, ">k", clip_on=False)
    ax.plot(0, 3, "^k", clip_on=False)
    ax.spines[["top", "right"]].set_visible(False)

    # ax.plot(D*minclambda, minclambda, "ok", clip_on=False)
    # ax.annotate("$(\mathit{C}_{L, \lambda}\mathit{D}, \mathit{C}_{L, \lambda})$",
    #             (D * minclambda+0.3, minclambda-0.3))

    # ax.plot(0, minclambda*(T+D)/T, "ok", clip_on=False)
    # ax.annotate(
    #     "$\\left(0, \mathit{C}_{L, \lambda}\\frac{\mathit{T^*}+\mathit{D}}{\mathit{T^*}}\\right)$",
    #     (0.1, minclambda * (T+D)/T))

    # ax.annotate("$\\text{slope}=\\frac{-1}{\mathit{T^*}}$", xy=(minclambda * D / 2, minclambda * (2*T+D)/(2*T)),
    #             xytext=(D * minclambda+0.2, minclambda * (2*T+D)/(2*T)), arrowprops=dict(arrowstyle="<-"))

    fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
    fig.savefig(os.path.join(script_directory, "./beliefs_narrow.svg"))
                # bbox_inches='tight', pad_inches=0.01)



def empty_axes():
    fig, ax = doc.subfigures(xscale=0.6, yscale=0.35)

    ax.set_xlim(0, 4.5)
    ax.set_ylim(0.5, 3)
    ax.set_xlabel("$\\beta$", loc='right')
    ax.set_ylabel("$\mathit{C}$")
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.xaxis.labelpad = 0
    ax.xaxis.labelpad = -16

    ax.plot(4.5, 0.5, ">k", clip_on=False)
    ax.plot(0, 3, "^k", clip_on=False)
    ax.spines[["top", "right"]].set_visible(False)

    fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
    fig.savefig(os.path.join(script_directory, "./empty_axes.svg"))


def c_belief_comp_inversion():
    fig, [ax1, ax2] = doc.subfigures(1, 2)

    D = 1
    T = 2

    # First plot
    xx = np.linspace(0, 5, 100) # = C
    yy1 = xx * (T-D)/T
    yy2 = xx * (T+D)/T
    ax1.plot(xx, yy1, color='k', linestyle='-')
    ax1.plot(xx, yy2, color='k', linestyle='-')
    ax1.fill_between(xx, yy1, yy2, color='blue', alpha=0.2, edgecolor='white')

    r = 1.5
    C_L = r*T/(T+D)
    C_H = r*T/(T-D)
    xx = np.linspace(0, C_H, 100)
    yy = xx*0 + r
    ax1.plot(xx, yy, color='red', linestyle='--')

    yy = np.linspace(0, r, 100)
    ax1.plot(0*yy + C_L, yy, color='red', linestyle='--')
    ax1.plot(0*yy + C_H, yy, color='red', linestyle='--')

    ax1.set_xlim(0, 5)
    ax1.set_ylim(0, 5)
    ax1.set_xlabel("$\\mathit{C}$", loc='right')
    ax1.set_ylabel("$\\mathit{r}$")
    ax1.grid(False)
    ax1.set_xticks([C_L, C_H])
    ax1.set_xticklabels(["$\mathit{C}_L$", "$\mathit{C}_H$"], color='red')
    ax1.set_yticks([])
    ax1.annotate("$\\frac{\mathit{C}(\mathit{T}+\mathit{D})}{\mathit{T}}$", (1.5, 4))
    ax1.annotate("$\\frac{\mathit{C}(\mathit{T}-\mathit{D})}{\mathit{T}}$", (3.6, 1))
    # ax1.annotate("$\\lambda \\geq \\mathit{C}$", (0, 4), boxstyle="square,pad=0.3", color='blue')
    ax1.text(0.2, 4, '$\\lambda \\geq \\mathit{C}$', color='blue',
        bbox=dict(facecolor='none', edgecolor='blue', linewidth=0.5, pad=2), fontsize=doc.scriptsize)
    ax1.annotate("Feasible\nbehaviors", (3.4, 3.5), fontsize=doc.scriptsize)

    # xx = np.linspace(C_L, C_H, 100)
    # ax1.plot(xx, xx*0, color='red', linestyle='-')

    # Second plot
    lambda_ = 2
    xx = np.linspace(0, 5, 100) # = C
    yy1 = xx * 0 + lambda_ * (T-D)/T
    yy2 = xx * (T+D)/T
    ax2.plot(xx, yy1, color='k', linestyle='-')
    ax2.plot(xx, yy2, color='k', linestyle='-')

    xx = np.linspace(lambda_*(T-D)/(T+D), 5, 100)
    yy1 = xx * 0 + lambda_ * (T-D)/T
    yy2 = xx * (T+D)/T
    ax2.fill_between(xx, yy1, yy2, color='blue', alpha=0.2, edgecolor='white')

    r = 3
    C_L = r*T/(T+D)
    # C_H = r*T/(T-D)
    xx = np.linspace(0, 5, 100) # = C
    yy = xx*0 + r
    ax2.plot(xx, yy, color='red', linestyle='--')

    yy = np.linspace(0, r, 100)
    ax2.plot(0*yy + C_L, yy, color='red', linestyle='--')

    ax2.set_xlim(0, 5)
    ax2.set_ylim(0, 5)
    ax2.set_xlabel("$\\mathit{C}$", loc='right')
    ax2.set_ylabel("$\\mathit{r}$")
    ax2.grid(False)
    ax2.set_xticks([C_L])
    ax2.set_xticklabels(["$\mathit{C}_L$"], color='red')
    ax2.annotate("$\mathit{C}_H=\\infty$", (3.2, r+0.3), color='red', fontsize=doc.scriptsize)
    ax2.set_yticks([])
    ax2.annotate("$\\frac{\mathit{C}(\mathit{T}+\mathit{D})}{\mathit{T}}$", (1.5, 4))
    ax2.annotate("$\\frac{\lambda(\mathit{T}-\mathit{D})}{\mathit{T}}$", (3.6, 1.4))
    # ax2.annotate("$\\lambda \\geq \\mathit{C}$", (0, 4), boxstyle="square,pad=0.3", color='blue')
    ax2.text(0.2, 4, '$\\lambda < \\mathit{C}$', color='blue',
        bbox=dict(facecolor='none', edgecolor='blue', linewidth=0.5, pad=2), fontsize=doc.scriptsize)

    for ax in [ax1, ax2]:
        ax.xaxis.labelpad = -5
        ax.yaxis.labelpad = 0
        ax.minorticks_off()

        ax.plot(5, 0, ">k", clip_on=False)
        ax.plot(0, 5, "^k", clip_on=False)
        ax.spines[["top", "right"]].set_visible(False)

    fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
    fig.savefig(os.path.join(script_directory, "c_belief_comp_inversion.pdf"))


def r_bounds_derivation():
    fig, ax = doc.subfigures(1, 1)

    N = 4
    D = 1
    C = 1

    xx = np.linspace(0, 5, 100) # = C
    yy1 = C * xx
    yy2 = C * (xx - D)
    ax.plot(xx, yy1, color='k', linestyle='-', label="_nolegend_")
    ax.plot(xx, yy2, color='k', linestyle='-', label="_nolegend_")
    ax.fill_between(xx, yy1, yy2, color='blue', alpha=0.2, edgecolor='white', label="_nolegend_")

    n_lines = 3
    lines = []
    for l in range(1, n_lines+1):
        # min slope
        st = 0
        en = l*D
        xx = np.linspace(st, en, 100)
        yy = (l-1) * C * xx / l
        inset = f"$T={l}D, "
        num = str(l-1)
        den = str(l)
        line = ax.plot(xx, yy, label=inset + "r_{L} = \\frac{" + num + "C}{" + den + "}$")
        lines.append(line)

        st = D
        en = (l+1)*D
        xx = np.linspace(st, en, 100)
        yy = (l+1)*C*D/l * (xx - D)
        num = str(l+1)
        den = str(l)
        line = ax.plot(xx, yy, label=inset + "r_{U} = \\frac{" + num + "C}{" + den + "}$")

    legend = ax.legend(borderpad=0.2) # , bbox_to_anchor=(1, 0), loc='lower right')

    ax.set_xlim(0, N)
    ax.set_ylim(-C*D, C * N)
    ax.set_xlabel("Time", loc='right')
    ax.set_ylabel("Bytes", loc='top')
    ax.set_xticks(range(0, N))
    ax.set_xticklabels([f"${x}D$" for x in range(0, N)])
    ax.set_yticks([C*x for x in range(0, N)])
    ax.set_yticklabels([f"${x}CD$" for x in range(0, N)])

    ax.annotate("$\\mathit{S_U}$", (2.6, 3))
    ax.annotate("$\\mathit{S_L}$", (3.5, 2.2))
    ax.annotate("Feasible\nbehaviors", (2.9, 3.5), fontsize=doc.scriptsize)

    ax.xaxis.labelpad = -5
    ax.yaxis.labelpad = 0
    ax.minorticks_off()

    ax.plot(N, -C*D, ">k", clip_on=False)
    ax.plot(0, C * N, "^k", clip_on=False)
    ax.spines[["top", "right"]].set_visible(False)

    # for k, spine in ax.spines.items():  #ax.spines is a dictionary
    #     spine.set_zorder(10)

    fig.set_tight_layout({'h_pad': 0, 'w_pad': 0.5, 'pad': 0})
    fig.savefig(os.path.join(script_directory, "r_bounds_derivation.pdf"))


if(__name__ == "__main__"):
    # observations()
    # network_model()
    # belief_inversion()
    cbr_delay_beliefs()
    cbr_delay_beliefs2()
    # empty_axes()
    # c_belief_comp_inversion()
    # r_bounds_derivation()
    beliefs_narrow()
