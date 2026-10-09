#!/usr/bin/env python3
"""Draw the figures for the fabric linear-algebra pages.

Writes PNGs into docs/science/img/fabric-math/. Every number drawn here is
computed, not typed in, so the figures stay consistent with the worked
examples on the pages:

  science/fabric-linear-algebra.md     vector, projection, matrix-action
  science/fabric-eigenvalues.md        crystals
  science/fabric-inversion-eigenvalues.md  eigen-patterns, recovery

Needs numpy and matplotlib, which the site build does not:

    python3 -m venv /tmp/figs && /tmp/figs/bin/pip install numpy matplotlib
    /tmp/figs/bin/python tools/fabric_math_figures.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "docs/science/img/fabric-math"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": MUTED,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def arrow(ax, x, y, color, lw=2.0, alpha=1.0, z=3):
    ax.annotate("", xy=(x, y), xytext=(0, 0), zorder=z,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                alpha=alpha, shrinkA=0, shrinkB=0,
                                mutation_scale=14))


def plane(ax, lim):
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.grid(color=GRID, lw=0.8)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_xlabel("x (east)")
    ax.set_ylabel("y (north)")


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fn = OUT / name
    fig.savefig(fn, dpi=160, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", fn.relative_to(OUT.parent.parent.parent))


def fig_vector():
    """A vector and its components; a c-axis and its double-headed axis."""
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 4.3),
                               gridspec_kw={"wspace": 0.35})

    plane(a, 3)
    a.set_xlim(-0.5, 3.2)
    a.set_ylim(-0.5, 2.2)
    a.plot([0, 2], [0, 0], color=MUTED, lw=1.2, ls="--")
    a.plot([2, 2], [0, 1], color=MUTED, lw=1.2, ls="--")
    arrow(a, 2, 1, BLUE, lw=2.4)
    a.text(1.0, -0.22, "x-component = 2", ha="center", color=MUTED)
    a.text(2.08, 0.5, "y-component\n= 1", va="center", color=MUTED)
    a.text(0.75, 0.62, r"$\mathbf{v} = (2,\ 1)$", color=BLUE, fontsize=13)
    a.text(0.95, 1.55, r"length $= \sqrt{2^2 + 1^2} \approx 2.24$",
           ha="center", color=INK)
    a.set_title("A vector is an arrow written as two numbers", fontsize=11)

    plane(b, 1.3)
    t = np.deg2rad(30)
    c = np.array([np.cos(t), np.sin(t)])
    arrow(b, *c, BLUE, lw=2.4)
    arrow(b, *(-c), ORANGE, lw=2.4)
    b.text(c[0] + 0.05, c[1] + 0.05, r"$\mathbf{c}$", color=BLUE, fontsize=13)
    b.text(-c[0] - 0.22, -c[1] - 0.17, r"$-\mathbf{c}$", color=ORANGE,
           fontsize=13)
    b.text(0, -1.15, "same crystal: an axis has no head or tail",
           ha="center", color=MUTED)
    b.set_title("A c-axis points both ways", fontsize=11)
    save(fig, "vector.png")


def fig_projection():
    """Projection of a field onto an antenna direction (the dot product)."""
    fig, ax = plt.subplots(figsize=(5.2, 4.4))
    plane(ax, 1.3)
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(-0.3, 1.1)
    psi, phi = np.deg2rad(10), np.deg2rad(50)
    u = np.array([np.cos(psi), np.sin(psi)])
    e = 1.0 * np.array([np.cos(phi), np.sin(phi)])
    p = (e @ u) * u
    ax.plot([-0.25 * u[0], 1.25 * u[0]], [-0.25 * u[1], 1.25 * u[1]],
            color=MUTED, lw=1, ls=":")
    ax.plot([e[0], p[0]], [e[1], p[1]], color=MUTED, lw=1.2, ls="--")
    arrow(ax, *e, BLUE, lw=2.4)
    arrow(ax, *u, AQUA, lw=2.4, z=2)
    ax.plot([0, p[0]], [0, p[1]], color=ORANGE, lw=5, alpha=0.85,
            solid_capstyle="butt", zorder=4)
    ax.text(e[0] - 0.05, e[1] + 0.05, r"field $\mathbf{E}$", color=BLUE,
            ha="right", fontsize=12)
    ax.text(u[0] + 0.02, u[1] - 0.12, r"antenna $\mathbf{u}$", color=AQUA,
            fontsize=12)
    ax.text(p[0] * 0.55, p[1] * 0.55 - 0.16,
            r"$\mathbf{E}\cdot\mathbf{u} = \cos 40^\circ \approx 0.77$",
            color=INK, ha="center", fontsize=11)
    ax.set_title("The dot product: how much of E lies along u", fontsize=11)
    save(fig, "projection.png")


def fig_matrix_action():
    """A symmetric matrix acting on a ring of directions."""
    A = np.array([[2.0, 1.0], [1.0, 2.0]])
    angles = np.deg2rad(np.arange(0, 360, 15))
    eig = {45, 135, 225, 315}
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.8))
    for ax, title, mat in ((axs[0], r"before: unit vectors $\mathbf{v}$",
                            np.eye(2)),
                           (axs[1], r"after: $A\mathbf{v}$ with A = [[2, 1], [1, 2]]",
                            A)):
        plane(ax, 3.4)
        tt = np.linspace(0, 2 * np.pi, 200)
        ring = mat @ np.vstack([np.cos(tt), np.sin(tt)])
        ax.plot(*ring, color=GRID, lw=1.5, zorder=1)
        for t in angles:
            v = mat @ np.array([np.cos(t), np.sin(t)])
            deg = round(np.rad2deg(t)) % 360
            if deg in eig:
                col = ORANGE if deg in (45, 225) else AQUA
                arrow(ax, *v, col, lw=2.6, z=4)
            else:
                arrow(ax, *v, BLUE, lw=1.2, alpha=0.45)
        ax.set_title(title, fontsize=11)
    axs[1].text(2.25, 2.25, r"$\times 3$", color=ORANGE, fontsize=13,
                ha="left", va="bottom")
    axs[1].text(-1.0, 0.85, r"$\times 1$", color=AQUA, fontsize=13,
                ha="right")
    fig.text(0.5, -0.02,
             "Blue arrows change direction. The orange and green directions "
             "only stretch: they are the eigenvectors.",
             ha="center", color=MUTED)
    save(fig, "matrix-action.png")


def fig_crystals():
    """The four-crystal example and a larger sample, with their ellipses."""
    fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.8))
    rng = np.random.default_rng(3)
    samples = [
        (np.deg2rad([0, 30, 60, 90]), "four crystals (worked example)"),
        (np.deg2rad(30) + 0.45 * rng.standard_normal(300),
         "300 crystals clustered near 30°"),
    ]
    for ax, (ang, title) in zip(axs, samples):
        plane(ax, 1.25)
        for t in ang:
            c = np.array([np.cos(t), np.sin(t)])
            ax.plot([-c[0], c[0]], [-c[1], c[1]], color=BLUE,
                    lw=2.0 if len(ang) < 10 else 0.6,
                    alpha=1.0 if len(ang) < 10 else 0.25, zorder=2)
        C = np.vstack([np.cos(ang), np.sin(ang)])
        Ah = C @ C.T / len(ang)
        w, V = np.linalg.eigh(Ah)
        tt = np.linspace(0, 2 * np.pi, 200)
        ell = V @ np.diag(w) @ np.vstack([np.cos(tt), np.sin(tt)])
        ell = ell / w.max()
        ax.plot(*ell, color=INK, lw=1.4, zorder=3)
        for k, col in ((1, ORANGE), (0, AQUA)):
            v = V[:, k] * w[k] / w.max()
            if v[0] < 0:
                v = -v
            arrow(ax, *v, col, lw=2.6, z=5)
            y0 = 0.94 if k == 1 else 0.86
            ax.plot([0.04, 0.10], [y0, y0], color=col, lw=3,
                    transform=ax.transAxes, zorder=6)
            ax.text(0.12, y0, r"$\lambda = %.2f$" % w[k], color=INK,
                    fontsize=11, va="center", transform=ax.transAxes,
                    zorder=6, bbox=dict(fc=SURFACE, ec="none", pad=1))
        ax.set_title(title, fontsize=11)
    fig.text(0.5, -0.02,
             "Blue lines: horizontal c-axes. Arrows: eigenvectors of the "
             "averaged matrix, scaled by their eigenvalues.",
             ha="center", color=MUTED)
    save(fig, "crystals.png")


def toy_inversion():
    c, eps_p, deps = 0.299792458, 3.15, 0.034
    g = deps / (c * np.sqrt(eps_p))
    m, dz = 8, 100.0
    G = g * dz * np.tril(np.ones((m, m)))
    return G, m, dz


def fig_patterns():
    """Best- and worst-resolved depth patterns of the toy normal matrix."""
    G, m, dz = toy_inversion()
    w, V = np.linalg.eigh(G.T @ G)
    depth = (np.arange(m) + 0.5) * dz
    fig, axs = plt.subplots(1, 2, figsize=(8, 4.6), sharey=True)
    for ax, k, col, name in ((axs[0], -1, ORANGE, "best resolved"),
                             (axs[1], 0, AQUA, "worst resolved")):
        v = V[:, k] * np.sign(V[0, k])
        ax.barh(depth, v, height=dz * 0.8, color=col)
        ax.axvline(0, color=MUTED, lw=0.8)
        ax.set_xlim(-0.6, 0.6)
        ax.set_title("%s  (eigenvalue %.0f)" % (name, w[k]), fontsize=11)
        ax.set_xlabel(r"pattern of $\Delta\lambda$")
        ax.grid(axis="x", color=GRID, lw=0.8)
    axs[0].set_ylabel("depth of interval (m)")
    axs[0].invert_yaxis()
    save(fig, "eigen-patterns.png")


def fig_recovery():
    """True profile, plain least squares, and the regularized solve."""
    G, m, dz = toy_inversion()
    N = G.T @ G
    D = np.diff(np.eye(m), axis=0)
    alpha = 0.05 * np.trace(N) / m
    rng = np.random.default_rng(0)
    true = np.array([0.02, 0.02, 0.05, 0.10, 0.15, 0.15, 0.10, 0.08])
    d = G @ true + rng.normal(0, 0.3, m)
    plain = np.linalg.solve(N, G.T @ d)
    reg = np.linalg.solve(N + alpha * D.T @ D, G.T @ d)
    edges = np.arange(m + 1) * dz

    def step(x):
        return np.repeat(x, 2), np.repeat(edges, 2)[1:-1]

    fig, ax = plt.subplots(figsize=(5.2, 5.0))
    for x, col, lw, name in ((true, INK, 2.6, "true"),
                             (plain, ORANGE, 1.8, "plain least squares"),
                             (reg, BLUE, 1.8, "with smoothness penalty")):
        xs, zs = step(x)
        ax.plot(xs, zs, color=col, lw=lw, label=name)
    ax.invert_yaxis()
    ax.set_xlabel(r"$\Delta\lambda$")
    ax.set_ylabel("depth (m)")
    ax.grid(color=GRID, lw=0.8)
    ax.legend(frameon=False, loc="upper center", ncol=3, fontsize=9,
              bbox_to_anchor=(0.5, -0.13))
    ax.set_title("0.3 ns of noise on eight traveltime nodes", fontsize=11)
    save(fig, "recovery.png")


if __name__ == "__main__":
    fig_vector()
    fig_projection()
    fig_matrix_action()
    fig_crystals()
    fig_patterns()
    fig_recovery()
