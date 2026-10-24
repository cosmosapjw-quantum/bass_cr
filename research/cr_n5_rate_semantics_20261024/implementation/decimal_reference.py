"""Independent 80-digit references; no production arithmetic is imported."""
from decimal import Decimal, localcontext


def dec(value):
    return Decimal(str(value))


def reference_hazard_limit(epsilon, mean):
    with localcontext() as context:
        context.prec = 80
        # This reference checks the supplied binary64 inputs, not nearby decimal
        # literals. Near epsilon=1, changing the input itself is ill-conditioned.
        eps = Decimal.from_float(epsilon) if isinstance(epsilon, float) else dec(epsilon)
        duration = Decimal.from_float(mean) if isinstance(mean, float) else dec(mean)
        return -(Decimal(1) - eps).ln() / duration


def reference_product(*values):
    with localcontext() as context:
        context.prec = 80
        out = Decimal(1)
        for value in values:
            out *= dec(value)
        return +out


def scaled_error(actual, reference):
    reference = dec(reference)
    with localcontext() as context:
        context.prec = 80
        error = abs(dec(actual) - reference)
        if reference == 0:
            return Decimal(0) if error == 0 else Decimal("Infinity")
        return error / abs(reference)


def reference_envelope(channels, domain, threshold, density, ev, mass):
    """Endpoint oracle independent of the production stationary search.

    For W>=0 affine on a positive interval, an interior stationary point of
    W/sqrt(E) is a minimum. Thus the union of channel knots and clipped domain
    endpoints is sufficient. Exact Decimal interpolation avoids binary slopes.
    """
    with localcontext() as context:
        context.prec = 80
        low, high = map(dec, domain)
        threshold = dec(threshold)
        data = {key: (list(map(dec, x)), list(map(dec, y))) for key, (x, y) in channels.items()}
        points = {low, high}
        if low < threshold < high:
            points.add(threshold)
        for x, _ in data.values():
            points.update(v for v in x if low < v < high)
        prefactor = dec(density) * 100 * (2 * dec(ev) / dec(mass)).sqrt()
        best = (Decimal(-1), None)
        for point in sorted(points):
            total = Decimal(0)
            if point >= threshold:
                for x, y in data.values():
                    if point in x:
                        total += y[x.index(point)]
                        continue
                    for i in range(len(x) - 1):
                        if x[i] < point < x[i + 1]:
                            t = (point - x[i]) / (x[i + 1] - x[i])
                            total += (1 - t) * y[i] + t * y[i + 1]
                            break
                    else:
                        raise ValueError("REFERENCE_OUTSIDE_SOURCE")
            value = prefactor * total / point.sqrt()
            if value > best[0]:
                best = value, point
        return {"hmax": +best[0], "energy_eV": +best[1], "precision_digits": 80}


def reference_first_event(hmax, mean, fraction):
    with localcontext() as context:
        context.prec = 80
        active = 1 - (-dec(hmax) * dec(mean)).exp()
        return +active, +(dec(fraction) * active)
