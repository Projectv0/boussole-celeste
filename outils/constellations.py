"""Les douze constellations du zodiaque, en coordonnées réelles simplifiées.

Chaque étoile : (nom, ascension droite en heures, déclinaison en degrés, magnitude).
Les tracés relient les étoiles principales, selon les figures usuelles des cartes du ciel,
allégées pour rester lisibles en petit. Sert aux planches de DA, aux vignettes du site,
à la roue des résultats, aux cartes à partager et aux icônes : une seule source.

    from constellations import CONSTELLATIONS, projeter
    pts, traits = projeter("lion", largeur, hauteur, marge)
"""
import math

CONSTELLATIONS = {
    "belier": {
        "etoiles": [("alpha", 2.1196, 23.4625, 2.00), ("beta", 1.9107, 20.8080, 2.64),
                    ("gamma", 1.8923, 19.2939, 3.88), ("41", 2.8330, 27.2605, 3.61)],
        "traits": [("gamma", "beta"), ("beta", "alpha"), ("alpha", "41")],
    },
    "taureau": {
        "etoiles": [("alpha", 4.5987, 16.5093, 0.85), ("beta", 5.4382, 28.6074, 1.65),
                    ("zeta", 5.6274, 21.1426, 3.00), ("theta2", 4.4782, 15.8709, 3.40),
                    ("gamma", 4.3299, 15.6276, 3.65), ("delta1", 4.3825, 17.5426, 3.76),
                    ("epsilon", 4.4769, 19.1804, 3.53), ("lambda", 4.0110, 12.4903, 3.47),
                    ("eta", 3.7914, 24.1051, 2.87)],
        "traits": [("lambda", "gamma"), ("gamma", "delta1"), ("delta1", "epsilon"),
                   ("epsilon", "beta"), ("gamma", "theta2"), ("theta2", "alpha"), ("alpha", "zeta")],
    },
    "gemeaux": {
        "etoiles": [("alpha", 7.5767, 31.8883, 1.58), ("beta", 7.7553, 28.0262, 1.14),
                    ("gamma", 6.6285, 16.3993, 1.92), ("epsilon", 6.7322, 25.1311, 2.98),
                    ("mu", 6.3827, 22.5136, 2.87), ("eta", 6.2479, 22.5068, 3.31),
                    ("delta", 7.3354, 21.9823, 3.53), ("zeta", 7.0685, 20.5703, 3.93),
                    ("tau", 7.1857, 30.2452, 4.41), ("kappa", 7.7406, 24.3980, 3.57),
                    ("iota", 7.4287, 27.7981, 3.78), ("upsilon", 7.5980, 26.8957, 4.06)],
        "traits": [("alpha", "tau"), ("tau", "epsilon"), ("epsilon", "mu"), ("mu", "eta"),
                   ("beta", "upsilon"), ("upsilon", "delta"), ("delta", "zeta"), ("zeta", "gamma"),
                   ("tau", "iota"), ("iota", "upsilon"), ("beta", "kappa")],
    },
    "cancer": {
        "etoiles": [("alpha", 8.9748, 11.8577, 4.26), ("beta", 8.2753, 9.1855, 3.52),
                    ("delta", 8.7448, 18.1543, 3.94), ("gamma", 8.7215, 21.4685, 4.66),
                    ("iota", 8.7781, 28.7600, 4.02)],
        "traits": [("beta", "delta"), ("delta", "alpha"), ("delta", "gamma"), ("gamma", "iota")],
    },
    "lion": {
        "etoiles": [("alpha", 10.1395, 11.9672, 1.35), ("beta", 11.8177, 14.5721, 2.14),
                    ("gamma", 10.3329, 19.8415, 2.08), ("delta", 11.2351, 20.5237, 2.56),
                    ("theta", 11.2373, 15.4296, 3.33), ("eta", 10.1222, 16.7627, 3.48),
                    ("zeta", 10.2782, 23.4173, 3.44), ("mu", 9.8794, 26.0070, 3.88),
                    ("epsilon", 9.7642, 23.7743, 2.98)],
        "traits": [("alpha", "eta"), ("eta", "gamma"), ("gamma", "zeta"), ("zeta", "mu"),
                   ("mu", "epsilon"), ("gamma", "delta"), ("delta", "beta"), ("beta", "theta"),
                   ("theta", "alpha"), ("delta", "theta")],
    },
    "vierge": {
        "etoiles": [("alpha", 13.4199, -11.1613, 0.97), ("gamma", 12.6943, -1.4494, 2.74),
                    ("epsilon", 13.0363, 10.9592, 2.83), ("delta", 12.9267, 3.3975, 3.38),
                    ("zeta", 13.5783, -0.5958, 3.37), ("beta", 11.8449, 1.7647, 3.61),
                    ("eta", 12.3317, -0.6668, 3.89), ("theta", 13.1658, -5.5390, 4.38),
                    ("iota", 14.2669, -6.0005, 4.08), ("mu", 14.7177, -5.6582, 3.88),
                    ("109", 14.7703, 1.8929, 3.72)],
        "traits": [("beta", "eta"), ("eta", "gamma"), ("gamma", "delta"), ("delta", "epsilon"),
                   ("gamma", "theta"), ("theta", "alpha"), ("delta", "zeta"), ("zeta", "iota"),
                   ("iota", "mu"), ("zeta", "109")],
    },
    "balance": {
        "etoiles": [("alpha", 14.8480, -16.0418, 2.75), ("beta", 15.2834, -9.3829, 2.61),
                    ("sigma", 15.0678, -25.2820, 3.29), ("gamma", 15.5921, -14.7895, 3.91),
                    ("upsilon", 15.6170, -28.1350, 3.58), ("tau", 15.6447, -29.7778, 3.66)],
        "traits": [("alpha", "beta"), ("beta", "gamma"), ("gamma", "alpha"), ("alpha", "sigma"),
                   ("gamma", "upsilon"), ("upsilon", "tau")],
    },
    "scorpion": {
        "etoiles": [("alpha", 16.4901, -26.4320, 1.06), ("beta", 16.0906, -19.8055, 2.62),
                    ("delta", 16.0056, -22.6217, 2.29), ("pi", 15.9809, -26.1141, 2.89),
                    ("sigma", 16.3531, -25.5928, 2.89), ("tau", 16.5980, -28.2160, 2.82),
                    ("epsilon", 16.8361, -34.2932, 2.29), ("mu", 16.8645, -38.0474, 3.00),
                    ("zeta", 16.9097, -42.3613, 3.62), ("eta", 17.2025, -43.2392, 3.33),
                    ("theta", 17.6219, -42.9978, 1.86), ("iota", 17.7931, -40.1270, 2.99),
                    ("kappa", 17.7081, -39.0300, 2.39), ("lambda", 17.5601, -37.1038, 1.62),
                    ("upsilon", 17.5127, -37.2958, 2.70)],
        "traits": [("beta", "delta"), ("delta", "pi"), ("delta", "sigma"), ("sigma", "alpha"),
                   ("alpha", "tau"), ("tau", "epsilon"), ("epsilon", "mu"), ("mu", "zeta"),
                   ("zeta", "eta"), ("eta", "theta"), ("theta", "iota"), ("iota", "kappa"),
                   ("kappa", "lambda"), ("lambda", "upsilon")],
    },
    "sagittaire": {
        "etoiles": [("epsilon", 18.4029, -34.3846, 1.85), ("sigma", 18.9211, -26.2967, 2.05),
                    ("zeta", 19.0435, -29.8801, 2.60), ("delta", 18.3499, -29.8281, 2.70),
                    ("lambda", 18.4662, -25.4217, 2.81), ("gamma", 18.0968, -30.4241, 2.98),
                    ("phi", 18.7609, -26.9908, 3.17), ("tau", 19.1157, -27.6704, 3.32),
                    ("eta", 18.2938, -36.7617, 3.11)],
        "traits": [("gamma", "delta"), ("gamma", "epsilon"), ("delta", "epsilon"), ("delta", "lambda"),
                   ("lambda", "phi"), ("delta", "phi"), ("phi", "sigma"), ("sigma", "tau"),
                   ("tau", "zeta"), ("zeta", "phi"), ("zeta", "epsilon"), ("epsilon", "eta")],
    },
    "capricorne": {
        "etoiles": [("delta", 21.7840, -16.1273, 2.85), ("beta", 20.3502, -14.7814, 3.05),
                    ("alpha", 20.3001, -12.5449, 3.57), ("gamma", 21.6682, -16.6623, 3.69),
                    ("theta", 21.0992, -17.2329, 4.07), ("omega", 20.8638, -26.9191, 4.12),
                    ("psi", 20.7684, -25.2709, 4.13), ("zeta", 21.4444, -22.4113, 3.74),
                    ("iota", 21.3709, -16.8345, 4.28)],
        "traits": [("alpha", "beta"), ("beta", "psi"), ("psi", "omega"), ("omega", "zeta"),
                   ("zeta", "delta"), ("delta", "gamma"), ("gamma", "iota"), ("iota", "theta"),
                   ("theta", "beta")],
    },
    "verseau": {
        "etoiles": [("beta", 21.5260, -5.5712, 2.87), ("alpha", 22.0964, -0.3199, 2.95),
                    ("delta", 22.9108, -15.8208, 3.27), ("zeta", 22.4807, -0.0200, 3.65),
                    ("gamma", 22.3609, -1.3873, 3.84), ("eta", 22.5893, -0.1175, 4.04),
                    ("pi", 22.4214, 1.3774, 4.66), ("lambda", 22.8769, -7.5796, 3.74),
                    ("epsilon", 20.7946, -9.4958, 3.77), ("theta", 22.2806, -7.7833, 4.16),
                    ("tau", 22.8265, -13.5925, 4.01), ("88", 23.1574, -21.1724, 3.66),
                    ("phi", 23.2384, -6.0487, 4.22)],
        "traits": [("epsilon", "beta"), ("beta", "alpha"), ("alpha", "gamma"), ("gamma", "zeta"),
                   ("zeta", "eta"), ("zeta", "pi"), ("alpha", "theta"), ("theta", "lambda"),
                   ("lambda", "phi"), ("lambda", "tau"), ("tau", "delta"), ("delta", "88")],
    },
    "poissons": {
        "etoiles": [("alpha", 2.0340, 2.7638, 3.82), ("eta", 1.5247, 15.3458, 3.62),
                    ("gamma", 23.2858, 3.2823, 3.69), ("omega", 23.9886, 6.8633, 4.03),
                    ("iota", 23.6658, 5.6263, 4.13), ("theta", 23.4661, 6.3790, 4.27),
                    ("lambda", 23.7004, 1.7800, 4.49), ("kappa", 23.4489, 1.2556, 4.94),
                    ("epsilon", 1.0491, 7.8901, 4.27), ("delta", 0.8114, 7.5851, 4.43),
                    ("nu", 1.6905, 5.4876, 4.44), ("mu", 1.5032, 6.1438, 4.84),
                    ("omicron", 1.7566, 9.1577, 4.26), ("tau", 1.1944, 30.0897, 4.51),
                    ("upsilon", 1.3244, 27.2641, 4.74), ("phi", 1.2290, 24.5837, 4.67),
                    ("beta", 23.0629, 3.8200, 4.48)],
        "traits": [("beta", "gamma"), ("gamma", "theta"), ("theta", "iota"), ("iota", "lambda"),
                   ("lambda", "kappa"), ("kappa", "gamma"), ("iota", "omega"), ("omega", "delta"),
                   ("delta", "epsilon"), ("epsilon", "mu"), ("mu", "nu"), ("nu", "alpha"),
                   ("alpha", "omicron"), ("omicron", "eta"), ("eta", "phi"), ("phi", "upsilon"),
                   ("upsilon", "tau")],
    },
}

ORDRE = ["belier", "taureau", "gemeaux", "cancer", "lion", "vierge",
         "balance", "scorpion", "sagittaire", "capricorne", "verseau", "poissons"]


def _plan(etoiles):
    """Projection locale : ciel vu de face (l'est à gauche), déclinaison vers le haut."""
    ras = [e[1] for e in etoiles]
    if max(ras) - min(ras) > 12:  # la figure chevauche 0 h (Poissons)
        etoiles = [(n, ra + 24 if ra < 12 else ra, d, m) for n, ra, d, m in etoiles]
    ra0 = sum(e[1] for e in etoiles) / len(etoiles)
    de0 = sum(e[2] for e in etoiles) / len(etoiles)
    k = math.cos(math.radians(de0))
    return {n: (-(ra - ra0) * 15 * k, -(d - de0), m) for n, ra, d, m in etoiles}


def projeter(signe, w, h, marge=0.1):
    """Points {nom: (x, y, rayon relatif 0-1)} et traits [(xa, ya, xb, yb)], cadrés dans w × h."""
    c = CONSTELLATIONS[signe]
    p = _plan(c["etoiles"])
    xs = [v[0] for v in p.values()]
    ys = [v[1] for v in p.values()]
    lx, ly = (max(xs) - min(xs)) or 1, (max(ys) - min(ys)) or 1
    e = min(w * (1 - 2 * marge) / lx, h * (1 - 2 * marge) / ly)
    ox = (w - lx * e) / 2 - min(xs) * e
    oy = (h - ly * e) / 2 - min(ys) * e
    pts = {}
    for n, (x, y, m) in p.items():
        r = max(0.25, min(1.0, (5.2 - m) / 4.2))  # magnitude 1 → 1, magnitude 5 → 0,25
        pts[n] = (ox + x * e, oy + y * e, r)
    traits = [(pts[a][0], pts[a][1], pts[b][0], pts[b][1]) for a, b in c["traits"]]
    return pts, traits
