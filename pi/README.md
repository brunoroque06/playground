# Estimation of π Using Monte Carlo Method

Given a square containing a circle, with a radius of half the size of the square's side, the following equation is true:

```math
π * r ^ 2    Pin             Ar * Pin
--------- = ------ => π = --------------
    Ar      Ptotal        Ptotal * r ^ 2
```

where:

- `r`, circle's radius;
- `Ar`, rectangle's area;
- `Pin`, number of points inside the circle;
- `Ptotal`, total number of points.

The points above mentioned are randomly placed in the square, where some of those will be inside the circle, and the orhter won't. The precision of the estimation increases as the number of points increase.