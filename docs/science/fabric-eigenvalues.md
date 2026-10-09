# Eigenvalues and the horizontal fabric

The [fabric tutorial](fabric-polarimetry.md) ends with a profile of
$\Delta\lambda = \lambda_x - \lambda_y$ and, from quad-pol data, an axis
$\theta_0$. Both numbers come from the eigenvalues and eigenvectors of a
small symmetric matrix. This page explains what that matrix is and what its
eigenvalues and eigenvectors mean physically, and it shows why the
radar can see only part of it. It uses short Python and MATLAB snippets you can run
anywhere.

The page ends with a second matrix: the normal matrix that
`invertHorizontalFabricJoint` solves at every Gauss–Newton step. Its eigenvalues
tell you which depth patterns of $\Delta\lambda$ the data actually constrain.

No linear algebra beyond matrix multiplication is assumed.

## Eigenvalues in one paragraph

For a square matrix $A$, an **eigenvector** $\mathbf{v}$ is a direction that
$A$ only stretches and never turns:

$$A\mathbf{v} = \lambda\mathbf{v}$$

The stretch factor $\lambda$ is the **eigenvalue**. Every matrix on this page is
**real and symmetric** ($A = A^T$), which buys three guarantees:

1. the eigenvalues are real;
2. the eigenvectors are mutually perpendicular;
3. the matrix can be rebuilt from them as $A = R\,\Lambda\,R^T$, where $\Lambda$ is the diagonal matrix of eigenvalues and the
   columns of the rotation $R$ are the eigenvectors.

The third point is the important one. In the frame of its own eigenvectors a symmetric
matrix is diagonal, so it acts on each axis separately. Finding that frame is called
**diagonalizing** the matrix. For fabric, it means finding the directions the
crystals prefer and how strongly they prefer them.

Two identities are worth remembering, because they let you check answers
without computing anything:

$$\operatorname{tr}A = \sum_i \lambda_i \qquad\qquad \det A = \prod_i \lambda_i$$

## The orientation tensor

Each ice crystal has a symmetry axis, its **c-axis**, written as a unit
vector $\mathbf{c}$. A c-axis has no head or tail: $\mathbf{c}$ and
$-\mathbf{c}$ describe the same crystal. So we cannot simply average the
vectors, because they would cancel. Instead we average the outer product,
which is unchanged when the sign flips:

$$
\mathbf{a}^{(2)} = \langle \mathbf{c}\,\mathbf{c}^T \rangle =
\begin{bmatrix}
\langle c_x^2\rangle & \langle c_x c_y\rangle & \langle c_x c_z\rangle\\
\langle c_x c_y\rangle & \langle c_y^2\rangle & \langle c_y c_z\rangle\\
\langle c_x c_z\rangle & \langle c_y c_z\rangle & \langle c_z^2\rangle
\end{bmatrix}
$$

This is the **second-order orientation tensor**. It is symmetric by construction, and its
trace is $\langle c_x^2 + c_y^2 + c_z^2\rangle = 1$, so its three eigenvalues
always sum to one. The eigenvalues say how the c-axes are spread out. The
eigenvectors say which way.

| fabric | eigenvalues $(\lambda_1, \lambda_2, \lambda_3)$ | picture |
|---|---|---|
| isotropic | $(\tfrac13, \tfrac13, \tfrac13)$ | c-axes in every direction |
| single maximum | $(0, 0, 1)$ | all c-axes along one direction |
| girdle | $(\tfrac12, \tfrac12, 0)$ | c-axes spread evenly around a plane |

Real ice falls in between. The code calls the three eigenvalues
`lam = [lam_x lam_y lam_z]`, ordered by the principal axes $(x, y, z)$
rather than by size (`ptt.columnProfiles`).

## The horizontal block

A ground-based accumulation radar sends waves nearly straight down. The
electric field of a vertically travelling wave lies in the **horizontal**
plane, so the radar only sees the part of $\mathbf{a}^{(2)}$ that acts on
horizontal vectors.

The method assumes one eigenvector is vertical, which is a good assumption away
from steep bed topography. The tensor then splits into a $2\times2$
horizontal block and a single vertical eigenvalue:

$$
\mathbf{a}^{(2)} =
\begin{bmatrix}
A_h & \mathbf{0}\\
\mathbf{0}^T & \lambda_z
\end{bmatrix},
\qquad
A_h =
\begin{bmatrix}
a_{xx} & a_{xy}\\
a_{xy} & a_{yy}
\end{bmatrix}
$$

$A_h$ is the matrix this page is about. It holds three numbers, $a_{xx}$,
$a_{yy}$ and $a_{xy}$, and it is equivalent to its two eigenvalues
$\lambda_x \ge \lambda_y$ together with the azimuth $\theta$ of the
$\lambda_x$ eigenvector.

### Diagonalizing a 2×2 by hand

The eigenvalues are the roots of $\det(A_h - \lambda I) = 0$, which for a
$2\times2$ matrix is a quadratic:

$$
\lambda^2 - (a_{xx} + a_{yy})\,\lambda + (a_{xx}a_{yy} - a_{xy}^2) = 0
$$

Its roots are

$$
\lambda_{x,y} = \frac{h}{2} \pm \sqrt{\left(\frac{a_{xx}-a_{yy}}{2}\right)^2 + a_{xy}^2},
\qquad h = a_{xx} + a_{yy} = 1 - \lambda_z
$$

so the **difference** of the eigenvalues, the quantity the fabric chain
inverts for, is

$$
\boxed{\Delta\lambda = \lambda_x - \lambda_y = \sqrt{(a_{xx}-a_{yy})^2 + 4a_{xy}^2}}
$$

The eigenvector azimuth comes from the same two combinations:

$$
\boxed{\tan 2\theta = \frac{2a_{xy}}{a_{xx} - a_{yy}}}
$$

Notice the **$2\theta$**. Turning an axis by 180° gives the same axis, so the
matrix can only depend on the doubled angle. Putting the two results together
gives the cleanest way to write $A_h$:

$$
A_h = \frac{h}{2}\,I + \frac{\Delta\lambda}{2}
\begin{bmatrix}
\cos 2\theta & \sin 2\theta\\
\sin 2\theta & -\cos 2\theta
\end{bmatrix}
$$

Read it term by term:

- $\tfrac{h}{2} I$ is the **isotropic part**. It looks the same in every
  horizontal direction, so a radar comparing two polarizations cannot see
  it. This is why $\lambda_z$ (and therefore $h$) has to be *assumed* in the
  common-offset inversion: the data constrain only the second term.
- $\tfrac{\Delta\lambda}{2}[\dots]$ is the **anisotropic part**: the strength
  $\Delta\lambda$ and the direction $\theta$. These are the two things the
  radar measures.

This explains how `invertHorizontalFabricJoint` builds its column. Given an
assumed $\lambda_z$ and a trial $\Delta\lambda$, it sets
`lam_x = (h + dlam)/2` with `h = 1 - lam_z`. It also clips $|\Delta\lambda| < h$,
because $\lambda_y = (h-\Delta\lambda)/2$ cannot go negative. That clip is the
"eigenvalue bound" reported in `out.clipped`.

!!! note "Why the code never unwraps an axis angle"
    $\theta$ and $\theta + 180°$ are the same axis, which is why every formula
    above uses $2\theta$. Averaging or interpolating raw angles across the
    0/180 wrap gives nonsense: the mean of 1° and 179° is 90°, which is
    perpendicular to both. The fix used throughout `+ptt` (`axisFold`,
    `thetaProfileAt`) is to work with the **doubled-angle phasor**
    $e^{2i\theta}$, average that, and halve its angle at the end. The
    [troubleshooting habits](fabric-polarimetry.md#trouble-shooting-habits)
    rule "never unwrap axis angles" comes from this.

### Try it

Build $A_h$ from known eigenvalues and an axis, then take it apart again.

=== "Python"

    ```python
    import numpy as np

    lam_z = 0.40                     # assumed vertical eigenvalue
    h     = 1 - lam_z                # left for the horizontal plane
    dlam  = 0.12                     # lam_x - lam_y
    theta = np.deg2rad(30)           # azimuth of the lam_x eigenvector

    lam_x, lam_y = (h + dlam)/2, (h - dlam)/2
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta),  np.cos(theta)]])
    A = R @ np.diag([lam_x, lam_y]) @ R.T     # A = R Lambda R^T

    w, V = np.linalg.eigh(A)         # eigh: for symmetric matrices
    v = V[:, -1]                     # eigenvector of the largest eigenvalue
    print(A)
    print(w, np.rad2deg(np.arctan2(v[1], v[0])) % 180)
    ```

=== "MATLAB"

    ```matlab
    lam_z = 0.40;  h = 1 - lam_z;
    dlam  = 0.12;  theta = deg2rad(30);

    lam_x = (h + dlam)/2;  lam_y = (h - dlam)/2;
    R = [cos(theta) -sin(theta); sin(theta) cos(theta)];
    A = R * diag([lam_x lam_y]) * R';

    [V, L] = eig(A);                 % symmetric input: L ascending
    v = V(:, end);
    disp(A)
    disp(diag(L)')
    disp(mod(rad2deg(atan2(v(2), v(1))), 180))
    ```

Output:

```
[[0.33  0.052]
 [0.052 0.27 ]]
[0.24 0.36] 30.0
```

Check it with the identities: $\operatorname{tr}A_h = 0.33 + 0.27 = 0.60 = h$, and
$\det A_h = 0.33 \cdot 0.27 - 0.052^2 = 0.0864 = 0.24 \cdot 0.36$. The closed
forms give $\Delta\lambda = \sqrt{0.06^2 + 4\cdot0.052^2} = 0.12$ and
$\tfrac12\operatorname{atan2}(0.104, 0.06) = 30°$, with no `eig` call needed.

!!! tip "The sign of an eigenvector is arbitrary"
    On this example `eigh` returns the $\lambda_x$ eigenvector as
    $(-0.866, -0.5)$, which points at 210°. That is the same axis as 30°. Any
    solver may flip the sign, so always reduce an eigenvector azimuth modulo
    180° (or use the doubled angle) before you compare it with anything.

## From fabric to permittivity

A single ice crystal has a permittivity $\varepsilon_c$ along its c-axis that is
slightly larger than the permittivity $\varepsilon_a$ across it:
$\Delta\varepsilon = \varepsilon_c - \varepsilon_a = 0.034$ (`ptt.constants`).
Averaged over the fabric, the permittivity tensor of solid ice is a
**linear function of the orientation tensor** (Rathmann 2026, eq. 2.5):

$$
\boldsymbol{\varepsilon} = \bar\varepsilon\,I + \Delta\varepsilon\left(\mathbf{a}^{(2)} - \tfrac13 I\right)
$$

which in code is the single line
`eps_ice = C.eps_bar + C.deps * (lam - 1/3)` in `ptt.columnProfiles`.

Adding a multiple of $I$ to a matrix, or scaling it, does not change its
eigenvectors. It only shifts and scales the eigenvalues. So:

- **the permittivity tensor has the same principal axes as the fabric**, and
- its horizontal eigenvalues differ by exactly $\Delta\varepsilon\,\Delta\lambda$.

Physically, a wave polarized along an eigenvector of $\boldsymbol\varepsilon$
travels through the ice without changing its polarization. These two
polarizations are the **eigenmodes** of the column. The one along the
$\lambda_x$ axis sees the larger permittivity, so it is the **slow** mode. The
refractive-index difference between the two modes is

$$
\Delta n \approx \frac{\Delta\varepsilon\,\Delta\lambda}{2\sqrt{\varepsilon'}}
$$

and over a thickness $\Delta z$ the two-way traveltime difference grows by

$$
\Delta\tau = \frac{2\,\Delta n\,\Delta z}{c}
= \underbrace{\frac{\Delta\varepsilon}{c\sqrt{\varepsilon'}}}_{g\ \approx\ 0.064\ \text{ns m}^{-1}}\;\Delta\lambda\;\Delta z
$$

This is the conversion `ptt.birefringentPhaseRate` owns. As a sanity check,
$\Delta\lambda = 0.1$ over 1000 m of solid ice gives
$\Delta\tau \approx 6.4$ ns. The full model in `ptt.twttDifference` adds firn
mixing and ray bending on top of this, but the dependence on $\Delta\lambda$ is
the same.

## What the antennas see: rotation is a change of basis

The radar measures the column in its own antenna frame, which is turned by an
azimuth $\psi$ from the fabric frame. Looking at a symmetric matrix from a
rotated frame means multiplying by the rotation on both sides:

$$
T(\psi) = R(\psi)^T A_h\, R(\psi)
$$

This is the same operation `ptt.rotatePolarization` applies to the measured
scattering matrix, $T = R' S R$. Applying it to the form of $A_h$ above gives

$$
T_{11} - T_{22} = \Delta\lambda\cos 2(\theta - \psi),
\qquad
T_{12} = \frac{\Delta\lambda}{2}\sin 2(\theta - \psi)
$$

and running the rotation numerically confirms it:

| $\psi$ | $T_{11}-T_{22}$ | $T_{12}$ | |
|---:|---:|---:|---|
| 0° | 0.060 | 0.052 | antennas 30° off the axis |
| 30° | **0.120** | **0.000** | aligned with the eigenvectors |
| 75° | 0.000 | −0.060 | 45° off: co-pol contrast vanishes |
| 120° | −0.120 | 0.000 | aligned, with H and V swapped |

The table shows three consequences.

1. **The off-diagonal term vanishes only in the eigenvector frame.** This is
   the definition of the eigenvectors, and it is why a cross-polarized
   (HV) null marks the fabric axis. Ershadi et al. (2022) read $\theta$ from that
   minimum (`ershadiFabric`).
2. **A co-polarized HH/VV pair measures a projection, not $\Delta\lambda$.** It
   measures $\Delta\lambda\cos 2(\theta-\psi)$. Along a single line with
   unknown $\theta$, the copol chain gives a *lower bound* on the
   contrast, and it reads zero where the antennas are 45° off the axis. This is
   also why `docs/method.md` notes that evaluating 25° off-axis scales
   $\Delta\lambda$ down by $\cos 50° \approx 0.64$.
3. **Quad-pol recovers the eigenvectors.** With HV and VH recorded, the
   whole sweep in $\psi$ can be synthesized from one pass. `quadpolFabricLS`
   fits it with $\mu = \cos 2(\psi - \theta_0)$, which is the
   $T_{11}-T_{22}$ column of the table written as a function. Its $\theta_0$ is the slow
   ($\lambda_{\max}$) eigenvector, unique modulo $\pi$.

## The other matrix: what the joint solve can resolve

Inverting $\Delta\tau(z)$ for a profile of $\Delta\lambda$ is a second
eigenvalue problem, and it explains the regularization and the
`dlam_ref_degenerate` flag.

Split the column into $m$ intervals. Each traveltime node sees the sum of the intervals above it, so to first
order (small offset, solid ice) the forward model is linear:

$$
\Delta\boldsymbol\tau = G\,\Delta\boldsymbol\lambda,
\qquad
G_{ki} = \begin{cases} g\,\Delta z_i & i \le k\\ 0 & \text{otherwise}\end{cases}
$$

`invertHorizontalFabricJoint` computes $G$ numerically as the Jacobian `A`
(its Gauss–Newton step is nearly exact because the model is so close to
linear). Then each step solves

$$
\underbrace{\left(G^T W G + \alpha D^T D\right)}_{N}\,\delta\boldsymbol\lambda = G^T W\,\mathbf{r}
$$

The **normal matrix** $N$ is symmetric, so everything above applies to it.
Its eigenvectors are depth patterns of $\Delta\lambda$, and each eigenvalue says how
strongly the data constrain that pattern. The noise in the solution along an eigenvector
scales like $1/\sqrt{\lambda_i}$.

=== "Python"

    ```python
    import numpy as np

    c, eps_p, deps = 0.299792458, 3.15, 0.034
    g = deps / (c*np.sqrt(eps_p))                 # 0.0639 ns / m / unit dlam

    m, dz = 8, 100.0                              # 8 intervals of 100 m
    G = g * dz * np.tril(np.ones((m, m)))
    N = G.T @ G

    w, V = np.linalg.eigh(N)
    print(w)                                      # ascending
    print(V[:, -1])                               # best-resolved pattern
    print(V[:, 0])                                # worst-resolved pattern

    D = np.diff(np.eye(m), axis=0)                # first differences
    alpha = 0.05 * np.trace(N) / m                # the code's default reg
    print(np.linalg.eigvalsh(N + alpha * D.T @ D))
    ```

=== "MATLAB"

    ```matlab
    c = 0.299792458; eps_p = 3.15; deps = 0.034;
    g = deps / (c*sqrt(eps_p));

    m = 8; dz = 100;
    G = g * dz * tril(ones(m));
    N = G' * G;

    [V, L] = eig(N);
    disp(diag(L)')
    disp(V(:, end)')                              % best-resolved
    disp(V(:, 1)')                                % worst-resolved

    D = diff(eye(m));
    alpha = 0.05 * trace(N) / m;
    disp(eig(N + alpha * (D' * D))')
    ```

Output (rounded):

```
eig(G'G)        10.6  11.7  14.1  18.7  28.1  51.4  136   1199
best-resolved   [0.48 0.47 0.43 0.39 0.33 0.26 0.18 0.09]   (signs arbitrary)
worst-resolved  [0.09 -0.26 0.39 -0.47 0.48 -0.43 0.33 -0.18]
eig(G'G+aD'D)   33.0  39.7  41.1  43.4  46.0  57.7  139   1199
```

- The **best-resolved** pattern is smooth and weighted toward the surface,
  because shallow intervals are seen by every node below them. It roughly
  sets the column-average contrast.
- The **worst-resolved** pattern alternates sign from one interval to the next. The
  data barely see it, so noise drives the solution toward it. This is the
  "noise-amplified oscillation" the header of `invertHorizontalFabricJoint`
  describes.
- The penalty $\alpha D^TD$ is large exactly for those alternating patterns.
  It lifts the small eigenvalues (10.6 to 33.0) and leaves the large ones almost
  unchanged, which cuts the **condition number**
  $\lambda_{\max}/\lambda_{\min}$ from 113 to 36. That is the trade the code
  makes: some depth resolution in exchange for stability.

### A zero eigenvalue: the reference offset

With `obs.zref` set, the joint solve adds one more unknown: a constant offset
$c$ in every node, to absorb error in the surface reference. That adds a
column of ones to $G$. Recompute the spectrum:

```python
Ga = np.hstack([G, np.ones((m, 1))])
w, V = np.linalg.eigh(Ga.T @ Ga)
print(w[0])                          # -> 0 (to rounding)
print(V[:, 0] / abs(V[:, 0]).max())  # -> [0.156 0 0 0 0 0 0 0 -1]
```

The smallest eigenvalue is **exactly zero**. Its eigenvector touches only
$\Delta\lambda_1$ (the shallowest interval) and the offset, in the ratio
$1/(g\,\Delta z_1) = 0.156$. The first column of $G$ is a constant, because every node
sees all of interval 1, so it is parallel to the column of ones. The data
cannot tell "more fabric in interval 1" from "a shifted reference".

A zero eigenvalue means a direction with no information at all. Only the priors
($\alpha$ and `ref_sigma_ns`) decide how the solution is split along it. This is
why the code sets `out.ref_degenerate(1) = true`, why the products carry
`dlam_ref_degenerate`, and why fabric is quoted from interval 2 down.

## Exercises

??? question "1. A matrix with no off-diagonal term"
    $A_h = \begin{bmatrix}0.35 & 0\\ 0 & 0.25\end{bmatrix}$. What are
    $\lambda_z$, $\Delta\lambda$ and $\theta$?

    **Answer.** It is already diagonal, so the eigenvalues are 0.35 and 0.25 and the
    eigenvectors are the coordinate axes. $h = 0.60$, $\lambda_z = 0.40$,
    $\Delta\lambda = 0.10$, $\theta = 0°$.

??? question "2. Equal diagonal entries"
    $A_h = \begin{bmatrix}0.30 & 0.05\\ 0.05 & 0.30\end{bmatrix}$. Where is
    the axis, and what would an HH/VV pair aligned with $x$ measure?

    **Answer.** $\tan 2\theta = 0.1/0 \Rightarrow \theta = 45°$, and
    $\Delta\lambda = \sqrt{0 + 4\cdot0.05^2} = 0.10$. Antennas along $x$ sit
    45° off the axis, so $T_{11}-T_{22} = 0.10\cos 90° = 0$. The copol chain
    reports no fabric even though $\Delta\lambda = 0.10$.

??? question "3. Isotropic in the horizontal"
    What happens to $\theta$ when $\Delta\lambda = 0$?

    **Answer.** $A_h = \tfrac{h}{2}I$, so every horizontal vector is an
    eigenvector and $\theta$ is undefined. Near this limit any estimated axis
    is noise. This is why `quadpolFabricLS` abstains on $\theta_0$ where the
    birefringence is unresolvable instead of returning a confident angle.

??? question "4. A crossing"
    Two lines cross at a site where $\Delta\lambda = 0.12$, $\theta = 30°$.
    Line 1 runs at $\psi = 0°$ and line 2 at $\psi = 90°$. What does the
    copol chain report on each line, and why do they disagree?

    **Answer.** $0.12\cos 60° = 0.06$ on line 1 and
    $0.12\cos(-120°) = -0.06$ on line 2. Swapping the antenna azimuth by 90°
    swaps H and V, which flips the sign of the projection. Two azimuths give
    two projections of one $2\times2$ matrix, which is enough to recover both
    $\Delta\lambda$ and $\theta$. That is why copol mapping of orientation
    needs survey crossings.

??? question "5. More intervals"
    Rerun the normal-matrix example with `m = 20, dz = 40`. What happens to
    the condition number of $G^TG$, and why?

    **Answer.** It grows from about 113 to about 680, roughly as $m^2$. Thinner
    intervals give more alternating patterns, each with a smaller traveltime signature.
    Resolving finer structure costs stability, which is the reason to choose
    `num_intervals` with the noise level in mind.

## Further reading

- Rathmann (2026), *Inferring glacier ice-crystal orientation fabrics from
  oblique polarimetric radar*, Proc. R. Soc. A: eq. 2.5 (permittivity from
  fabric) and eq. 4.2 (eigenvalue profiles).
- Ershadi et al. (2022), *The Cryosphere* 16, 1719: the cross-pol null and
  coherence-phase approach to $\theta$ and $\Delta\lambda$.
- In the `fabric_anisotropy` repo: `+ptt/columnProfiles.m`,
  `+ptt/rotatePolarization.m`, `+ptt/birefringentPhaseRate.m`,
  `+ptt/private/axisFold.m`, and
  `+ptt/+estimators/private/invertHorizontalFabricJoint.m`.

## Next

[Fabric from quad-pol accumulation radar](fabric-polarimetry.md) runs the
chain that produces $\Delta\lambda$ and $\theta_0$ from real data.
