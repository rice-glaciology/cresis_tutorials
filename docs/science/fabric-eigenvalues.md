# The horizontal fabric matrix

This is page 2 of 3. It uses the ideas from
[vectors, matrices and eigenvalues from scratch](fabric-linear-algebra.md):
vectors, the dot product, matrices acting on vectors, rotation, and
eigenvalues. If any of those terms are unfamiliar, start there; this page refers
back to its sections as "page 1, §n".

By the end you will know where the two numbers the
[fabric chain](fabric-polarimetry.md) produces come from:

- $\Delta\lambda = \lambda_x - \lambda_y$, the **strength** of the horizontal
  fabric;
- $\theta$ (written $\theta_0$ in the code), its **direction**.

Both are read off one $2\times2$ symmetric matrix that describes how the crystals in a
column of ice are oriented.

## 1. One crystal as a matrix

A crystal's c-axis is a unit vector $\mathbf{c} = (c_x, c_y)$ (page 1, §1).
For now, pretend every c-axis lies flat in the horizontal plane; §3 adds the
vertical.

We want to average many crystals, but averaging the vectors themselves fails.
$\mathbf{c}$ and $-\mathbf{c}$ are the same crystal, so a sample containing
both would average to zero. The fix is to describe each crystal by the
products of its components:

$$
\mathbf{c}\,\mathbf{c}^T =
\begin{bmatrix} c_x c_x & c_x c_y \\ c_y c_x & c_y c_y \end{bmatrix}
$$

This is called the **outer product** of $\mathbf{c}$ with itself. Flipping the
sign of $\mathbf{c}$ flips both factors in every entry, so the matrix is
unchanged, which is exactly what we want for an axis. It is also symmetric
(page 1, §4).

**Worked example.** A crystal at 30° has
$\mathbf{c} = (\cos 30°, \sin 30°) = (0.866, 0.5)$, so

$$
\mathbf{c}\,\mathbf{c}^T =
\begin{bmatrix} 0.866^2 & 0.866 \times 0.5 \\ 0.5 \times 0.866 & 0.5^2 \end{bmatrix}
= \begin{bmatrix} 0.75 & 0.433 \\ 0.433 & 0.25 \end{bmatrix}
$$

Its eigenvalues (page 1, §7) are **1, along $\mathbf{c}$ itself**, and **0,
along the perpendicular direction**. The trace is $0.75 + 0.25 = 1$ and the determinant
is $0.75 \times 0.25 - 0.433^2 = 0$, which checks. So the matrix of a single crystal
says: "everything is along this one axis, and nothing across it".

## 2. Many crystals: average the matrices

A piece of ice has millions of crystals. The **orientation matrix** is the
average of their individual matrices, written with angle brackets
$\langle\ \rangle$ for "average over crystals":

$$
A_h = \langle \mathbf{c}\,\mathbf{c}^T \rangle =
\begin{bmatrix} \langle c_x^2 \rangle & \langle c_x c_y \rangle \\
\langle c_x c_y \rangle & \langle c_y^2 \rangle \end{bmatrix}
$$

**Worked example with four crystals**, at 0°, 30°, 60° and 90°:

| crystal | $c_x^2$ | $c_x c_y$ | $c_y^2$ |
|---|---:|---:|---:|
| 0° | 1.000 | 0.000 | 0.000 |
| 30° | 0.750 | 0.433 | 0.250 |
| 60° | 0.250 | 0.433 | 0.750 |
| 90° | 0.000 | 0.000 | 1.000 |
| **average** | **0.500** | **0.217** | **0.500** |

$$
A_h = \begin{bmatrix} 0.5 & 0.217 \\ 0.217 & 0.5 \end{bmatrix}
$$

This is the same shape as the page 1 example
$\begin{bmatrix} 2 & 1 \\ 1 & 2\end{bmatrix}$: equal diagonal entries, so the
eigenvectors sit at 45° and 135°. The recipe (page 1, §7) gives

$$
(0.5 - \lambda)^2 - 0.217^2 = 0 \quad\Rightarrow\quad \lambda = 0.5 \pm 0.217 = 0.717 \text{ or } 0.283
$$

![Four crystals and a sample of 300, each with the ellipse of its averaged
matrix](img/fabric-math/crystals.png)

Read the picture as an ellipse (page 1, §6):

- The **long axis** points where the c-axes cluster. The crystals are spread
  symmetrically about 45°, so the long axis is at 45°. That eigenvector is the
  **fabric direction**.
- The **eigenvalues** say what fraction of the c-axes lies along each
  axis. They are 0.72 and 0.28 here, and in the right panel, where crystals
  cluster tightly near 30°, they are 0.83 and 0.17.
- The **difference**, $0.717 - 0.283 = 0.43$, measures how *strongly* the crystals
  prefer that direction. A random sample gives 0, and all crystals perfectly
  aligned gives 1. This difference is $\Delta\lambda$.

Two rules follow from the construction. The eigenvalues add up to 1, because each
crystal contributes trace 1. And they can **never be negative**, because each one is an
average of squared projections, $\langle(\mathbf{c}\cdot\mathbf{u})^2\rangle$.

## 3. Adding the vertical

Real c-axes point in three dimensions, $\mathbf{c} = (c_x, c_y, c_z)$, so
the full orientation matrix is $3\times3$:

$$
\mathbf{a}^{(2)} = \langle \mathbf{c}\,\mathbf{c}^T \rangle =
\begin{bmatrix}
\langle c_x^2\rangle & \langle c_x c_y\rangle & \langle c_x c_z\rangle\\
\langle c_x c_y\rangle & \langle c_y^2\rangle & \langle c_y c_z\rangle\\
\langle c_x c_z\rangle & \langle c_y c_z\rangle & \langle c_z^2\rangle
\end{bmatrix}
$$

Glaciologists call it the **second-order orientation tensor** ("tensor" just
means a matrix that describes a physical property). Everything from page 1 still
holds in 3D: it has three real eigenvalues, three perpendicular eigenvectors,
and the eigenvalues still add up to 1. Three standard cases:

| fabric | eigenvalues | what the crystals do |
|---|---|---|
| isotropic | $(\tfrac13, \tfrac13, \tfrac13)$ | point every which way |
| single maximum | $(0, 0, 1)$ | all point along one direction |
| girdle | $(\tfrac12, \tfrac12, 0)$ | spread evenly around a plane |

Real ice falls in between. The code stores the three eigenvalues as
`lam = [lam_x lam_y lam_z]` (`ptt.columnProfiles`), where `lam_z` is the
vertical one.

## 4. What a radar looking down can see

A ground-based radar sends its waves nearly straight down. The electric field
of a wave always points *across* its direction of travel, so for a downgoing wave
the field is **horizontal**. The radar therefore only sees how the matrix acts
on horizontal vectors.

The method assumes one eigenvector of $\mathbf{a}^{(2)}$ is vertical, which
is reasonable away from steep bed topography. The zeros in the matrix below
express that assumption: nothing mixes horizontal and vertical.

$$
\mathbf{a}^{(2)} =
\begin{bmatrix}
a_{xx} & a_{xy} & 0\\
a_{xy} & a_{yy} & 0\\
0 & 0 & \lambda_z
\end{bmatrix}
\qquad\Longrightarrow\qquad
A_h =
\begin{bmatrix}
a_{xx} & a_{xy}\\
a_{xy} & a_{yy}
\end{bmatrix}
$$

The top-left $2\times2$ block, $A_h$, is the **horizontal fabric matrix**.
It works just like the four-crystal example. The only difference is that its eigenvalues
now add up to

$$
h = a_{xx} + a_{yy} = 1 - \lambda_z
$$

rather than 1, because the vertical eigenvalue $\lambda_z$ takes its share.

## 5. Reading the strength and direction off any horizontal matrix

Apply the recipe from page 1, §7 to a general $A_h$. Setting
$\det(A_h - \lambda I) = 0$ gives the quadratic

$$
\lambda^2 - (a_{xx} + a_{yy})\,\lambda + (a_{xx}a_{yy} - a_{xy}^2) = 0
$$

Using the quadratic formula,
$\lambda = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$, and tidying up, gives

$$
\lambda_{x,y} = \frac{h}{2} \pm \sqrt{\left(\frac{a_{xx}-a_{yy}}{2}\right)^2 + a_{xy}^2}
$$

The two eigenvalues sit symmetrically about their average $h/2$. Subtracting
one from the other gives the number the fabric chain inverts for:

$$
\boxed{\Delta\lambda = \lambda_x - \lambda_y = \sqrt{(a_{xx}-a_{yy})^2 + 4a_{xy}^2}}
$$

Putting $\lambda_x$ back into $(A_h - \lambda I)\mathbf{v} = \mathbf{0}$ and
simplifying with two trigonometric identities gives the direction $\theta$ of its
eigenvector:

$$
\boxed{\tan 2\theta = \frac{2a_{xy}}{a_{xx} - a_{yy}}}
$$

Check both against the four crystals: $a_{xx} - a_{yy} = 0$ and
$a_{xy} = 0.217$, so $\Delta\lambda = \sqrt{0 + 4 \times 0.217^2} = 0.43$ and
$\tan 2\theta = \infty$, which means $2\theta = 90°$ and $\theta = 45°$.

### Why the angle is doubled

Turning an axis by 180° gives the same axis (page 1, §1). A formula for an
axis therefore cannot tell $\theta$ from $\theta + 180°$, and doubling the
angle is exactly what makes those two the same: $2\theta$ and $2\theta + 360°$
point the same way. Written with the doubled angle, the matrix
comes apart into two pieces:

$$
A_h = \underbrace{\frac{h}{2}\,I}_{\text{isotropic part}}
\;+\; \underbrace{\frac{\Delta\lambda}{2}
\begin{bmatrix}
\cos 2\theta & \sin 2\theta\\
\sin 2\theta & -\cos 2\theta
\end{bmatrix}}_{\text{anisotropic part}}
$$

(Multiply out the four crystals to check: $h = 1$, $\Delta\lambda = 0.43$
and $\theta = 45°$ give back $\begin{bmatrix} 0.5 & 0.217 \\ 0.217 & 0.5\end{bmatrix}$.)

- The **isotropic part** looks the same in every horizontal direction. A
  radar that compares two polarizations subtracts it away, so it cannot see it.
  This is why the common-offset inversion has to *assume* $\lambda_z$ and
  therefore $h$.
- The **anisotropic part** holds the two things the radar does see: the
  strength $\Delta\lambda$ and the direction $\theta$.

This explains several lines of code in `invertHorizontalFabricJoint`. It takes
an assumed $\lambda_z$, sets `h = 1 - lam_z`, and for a trial
$\Delta\lambda$ sets `lam_x = (h + dlam)/2`. It also clips
$|\Delta\lambda| < h$, because $\lambda_y = (h - \Delta\lambda)/2$ would
otherwise turn negative, which §2 showed is impossible. That clip is the
"eigenvalue bound" reported in `out.clipped`.

!!! note "Why the code never unwraps an axis angle"
    Averaging raw axis angles goes wrong across the 0/180 wrap. The mean of
    1° and 179° is 90°, perpendicular to both, even though both are nearly
    the east–west axis. The fix used throughout `+ptt` (`axisFold`,
    `thetaProfileAt`) is to average the **doubled angle**: average the unit
    vectors $(\cos 2\theta, \sin 2\theta)$, find the angle of the result, and
    halve it. The rule "never unwrap axis angles" in the
    [troubleshooting habits](fabric-polarimetry.md#trouble-shooting-habits)
    comes from this.

### Try it

Build $A_h$ from chosen eigenvalues and a direction ("rotate, stretch,
rotate back", page 1, §8), then take it apart again:

=== "Python"

    ```python
    import numpy as np

    lam_z = 0.40                     # assumed vertical eigenvalue
    h     = 1 - lam_z                # left for the horizontal plane
    dlam  = 0.12                     # lam_x - lam_y
    theta = np.deg2rad(30)           # direction of the lam_x eigenvector

    lam_x, lam_y = (h + dlam)/2, (h - dlam)/2
    R = np.array([[np.cos(theta), -np.sin(theta)],
                  [np.sin(theta),  np.cos(theta)]])
    A = R @ np.diag([lam_x, lam_y]) @ R.T

    w, V = np.linalg.eigh(A)
    v = V[:, -1]                     # eigenvector of the larger eigenvalue
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

    [V, L] = eig(A);
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

Check by hand: the trace is $0.33 + 0.27 = 0.60 = h$, and the determinant is
$0.33 \times 0.27 - 0.052^2 = 0.0864 = 0.24 \times 0.36$. The boxed formulas
give $\Delta\lambda = \sqrt{0.06^2 + 4 \times 0.052^2} = 0.12$ and
$\theta = \tfrac12 \arctan(0.104 / 0.06) = 30°$.

On this example `eigh` actually returns the $\lambda_x$ eigenvector as
$(-0.866, -0.5)$, which points at 210°. That is the same axis as 30°, which is why the
code takes the angle modulo 180.

## 6. From crystals to radio waves

**Permittivity** sets how fast a radio wave travels through a material: the
higher it is, the slower the wave. A single ice crystal has a slightly
higher permittivity for a field along its c-axis ($\varepsilon_c$) than
across it ($\varepsilon_a$). The difference is small,
$\Delta\varepsilon = \varepsilon_c - \varepsilon_a = 0.034$
(`ptt.constants`), but over hundreds of metres it adds up.

Because the answer depends on direction, the permittivity of ice is a
symmetric matrix too, and it is built directly from the fabric matrix
(Rathmann 2026, eq. 2.5):

$$
\boldsymbol{\varepsilon} = \bar\varepsilon\,I + \Delta\varepsilon\left(\mathbf{a}^{(2)} - \tfrac13 I\right)
$$

In code this is the single line `eps_ice = C.eps_bar + C.deps * (lam - 1/3)`
in `ptt.columnProfiles`.

Adding a multiple of $I$ to a matrix, or multiplying it by a number, moves
and scales the ellipse but **does not turn it**. So:

- **the permittivity matrix has the same eigenvectors as the fabric**, and
- its two horizontal eigenvalues differ by $\Delta\varepsilon\,\Delta\lambda$.

What this means for a wave: a wave whose field points along an eigenvector of
$\boldsymbol\varepsilon$ travels down the column without its field direction
changing. These two special polarizations are the column's
**eigenmodes**. The one along the $\lambda_x$ eigenvector has the larger
permittivity, so it is the **slow** wave. After travelling down to a reflector and back, the slow wave
arrives later than the fast one, and the delay grows with depth:

$$
\Delta\tau = \underbrace{\frac{\Delta\varepsilon}{c\sqrt{\varepsilon'}}}_{g\ \approx\ 0.064\ \text{ns per m}}\;\Delta\lambda\;\Delta z
$$

Here $c$ is the speed of light, $\varepsilon' \approx 3.15$ is the
permittivity of ice, and $\Delta z$ is the thickness travelled. For example,
$\Delta\lambda = 0.1$ over 1000 m of solid ice gives
$\Delta\tau \approx 6.4$ ns. This traveltime difference is what the fabric chain
measures. The full model (`ptt.twttDifference`, `ptt.birefringentPhaseRate`)
adds firn and ray bending, but it depends on $\Delta\lambda$ in the same way.

## 7. What the antennas see

The antennas have their own frame, turned by an azimuth $\psi$ from the
fabric's. To see the fabric matrix "through the antennas", rotate into their
frame (page 1, §5):

$$
T(\psi) = R(\psi)^T A_h\, R(\psi)
$$

`ptt.rotatePolarization` applies exactly this to the measured
scattering matrix, $T = R' S R$. Multiplying it out with the two-part form from §5
gives

$$
T_{11} - T_{22} = \Delta\lambda\cos 2(\theta - \psi),
\qquad
T_{12} = \frac{\Delta\lambda}{2}\sin 2(\theta - \psi)
$$

$T_{11} - T_{22}$ is the HH/VV contrast the antennas measure, and $T_{12}$ is
the cross term. Here they are for the example above ($\Delta\lambda = 0.12$, $\theta = 30°$):

| antenna azimuth $\psi$ | $T_{11}-T_{22}$ | $T_{12}$ | |
|---:|---:|---:|---|
| 0° | 0.060 | 0.052 | antennas 30° off the fabric axis |
| 30° | **0.120** | **0.000** | lined up with the eigenvectors |
| 75° | 0.000 | −0.060 | 45° off: the co-pol contrast vanishes |
| 120° | −0.120 | 0.000 | lined up, with H and V swapped |

The table shows three consequences.

1. **The cross term vanishes only when the antennas line up with the
   eigenvectors.** That is just page 1, §6 again: in its own frame a symmetric
   matrix is diagonal. It is why a null in the cross-polarized (HV) signal
   marks the fabric axis, which is how Ershadi et al. (2022) read $\theta$
   (`ershadiFabric`).
2. **A co-polarized HH/VV pair sees only a projection of $\Delta\lambda$.**
   It measures $\Delta\lambda\cos 2(\theta - \psi)$, which is never more than $\Delta\lambda$
   and is zero when the antennas are 45° off the axis. This is why
   `docs/method.md` notes that working 25° off-axis scales $\Delta\lambda$ down by
   $\cos 50° \approx 0.64$.
3. **Quad-pol recovers the eigenvectors.** With HV and VH recorded, the
   response at every $\psi$ can be computed from one pass. `quadpolFabricLS`
   fits the whole sweep using $\mu = \cos 2(\psi - \theta_0)$, which is the
   $T_{11} - T_{22}$ column above written as a formula. Its $\theta_0$ is the slow
   ($\lambda_{\max}$) eigenvector, defined modulo 180°.

## Exercises

??? question "1. A matrix that is already diagonal"
    $A_h = \begin{bmatrix}0.35 & 0\\ 0 & 0.25\end{bmatrix}$. What are
    $\lambda_z$, $\Delta\lambda$ and $\theta$?

    **Answer.** It is already diagonal, so the eigenvalues are 0.35 and 0.25 along the
    x and y axes. $h = 0.60$, $\lambda_z = 0.40$, $\Delta\lambda = 0.10$,
    $\theta = 0°$.

??? question "2. Equal diagonal entries"
    $A_h = \begin{bmatrix}0.30 & 0.05\\ 0.05 & 0.30\end{bmatrix}$. Where is
    the axis, and what would an HH/VV pair lined up with $x$ measure?

    **Answer.** $a_{xx} - a_{yy} = 0$, so $\theta = 45°$, and
    $\Delta\lambda = \sqrt{0 + 4 \times 0.05^2} = 0.10$. Antennas along $x$
    are 45° off the axis, so $T_{11}-T_{22} = 0.10\cos 90° = 0$. The co-pol
    chain would report no fabric, even though $\Delta\lambda = 0.10$.

??? question "3. No preferred direction"
    What happens to $\theta$ when $\Delta\lambda = 0$?

    **Answer.** $A_h = \tfrac{h}{2}I$, a circle rather than an ellipse, so
    *every* horizontal direction is an eigenvector and $\theta$ is undefined.
    Close to this case, any estimated direction is mostly noise. This is why
    `quadpolFabricLS` declines to report $\theta_0$ where the birefringence is too
    weak to resolve.

??? question "4. A crossing"
    Two survey lines cross at a site where $\Delta\lambda = 0.12$ and $\theta = 30°$.
    Line 1 runs at $\psi = 0°$ and line 2 at $\psi = 90°$. What does the
    co-pol chain report on each, and why do they disagree?

    **Answer.** $0.12\cos 60° = 0.06$ on line 1, and
    $0.12\cos(-120°) = -0.06$ on line 2. Turning the antennas by 90° swaps H
    and V, which flips the sign. Two azimuths give two different views of the same
    $2\times2$ matrix, which is enough to recover both $\Delta\lambda$ and
    $\theta$. That is why co-pol mapping of fabric direction needs survey
    crossings.

??? question "5. Your own crystals"
    Pick five angles, build $A_h$ by averaging the outer products as in §2,
    and compare `eigh` with the boxed formulas.

    **Answer.** They agree to rounding for any angles you choose. In Python:
    `C = np.vstack([np.cos(a), np.sin(a)]); A = C @ C.T / len(a)`.

## Next

[What the inversion can resolve](fabric-inversion-eigenvalues.md) turns to a
second symmetric matrix, the one `invertHorizontalFabricJoint` builds from
the data. Its eigenvalues show which depth profiles of $\Delta\lambda$ the
radar can and cannot pin down.
