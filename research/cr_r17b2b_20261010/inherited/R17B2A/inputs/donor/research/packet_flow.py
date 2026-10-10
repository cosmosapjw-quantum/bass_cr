"""Instantaneous one-cohort absorption, not a BE photon elimination."""
def loss(kappa, photons):
    return -kappa * photons
