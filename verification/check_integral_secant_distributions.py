#!/usr/bin/env python3
"""Exact checks for the integer secant-distribution bounds in the paper."""

from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from fractions import Fraction
from itertools import product
from math import comb, isqrt
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "integral-secant-checks.json"
CHECKSUMS = ROOT / "integral-secant-checks.sha256"
Q_VALUES = (4, 5, 7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 27, 31, 32, 49, 64, 81, 125, 128, 243, 256)
WIDE_DEGREE_Q_VALUES = (7, 8, 9, 11, 13, 16, 17, 19, 23, 25, 27, 31, 32)
LAMBDA_VALUES = (1, 2, 3)
RESONANCE_LAMBDA_MAX = 32


def fraction_record(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def prime_power_base(value: int) -> int | None:
    for prime in range(2, value + 1):
        if any(prime % divisor == 0 for divisor in range(2, prime)):
            continue
        residual = value
        while residual % prime == 0:
            residual //= prime
        if residual == 1:
            return prime
    return None


def resonance_record(u: int, v: int) -> dict[str, object]:
    """Exact first-order data for the ordered factor-pair resonance uv=lambda."""
    d = u + v + 1
    spectral = Fraction(u * (u * v + 3 * u + 2 * v + 3), 2 * u + 1)
    continuous = Fraction(
        u * (u * v * v + 4 * u * v + 2 * u + 2 * v * v + 4 * v + 1),
        2 * u * v + u + v,
    )
    gain = Fraction(
        u * (v + 1) * (u * u + u + 1),
        (2 * u + 1) * (2 * u * v + u + v),
    )
    h0 = Fraction(
        -u * (v + 1) * (u * u * v + u * u - v),
        2 * u * v + u + v,
    )
    slope = Fraction(2 * v, (u + v) * (2 * u * v + u + v + 1))
    exception_per_q = Fraction(
        u * (v + 1) * (v + 1) * (u * u + u + 1),
        2 * u * v + u + v,
    )

    def lower(h: int) -> Fraction:
        return Fraction(d) - Fraction(h, u)

    def moment(h: int) -> Fraction:
        return continuous + slope * (h - h0)

    h_floor = h0.numerator // h0.denominator
    candidates = (h_floor, h_floor + 1)
    lattice, minimizing_h = min((max(lower(h), moment(h)), h) for h in candidates)

    # Independent finite convexity check: the maximum of a decreasing and an
    # increasing affine function is minimized next to their real crossing.
    brute = min(
        (max(lower(h), moment(h)), h)
        for h in range(h_floor - 8, h_floor + 10)
    )
    assert brute == (lattice, minimizing_h)

    modular_lift_records = {}
    for support_size in (1, 2):
        shifted_crossing = h0 + Fraction(support_size, 1 + u * slope)
        shifted_floor = shifted_crossing.numerator // shifted_crossing.denominator
        shifted_candidates = (shifted_floor, shifted_floor + 1)
        shifted_lattice, shifted_h = min(
            (
                max(
                    lower(h) + Fraction(support_size, u),
                    moment(h),
                ),
                h,
            )
            for h in shifted_candidates
        )
        shifted_brute = min(
            (
                max(
                    lower(h) + Fraction(support_size, u),
                    moment(h),
                ),
                h,
            )
            for h in range(shifted_floor - 8, shifted_floor + 10)
        )
        assert shifted_brute == (shifted_lattice, shifted_h)
        assert shifted_lattice > lattice
        modular_lift_records[str(support_size)] = {
            "coefficient": fraction_record(shifted_lattice),
            "minimizing_h": shifted_h,
            "shifted_crossing": fraction_record(shifted_crossing),
            "gain_over_lattice_envelope": fraction_record(shifted_lattice - lattice),
        }

    characteristic = prime_power_base(d)
    residue_aware_record = None
    if characteristic is not None:
        residue_candidates = []
        search_radius = 4 * characteristic + 20
        for h in range(h_floor - search_radius, h_floor + search_radius + 1):
            minimum_support = 2 if (h - u * v) % characteristic == 0 else 1
            residue_candidates.append(
                (
                    max(
                        lower(h) + Fraction(minimum_support, u),
                        moment(h),
                    ),
                    h,
                    minimum_support,
                )
            )
        residue_coefficient, residue_h, residue_support = min(residue_candidates)
        assert residue_coefficient > lattice
        residue_aware_record = {
            "characteristic": characteristic,
            "coefficient": fraction_record(residue_coefficient),
            "minimizing_h": residue_h,
            "minimum_support_at_minimizer": residue_support,
            "gain_over_lattice_envelope": fraction_record(residue_coefficient - lattice),
        }
    assert continuous - spectral == gain
    assert lattice >= continuous > spectral
    crossing_denominator = 2 * u * v + u + v
    crossing_numerator = u * (v + 1) * (u * u * v + u * u - v)
    divisor_target = u * u * (u + 1) * (u * u + u + 1)
    assert (crossing_numerator % crossing_denominator == 0) == (
        divisor_target % crossing_denominator == 0
    )
    assert (h0.denominator == 1) == (divisor_target % crossing_denominator == 0)
    internal_excess_per_n = (
        -continuous * u * v
        - continuous * u
        - continuous * v
        - continuous
        + h0 * u
        + h0
        + u * u * v
        + u * u
        + u * v * v
        + 2 * u * v
        + u
    )
    assert -internal_excess_per_n / d == exception_per_q

    return {
        "lambda": u * v,
        "u": u,
        "v": v,
        "density_alpha": fraction_record(Fraction(u + 1, d)),
        "density_beta": fraction_record(Fraction(u, d)),
        "balanced_internal_degree": (u + 1) * (v + 1),
        "spectral_linear_coefficient": fraction_record(spectral),
        "continuous_envelope_coefficient": fraction_record(continuous),
        "certified_linear_gain": fraction_record(gain),
        "lattice_envelope_coefficient": fraction_record(lattice),
        "crossing_h0": fraction_record(h0),
        "minimizing_h": minimizing_h,
        "double_tight": h0.denominator == 1,
        "double_tight_exception_per_q": fraction_record(exception_per_q),
        "conditional_modular_lift_support": modular_lift_records,
        "conditional_residue_aware_modular_lift": residue_aware_record,
    }


def first_moment_minimum(q: int, s: int, lam: int = 1) -> int:
    """Smallest k not excluded by the Alabdullah--Hirschfeld inequality."""
    for k in range(s + 1, (s - 1) * q + s + 1):
        lhs = lam * (q * q + q + 1 - k) * s * (s - 1)
        rhs = k * (k - 1) * (q + 1 - s)
        if lhs <= rhs:
            return k
    raise AssertionError((q, s))


def convex_degree_maximum(k: int, degree_cap: int, degree_sum: int) -> int:
    full, remainder = divmod(degree_sum, degree_cap)
    if full > k or (full == k and remainder):
        raise ValueError("infeasible degree sum")
    return full * comb(degree_cap, 2) + comb(remainder, 2)


def convex_degree_minimum(vertices: int, degree_sum: int) -> int:
    """Minimum pair count for a fixed nonnegative integer degree sum."""
    quotient, remainder = divmod(degree_sum, vertices)
    return (vertices - remainder) * comb(quotient, 2) + remainder * comb(quotient + 1, 2)


def congruence_degree_minimum(
    vertices: int,
    degree_sum: int,
    modulus: int,
    residue: int,
    lower: int = 0,
) -> int | None:
    """Minimum pair sum for degrees in one residue class above a lower bound."""
    base = lower + (residue - lower) % modulus
    shifted = degree_sum - vertices * base
    if shifted < 0 or shifted % modulus:
        return None
    quotient, remainder = divmod(shifted // modulus, vertices)
    low_degree = base + modulus * quotient
    high_degree = low_degree + modulus
    return (vertices - remainder) * comb(low_degree, 2) + remainder * comb(
        high_degree, 2
    )


def bounded_degree_maximum(vertices: int, lower: int, upper: int, degree_sum: int) -> int:
    """Maximum pair count with a common lower and upper degree bound."""
    excess = degree_sum - vertices * lower
    capacity = upper - lower
    if excess < 0 or excess > vertices * capacity:
        raise ValueError("infeasible bounded degree sum")
    if capacity == 0:
        return vertices * comb(lower, 2)
    return (
        vertices * comb(lower, 2)
        + lower * excess
        + convex_degree_maximum(vertices, capacity, excess)
    )


def capacity_numerator(q: int, k: int, s: int, lam: int, t: int) -> tuple[int, int]:
    matching_cap = k // s
    degree_cap = (k - 1) // (s - 1)
    degree_sum = s * t
    max_internal_pairs = convex_degree_maximum(k, degree_cap, degree_sum)
    second_moment_lower = max(0, comb(t, 2) - max_internal_pairs)
    numerator = (matching_cap + lam - 1) * t * (q + 1 - s) - 2 * second_moment_lower
    denominator = lam * matching_cap
    return numerator, denominator


def second_moment_minimum(q: int, s: int, lam: int = 1) -> int | None:
    """Smallest k not excluded by the exact one-variable degree envelope."""
    start = first_moment_minimum(q, s, lam)
    for k in range(start, (s - 1) * q + s + 1):
        matching_cap = k // s
        if matching_cap < lam:
            continue
        degree_cap = (k - 1) // (s - 1)
        t_max = min(k * (k - 1) // (s * (s - 1)), k * degree_cap // s)
        feasible_t = (t_max,) if s == 2 else range(1, t_max + 1)
        max_num = None
        common_den = lam * matching_cap
        for t in feasible_t:
            numerator, denominator = capacity_numerator(q, k, s, lam, t)
            assert denominator == common_den
            if max_num is None or numerator > max_num:
                max_num = numerator
        required = q * q + q + 1 - k
        if max_num is not None and common_den * required <= max_num:
            return k
    return None


def spectral_minimum(q: int, s: int, lam: int = 1) -> int | None:
    """Complementary threshold from Bishnoi--Mattheus--Schillewaert, Theorem 8.1."""
    point_count = q * q + q + 1
    blocking_order = q + 1 - s
    for k in range(s + 1, (s - 1) * q + s + 1):
        blocking_size = point_count - k
        quadratic = (
            lam * blocking_size * blocking_size
            - (2 * lam * blocking_order * (q + 1) - (lam + blocking_order) * q)
            * blocking_size
            - blocking_order * (q - lam * blocking_order) * point_count
        )
        if quadratic <= 0:
            return k
    return None


def paired_moment_minimum(q: int, s: int, lam: int = 1, spectral: bool = False) -> int | None:
    """Threshold from overlapping the internal and external pair-count intervals."""
    point_count = q * q + q + 1
    blocking_order = q + 1 - s
    start = first_moment_minimum(q, s, lam)
    for k in range(start, (s - 1) * q + s + 1):
        matching_cap = k // s
        if matching_cap < lam:
            continue
        external_points = point_count - k
        degree_cap = (k - 1) // (s - 1)
        t_max = min(k * (k - 1) // (s * (s - 1)), k * degree_cap // s)
        feasible_t = (t_max,) if s == 2 else range(1, t_max + 1)
        for t in feasible_t:
            external_degree_sum = blocking_order * t
            if not lam * external_points <= external_degree_sum <= matching_cap * external_points:
                continue

            internal_minimum = convex_degree_minimum(k, s * t)
            internal_maximum = convex_degree_maximum(k, degree_cap, s * t)
            pair_total = comb(t, 2)
            internal_external_minimum = pair_total - internal_maximum
            internal_external_maximum = pair_total - internal_minimum

            external_minimum = convex_degree_minimum(external_points, external_degree_sum)
            external_maximum = bounded_degree_maximum(
                external_points, lam, matching_cap, external_degree_sum
            )
            if max(internal_external_minimum, external_minimum) > min(
                internal_external_maximum, external_maximum
            ):
                continue

            if spectral:
                gap = point_count * blocking_order - (q + 1) * external_points
                if t * gap * gap > q * external_points * k * (point_count - t):
                    continue
            return k
    return None


@lru_cache(maxsize=None)
def dp_degree_maximum(vertices: int, cap: int, total: int) -> int | None:
    """Independent small dynamic program for the convex-envelope check."""
    if vertices == 0:
        return 0 if total == 0 else None
    best = None
    for degree in range(min(cap, total) + 1):
        tail = dp_degree_maximum(vertices - 1, cap, total - degree)
        if tail is not None:
            value = comb(degree, 2) + tail
            best = value if best is None else max(best, value)
    return best


@lru_cache(maxsize=None)
def dp_degree_minimum(vertices: int, cap: int, total: int) -> int | None:
    """Independent small dynamic program for the balanced-minimum check."""
    if vertices == 0:
        return 0 if total == 0 else None
    best = None
    for degree in range(min(cap, total) + 1):
        tail = dp_degree_minimum(vertices - 1, cap, total - degree)
        if tail is not None:
            value = comb(degree, 2) + tail
            best = value if best is None else min(best, value)
    return best


def run_checks() -> dict[str, object]:
    checked_congruence_envelopes = 0
    for vertices in range(1, 6):
        for modulus in (2, 3):
            for residue in range(modulus):
                for lower in range(3):
                    max_total = 3 * vertices + lower
                    allowed = [
                        degree
                        for degree in range(lower, max_total + 1)
                        if degree % modulus == residue
                    ]
                    for degree_sum in range(vertices * lower, max_total + 1):
                        brute_values = [
                            sum(comb(degree, 2) for degree in degrees)
                            for degrees in product(allowed, repeat=vertices)
                            if sum(degrees) == degree_sum
                        ]
                        brute = min(brute_values) if brute_values else None
                        formula = congruence_degree_minimum(
                            vertices, degree_sum, modulus, residue, lower
                        )
                        assert formula == brute
                        checked_congruence_envelopes += 1

    checked_envelopes = 0
    for k in range(3, 21):
        for s in range(2, min(6, k)):
            cap = (k - 1) // (s - 1)
            max_total = k * cap
            for total in range(max_total + 1):
                direct = dp_degree_maximum(k, cap, total)
                formula = convex_degree_maximum(k, cap, total)
                assert direct == formula, (k, s, total, direct, formula)
                checked_envelopes += 1

    checked_bounded_envelopes = 0
    for vertices in range(1, 9):
        for lower in range(4):
            for upper in range(lower, 6):
                for total in range(vertices * lower, vertices * upper + 1):
                    shifted = dp_degree_maximum(vertices, upper - lower, total - vertices * lower)
                    assert shifted is not None
                    direct_maximum = vertices * comb(lower, 2) + lower * (
                        total - vertices * lower
                    ) + shifted
                    formula_maximum = bounded_degree_maximum(vertices, lower, upper, total)
                    assert direct_maximum == formula_maximum
                    direct_minimum = dp_degree_minimum(vertices, upper, total)
                    formula_minimum = convex_degree_minimum(vertices, total)
                    assert direct_minimum == formula_minimum
                    checked_bounded_envelopes += 1

    checked_arc_specializations = 0
    for k in range(4, 41):
        t = comb(k, 2)
        cap = k - 1
        lower = comb(t, 2) - convex_degree_maximum(k, cap, 2 * t)
        assert lower == 3 * comb(k, 4), (k, lower, 3 * comb(k, 4))
        checked_arc_specializations += 1

    checked_spectral_equivalences = 0
    for q in range(3, 17):
        point_count = q * q + q + 1
        for s in range(2, q + 1):
            blocking_order = q + 1 - s
            for lam in LAMBDA_VALUES:
                for k in range(s + 1, (s - 1) * q + s + 1):
                    blocking_size = point_count - k
                    cleared_cauchy = (
                        lam * blocking_size * s * s
                        + lam * k * blocking_order * blocking_order
                        - lam * k * blocking_size
                        - q * blocking_order * k
                    )
                    bms_quadratic = (
                        lam * blocking_size * blocking_size
                        - (
                            2 * lam * blocking_order * (q + 1)
                            - (lam + blocking_order) * q
                        )
                        * blocking_size
                        - blocking_order
                        * (q - lam * blocking_order)
                        * point_count
                    )
                    assert cleared_cauchy == bms_quadratic
                    checked_spectral_equivalences += 1

    checked_infinite_family_instances = 0
    for q in range(16, 97, 8):
        s = q // 2 + 1
        spectral = spectral_minimum(q, s, 2)
        paired = paired_moment_minimum(q, s, 2)
        assert spectral == s * s
        assert paired == s * s + q // 8 - 1
        checked_infinite_family_instances += 1

    checked_ordinary_resonance_instances = 0
    for n in range(3, 33):
        q = 3 * n
        s = 2 * n + 1
        spectral = spectral_minimum(q, s, 1)
        paired = paired_moment_minimum(q, s, 1)
        spectral_formula = 3 * n * n + 3 * n + 1
        paired_formula = spectral_formula + (3 * n - 2) // 5
        assert spectral == spectral_formula
        assert paired == paired_formula
        checked_ordinary_resonance_instances += 1

    checked_conjugate_resonance_instances = 0
    for m in range(2, 65):
        q = 8 * m
        s = 6 * m + 1
        spectral_offset = (52 * m + 9) // 5
        spectral_polynomial = lambda ell: (
            ell * ell
            - (40 * m * m + 20 * m + 2) * ell
            + 416 * m**3
            + 132 * m * m
            + 20 * m
            + 1
        )
        assert spectral_polynomial(spectral_offset - 1) > 0
        assert spectral_polynomial(spectral_offset) <= 0

        paired_bound = 32 * m * m + 12 * m - 1
        excluded_k = paired_bound - 1
        point_count = q * q + q + 1
        complement_size = point_count - excluded_k
        blocking_order = q + 1 - s
        t_min = (2 * complement_size + blocking_order - 1) // blocking_order
        obstruction = (
            convex_degree_minimum(excluded_k, s * t_min)
            + convex_degree_minimum(complement_size, blocking_order * t_min)
            - comb(t_min, 2)
        )
        assert obstruction > 0
        checked_conjugate_resonance_instances += 1

    checked_sharp_conjugate_resonance_instances = 0
    for m in range(2, 65):
        q = 8 * m
        s = 6 * m + 1
        point_count = q * q + q + 1
        blocking_order = 2 * m
        base = 32 * m * m + 12 * m - 1
        correction = 0 if m <= 6 else (1 if m <= 12 else 2)
        threshold = base + correction
        for k, should_obstruct in ((threshold - 1, True), (threshold, False)):
            complement_size = point_count - k
            t_min = (2 * complement_size + blocking_order - 1) // blocking_order
            obstruction = (
                convex_degree_minimum(k, s * t_min)
                + convex_degree_minimum(complement_size, blocking_order * t_min)
                - comb(t_min, 2)
            )
            assert (obstruction > 0) == should_obstruct
            if not should_obstruct:
                degree_cap = (k - 1) // (s - 1)
                matching_cap = k // s
                internal_minimum = convex_degree_minimum(k, s * t_min)
                internal_maximum = convex_degree_maximum(k, degree_cap, s * t_min)
                external_minimum = convex_degree_minimum(
                    complement_size, blocking_order * t_min
                )
                external_maximum = bounded_degree_maximum(
                    complement_size,
                    2,
                    matching_cap,
                    blocking_order * t_min,
                )
                pair_total = comb(t_min, 2)
                assert max(pair_total - internal_maximum, external_minimum) <= min(
                    pair_total - internal_minimum, external_maximum
                )
        checked_sharp_conjugate_resonance_instances += 1

    resonance_rows = []
    for lam in range(1, RESONANCE_LAMBDA_MAX + 1):
        for u in range(1, lam + 1):
            if lam % u == 0:
                resonance_rows.append(resonance_record(u, lam // u))

    # Recompute the first-order factor-pair expansion from the raw exact
    # balanced pair count, rather than from resonance_record's affine envelope.
    checked_raw_factor_pair_expansions = 0
    for u in range(1, 5):
        for v in range(1, 5):
            d = u + v + 1
            c_env = Fraction(
                u * (u * v * v + 4 * u * v + 2 * u + 2 * v * v + 4 * v + 1),
                2 * u * v + u + v,
            )
            h0 = Fraction(
                -u * (v + 1) * (u * u * v + u * u - v),
                2 * u * v + u + v,
            )
            slope = Fraction(2 * v, (u + v) * (2 * u * v + u + v + 1))
            scale = Fraction((u + v) * (2 * u * v + u + v + 1), 2)
            c_floor = c_env.numerator // c_env.denominator
            h_floor = h0.numerator // h0.denominator
            for n in (257, 509):
                q = d * n
                s = (u + 1) * n + 1
                point_count = q * q + q + 1
                for coefficient in range(c_floor, c_floor + 3):
                    k = u * d * n * n + coefficient * n
                    complement_size = point_count - k
                    for h in range(h_floor - 2, h_floor + 3):
                        t = u * d * (v + 1) * n + h
                        if u * v * complement_size > v * n * t:
                            continue
                        exact = (
                            convex_degree_minimum(k, s * t)
                            + convex_degree_minimum(complement_size, v * n * t)
                            - comb(t, 2)
                        )
                        predicted_per_n = scale * (
                            c_env + slope * (h - h0) - coefficient
                        )
                        error = abs(Fraction(exact, n) - predicted_per_n)
                        # The omitted terms are uniformly O(1/n) before this
                        # normalization.  On this declared finite domain the
                        # maximum normalized remainder is 1916/257 < 8.
                        assert error < 8, (u, v, n, coefficient, h, error)
                        checked_raw_factor_pair_expansions += 1

    known_resonances = {(row["u"], row["v"]): row for row in resonance_rows}
    assert known_resonances[(1, 1)]["lattice_envelope_coefficient"] == fraction_record(
        Fraction(18, 5)
    )
    assert known_resonances[(1, 2)]["lattice_envelope_coefficient"] == fraction_record(
        Fraction(9, 2)
    )
    assert known_resonances[(2, 1)]["lattice_envelope_coefficient"] == fraction_record(
        Fraction(6)
    )
    assert known_resonances[(2, 1)]["conditional_modular_lift_support"]["1"][
        "coefficient"
    ] == fraction_record(Fraction(73, 12))
    assert known_resonances[(2, 1)]["conditional_modular_lift_support"]["2"][
        "coefficient"
    ] == fraction_record(Fraction(37, 6))
    assert known_resonances[(1, 1)]["conditional_residue_aware_modular_lift"] == {
        "characteristic": 3,
        "coefficient": fraction_record(Fraction(4)),
        "minimizing_h": 0,
        "minimum_support_at_minimizer": 1,
        "gain_over_lattice_envelope": fraction_record(Fraction(2, 5)),
    }
    assert known_resonances[(2, 1)]["conditional_residue_aware_modular_lift"] == {
        "characteristic": 2,
        "coefficient": fraction_record(Fraction(73, 12)),
        "minimizing_h": -3,
        "minimum_support_at_minimizer": 1,
        "gain_over_lattice_envelope": fraction_record(Fraction(1, 12)),
    }

    # Exact zero-core falsifier for (OF3), independent of the displayed
    # first-order slack calculation.  An exact 1 mod 3 selected-line set puts
    # both degree sequences in the residue class 1.  Every arithmetically
    # admissible bounded offset below coefficient four violates the pair count.
    checked_of3_zero_core_instances = 0
    for n in (9, 27, 81, 243):
        q = 3 * n
        s = 2 * n + 1
        point_count = q * q + q + 1
        for coefficient in range(-2, 4):
            for constant in range(-3, 4):
                k = 3 * n * n + coefficient * n + constant
                complement_size = point_count - k
                for h in range(-12, 13):
                    t = 6 * n + h
                    if t < 0 or n * t < complement_size:
                        continue
                    internal = congruence_degree_minimum(k, s * t, 3, 1)
                    external = congruence_degree_minimum(
                        complement_size, n * t, 3, 1, lower=1
                    )
                    if internal is None or external is None:
                        continue
                    assert internal + external > comb(t, 2)
                    checked_of3_zero_core_instances += 1

    # Exact empty-repair falsifier for the first characteristic-two core.
    # Internal degrees are even and external completeness degrees are even and
    # at least two.  The finite checks mirror the asymptotic C>=16 obstruction.
    checked_pf_zero_core_instances = 0
    for m in (16, 32, 64, 128):
        q = 8 * m
        s = 6 * m + 1
        point_count = q * q + q + 1
        for coefficient in range(16):
            for constant in range(-4, 5):
                k = 32 * m * m + coefficient * m + constant
                complement_size = point_count - k
                for h in range(-16, 17):
                    t = 32 * m + h
                    if t < 0 or 2 * m * t < 2 * complement_size:
                        continue
                    internal = congruence_degree_minimum(k, s * t, 2, 0)
                    external = congruence_degree_minimum(
                        complement_size, 2 * m * t, 2, 0, lower=2
                    )
                    if internal is None or external is None:
                        continue
                    assert internal + external > comb(t, 2)
                    checked_pf_zero_core_instances += 1

    # On the ordinary (u,v)=(1,1) branch, an exact 1 mod 3 selected-line
    # multiset pays D+E beyond the unrestricted pair minimum.  Its coefficient
    # exceeds the entire available slack by 9, independently of C and H.
    for coefficient_numerator in range(15, 26):
        coefficient = Fraction(coefficient_numerator, 5)
        for h in range(-6, 7):
            unrestricted_slack = 5 * coefficient - h - 18
            mod_three_surcharge = 5 * coefficient - h - 9
            assert mod_three_surcharge - unrestricted_slack == 9
    checked_diagonal_double_tight_instances = 0
    for u in range(2, 65, 2):
        assert resonance_record(u, u)["double_tight"]
        checked_diagonal_double_tight_instances += 1

    # The first characteristic-compatible double-tight branch is (u,v)=(2,1).
    # For q=8m its stable exact paired threshold has T=4q-4 once m>=13.
    checked_cf_dual_threshold_instances = 0
    for m in range(13, 65):
        q = 8 * m
        s = 6 * m + 1
        k = 32 * m * m + 12 * m + 1
        complement_size = q * q + q + 1 - k
        blocking_order = q + 1 - s
        t_min = (2 * complement_size + blocking_order - 1) // blocking_order
        assert t_min == 4 * q - 4
        internal_degree_sum = s * t_min
        external_degree_sum = blocking_order * t_min
        assert external_degree_sum == 2 * complement_size
        assert 6 * k - internal_degree_sum == 8 * q + 10
        pair_slack = (
            comb(t_min, 2)
            - convex_degree_minimum(k, internal_degree_sum)
            - convex_degree_minimum(complement_size, external_degree_sum)
        )
        assert pair_slack == 45
        checked_cf_dual_threshold_instances += 1

    # A four-line symmetric difference with exactly three concurrent lines has
    # the stated spectrum.  In particular q^2-O(q) lines are 4-secants, so no
    # bounded point edit can have almost all line characters in {2,6}.
    checked_four_line_even_type_instances = 0
    for q in range(8, 129):
        spectrum = {2: 4 * q - 5, 4: q * q - 3 * q + 2, q - 2: 1, q: 3}
        line_count = sum(spectrum.values())
        first_moment = sum(j * count for j, count in spectrum.items())
        second_moment = sum(comb(j, 2) * count for j, count in spectrum.items())
        set_size = 4 * q - 4
        assert line_count == q * q + q + 1
        assert first_moment == set_size * (q + 1)
        assert second_moment == comb(set_size, 2)
        checked_four_line_even_type_instances += 1

    # An exact {2,6}-set would satisfy a quadratic whose discriminant is
    # (q+32)^2-1008.  The positive integral orders are therefore finite.
    exact_two_six_orders = []
    for q in range(1, 1009):
        discriminant = q * q + 64 * q + 16
        root = isqrt(discriminant)
        if root * root == discriminant:
            exact_two_six_orders.append(q)
    assert exact_two_six_orders == [1, 5, 11, 16, 35, 55, 96, 221]
    assert [q for q in exact_two_six_orders if q & (q - 1) == 0] == [1, 16]

    odd_parity_candidates = [
        (max(Fraction(76 + h, 6), Fraction(9 - h)), h)
        for h in range(-101, 102, 2)
    ]
    even_parity_candidates = [
        (max(Fraction(76 + h, 6), Fraction(10 - h)), h)
        for h in range(-100, 101, 2)
    ]
    odd_parity_minimum = min(odd_parity_candidates)
    even_parity_minimum = min(even_parity_candidates)
    assert odd_parity_minimum == (Fraction(73, 6), -3)
    assert even_parity_minimum == (Fraction(37, 3), -2)

    # Pointwise shell checks for the sharp three-line compression.  These
    # finite ranges are falsifiers only; the manuscript proves the inequalities
    # for all relevant integers by residue classes.
    line_code_shell_checks = 0
    for on_arc, maximum_u in ((True, 4), (False, 0)):
        for u in range(-100, maximum_u + 1):
            residue = u % 3
            z = 0 if residue == 0 else (1 if residue == 1 else -1)
            shell = u * (u - 1) // 2 if on_arc else u * (u + 1) // 2
            lhs = 2 * int(on_arc) * u - shell - u
            assert lhs <= int(z != 0)
            norm_correction = (u * u - z * z) - (u - z)
            assert norm_correction >= 0
            if not on_arc and z == 1:
                assert norm_correction >= 6
            if on_arc:
                assert u <= shell + int(z != 0)
            else:
                assert shell >= int(z == 1)
            if lhs == int(z != 0):
                degree = 1 + 3 * int(on_arc) - u
                if z == 1:
                    assert degree == 3
                elif z == -1:
                    assert degree == 2
                else:
                    assert degree in (1, 4)
            line_code_shell_checks += 1

    shell_collapse_checks = 0
    for r in (3, 9, 27, 81, 243):
        for delta in range(-2 * r, 2 * r + 1, max(1, r // 3)):
            for j in range(-8, 13):
                total = (9 - 3 * j) * r + 3 * delta - j + 1
                internal = (10 - 2 * j) * r + 4 * delta - j
                shell = Fraction((2 - j) * r + 1 + 5 * delta) + Fraction(j * (j - 7), 2)
                collapsed = 2 * internal - shell - total
                assert collapsed == 9 * r - Fraction((j - 1) * (j - 4), 2)
                shell_collapse_checks += 1

    phase_boundary_checks = 0
    for line_count in range(3, 12):
        boundary = Fraction(line_count - 1, 6)
        assert line_count <= 1 + 6 * boundary
        assert boundary >= Fraction(1, 3)
        phase_boundary_checks += 1

    # Exact arithmetic ledger at displacement q/3.  The manuscript supplies
    # the projective-geometric exclusions; this independently checks the
    # finite signed rows, support-equality degrees, pencil equations, and two
    # terminal cap gaps.
    endpoint_candidates = []
    for secant_offset in range(-2, 8):
        for coefficient_sum in (-3, -1, 1, 3):
            if coefficient_sum % 3 != (1 - secant_offset) % 3:
                continue
            positive_lines = (3 + coefficient_sum) // 2
            norm_surplus = 7 - secant_offset
            sum_correction = 4 - secant_offset - coefficient_sum
            if (
                secant_offset >= 1 + positive_lines
                and abs(sum_correction) <= norm_surplus
            ):
                endpoint_candidates.append((secant_offset, coefficient_sum))
    assert endpoint_candidates == [
        (1, -3), (2, -1), (3, 1),
        (4, -3), (4, 3), (5, -1), (7, -3),
    ]

    endpoint_rows = [
        row for row in endpoint_candidates if row != (7, -3)
    ]
    assert endpoint_rows == [
        (1, -3), (2, -1), (3, 1), (4, -3), (4, 3), (5, -1)
    ]

    endpoint_triangle_support_rows = []
    for secant_offset, coefficient_sum in endpoint_rows:
        support_offset = 0 if abs(coefficient_sum) == 3 else -2
        lower_offset = -((secant_offset - 1) * (secant_offset - 4) // 2)
        if support_offset >= lower_offset:
            endpoint_triangle_support_rows.append((secant_offset, coefficient_sum))
    assert endpoint_triangle_support_rows == [
        (1, -3), (4, -3), (4, 3), (5, -1)
    ]

    endpoint_triangle_rows = [(4, -3), (5, -1)]
    endpoint_connector_degrees = {
        "(4, -3)": [3, 3, 3],
        "(5, -1)": [4, 4, 3],
    }
    assert endpoint_connector_degrees == {
        "(4, -3)": [3, 3, 3],
        "(5, -1)": [4, 4, 3],
    }

    endpoint_field_rows = []
    for q in (81, 243, 729):
        r = q // 3
        assert not any(6 == 3 + q * y for y in (0, 1))
        assert not any(4 == 7 + q * (y - 1) for y in (0, 1))
        assert [y for y in (0, 1) if 6 == 6 + q * y] == [0]
        assert [
            (y, connector_sum)
            for y in (0, 1)
            for connector_sum in (2, 5, 8)
            if connector_sum == 8 + q * (y - 1)
        ] == [(1, 8)]
        assert [y for y in (0, 1) if 7 == 7 + q * y] == [0]
        all_negative_gap = (2 * q - 4) - (2 * (q - 5) + 3)
        assert all_negative_gap == 3
        degree_four_count = q * (q + 2) // 3 + 2
        assert degree_four_count > 0
        n = 2 * r + 1
        mixed_cap_gaps = []
        for tangent_count in (0, 1):
            selected_degree_three = n + tangent_count
            selected_on_positive_generator = selected_degree_three - 1 + 2
            mixed_cap_gaps.append(selected_on_positive_generator - n)
        assert mixed_cap_gaps == [1, 2]
        endpoint_field_rows.append(
            {
                "q": q,
                "delta": r,
                "all_negative_gap": all_negative_gap,
                "mixed_degree_four_count": degree_four_count,
                "mixed_positive_generator_cap_gaps": mixed_cap_gaps,
            }
        )

    centered_moment_rows = []
    for q in (81, 243, 729):
        r = q // 3
        centered_moment_rows.append(
            {
                "q": q,
                "branches": [
                    {
                        "T": 6 * r,
                        "sum_u": 9 * r + 1,
                        "norm_u": 15 * r + 1,
                        "shell_defect": 2 * r + 1,
                    },
                    {
                        "T": 6 * r + 1,
                        "sum_u": 6 * r,
                        "norm_u": 12 * r - 6,
                        "shell_defect": r - 2,
                    },
                ],
            }
        )
        for branch in centered_moment_rows[-1]["branches"]:
            assert branch["norm_u"] < (isqrt(q) + 1) * (q + 1 - isqrt(q))

    rows = []
    for q in Q_VALUES:
        for s in range(2, min(8, q) + 1):
            for lam in LAMBDA_VALUES:
                first = first_moment_minimum(q, s, lam)
                second = second_moment_minimum(q, s, lam)
                spectral = spectral_minimum(q, s, lam)
                paired = paired_moment_minimum(q, s, lam)
                paired_spectral = paired_moment_minimum(q, s, lam, spectral=True)
                assert second is None or second >= first
                assert spectral is None or spectral >= s + 1
                hybrid = None if second is None or spectral is None else max(second, spectral)
                assert paired is None or hybrid is None or paired >= hybrid
                assert paired_spectral == paired
                rows.append(
                    {
                        "q": q,
                        "s": s,
                        "lambda": lam,
                        "first_moment_minimum": first,
                        "second_moment_minimum": second,
                        "spectral_minimum": spectral,
                        "hybrid_minimum": hybrid,
                        "paired_moment_minimum": paired,
                        "paired_spectral_minimum": paired_spectral,
                        "improvement": None if second is None else second - first,
                        "excluded_through_universal_arc_maximum": second is None,
                    }
                )

    wide_degree_rows = []
    for q in WIDE_DEGREE_Q_VALUES:
        for s in range(2, q + 1):
            for lam in LAMBDA_VALUES:
                second = second_moment_minimum(q, s, lam)
                spectral = spectral_minimum(q, s, lam)
                hybrid = None if second is None or spectral is None else max(second, spectral)
                paired = paired_moment_minimum(q, s, lam)
                wide_degree_rows.append(
                    {
                        "q": q,
                        "s": s,
                        "lambda": lam,
                        "hybrid_minimum": hybrid,
                        "paired_moment_minimum": paired,
                        "gain_over_hybrid": None
                        if paired is None or hybrid is None
                        else paired - hybrid,
                        "degree_regime": "below_sqrt_q"
                        if s * s < q
                        else ("intermediate" if 2 * s < q else "at_least_half_q"),
                    }
                )

    return {
        "schema": "integral-secant-checks-v1",
        "meaning": "Necessary-bound thresholds only; projective-plane or arc existence is not asserted.",
        "parameters": {"lambda_values": list(LAMBDA_VALUES), "holes": 0, "q_values": list(Q_VALUES), "s_max": 8},
        "independent_checks": {
            "convex_envelope_instances": checked_envelopes,
            "congruence_envelope_instances": checked_congruence_envelopes,
            "bounded_convex_envelope_instances": checked_bounded_envelopes,
            "ordinary_arc_specializations": checked_arc_specializations,
            "spectral_quadratic_equivalences": checked_spectral_equivalences,
            "infinite_family_formula_instances": checked_infinite_family_instances,
            "ordinary_resonance_formula_instances": checked_ordinary_resonance_instances,
            "conjugate_resonance_bound_instances": checked_conjugate_resonance_instances,
            "sharp_conjugate_resonance_instances": checked_sharp_conjugate_resonance_instances,
            "factor_pair_resonance_instances": len(resonance_rows),
            "raw_factor_pair_expansion_instances": checked_raw_factor_pair_expansions,
            "of3_zero_core_instances": checked_of3_zero_core_instances,
            "pf_zero_core_instances": checked_pf_zero_core_instances,
            "diagonal_double_tight_instances": checked_diagonal_double_tight_instances,
            "cf_dual_threshold_instances": checked_cf_dual_threshold_instances,
            "four_line_even_type_spectrum_instances": checked_four_line_even_type_instances,
            "exact_two_six_integral_orders": exact_two_six_orders,
            "line_code_pointwise_shell_instances": line_code_shell_checks,
            "line_code_shell_collapse_instances": shell_collapse_checks,
            "line_code_phase_boundary_instances": phase_boundary_checks,
            "line_code_endpoint_candidate_rows": len(endpoint_candidates),
            "line_code_endpoint_field_instances": len(endpoint_field_rows),
        },
        "factor_pair_resonances": resonance_rows,
        "cf_parity_asymptotic": {
            "odd_selected_line_count": {
                "coefficient": fraction_record(odd_parity_minimum[0]),
                "offset": odd_parity_minimum[1],
            },
            "even_selected_line_count": {
                "coefficient": fraction_record(even_parity_minimum[0]),
                "offset": even_parity_minimum[1],
            },
        },
        "characteristic_three_line_code": {
            "sharp_displacement": fraction_record(Fraction(1, 3)),
            "support_invariant": "t>=3",
            "signed_capacity_invariant": "t<=1+6*alpha+o(1)",
            "consequence": "alpha>=1/3-o(1)",
            "centered_moment_rows": centered_moment_rows,
            "exact_endpoint": {
                "candidate_rows": [list(row) for row in endpoint_rows],
                "triangle_support_rows": [
                    list(row) for row in endpoint_triangle_support_rows
                ],
                "triangular_survivors": [list(row) for row in endpoint_triangle_rows],
                "connector_degrees": endpoint_connector_degrees,
                "field_rows": endpoint_field_rows,
            },
        },
        "rows": rows,
        "wide_degree_rows": wide_degree_rows,
    }


def canonical_bytes(payload: dict[str, object]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def checksum_line(path: Path, data: bytes) -> str:
    return f"{hashlib.sha256(data).hexdigest()}  {path.name}\n"


def generate() -> None:
    payload_bytes = canonical_bytes(run_checks())
    OUTPUT.write_bytes(payload_bytes)
    script_bytes = Path(__file__).read_bytes()
    CHECKSUMS.write_text(
        checksum_line(Path(__file__), script_bytes) + checksum_line(OUTPUT, payload_bytes),
        encoding="utf-8",
    )


def check() -> None:
    expected = canonical_bytes(run_checks())
    if OUTPUT.read_bytes() != expected:
        raise SystemExit("generated JSON is stale")
    expected_manifest = checksum_line(Path(__file__), Path(__file__).read_bytes()) + checksum_line(OUTPUT, expected)
    if CHECKSUMS.read_text(encoding="utf-8") != expected_manifest:
        raise SystemExit("checksum manifest is stale")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("generate", "check"))
    args = parser.parse_args()
    if args.mode == "generate":
        generate()
    else:
        check()


if __name__ == "__main__":
    main()
