from typing import Dict
import matplotlib.pyplot as plt
import xarray as xr
import os


def plot_comparison(name_profiles: Dict[str, xr.Dataset], attr: str = "DOXY", title: str = ""):
    fig, ax = plt.subplots(figsize=(6, 8))

    for name in name_profiles:
        profile = name_profiles[name]
        valid = profile[f'PRES_{attr}'].notnull() & profile[attr].notnull()
        doxy = profile[attr].loc[valid]
        pres = profile[f'PRES_{attr}'].loc[valid]
        linestyle, linewidth, alpha = '-', 1.6, 0.6
        ax.plot(doxy, pres, label=name, linestyle=linestyle, linewidth=linewidth, alpha=alpha)

    ax.invert_yaxis()
    ax.set_xlabel(rf'{attr} (mmol m$^{-3}$)')
    ax.set_ylabel('Pressure (dbar)')
    ax.set_title(f'{attr} profile comparison')

    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    file_name = f'{title}: {attr} of {"-".join(name_profiles.keys()).lower()}.png'

    save_plot(fig, file_name)


import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
import xarray as xr


def plot_similar_comparison(
    name_profiles: Dict[str, xr.Dataset],
    attr: str = "DOXY",
    title: str = "",
    reference: str = None,
):
    if reference is None: reference = list(name_profiles.keys())[0]
    fig, (ax_abs, ax_diff) = plt.subplots(
        1, 2,
        figsize=(11, 8),
        sharey=True,
        gridspec_kw={"width_ratios": [1.3, 1]}
    )

    # Visual styles
    colors = {
        "STANDARD": "#0072B2",
        "EXPERT": "#D55E00",
        "SUPERFLOAT": "#009E73"
    }

    styles = {
        "STANDARD": "-",
        "EXPERT": "--",
        "SUPERFLOAT": "-."
    }

    # Extract and clean profiles
    profiles = {}

    for name, profile in name_profiles.items():

        x = np.asarray(profile[attr].values).ravel()
        p = np.asarray(profile[f"PRES_{attr}"].values).ravel()

        valid = np.isfinite(x) & np.isfinite(p)
        x, p = x[valid], p[valid]

        # Sort by pressure
        order = np.argsort(p)
        x, p = x[order], p[order]

        # Remove duplicate pressure levels
        p, idx = np.unique(p, return_index=True)
        x = x[idx]

        profiles[name] = (x, p)

    if reference not in profiles:
        raise ValueError(f"Reference '{reference}' not found.")

    # Reference profile
    x_ref, p_ref = profiles[reference]

    # Plot absolute profiles
    for i, (name, (x, p)) in enumerate(profiles.items()):

        color = colors.get(name, f"C{i}")
        linestyle = styles.get(name, "-")

        ax_abs.plot(
            x, p,
            label=name,
            color=color,
            linestyle=linestyle,
            linewidth=2.2,
            marker="o",
            markersize=3,
            markevery=max(1, len(x) // 15),
            zorder=3 if name == reference else 2
        )

    # Plot differences relative to reference
    for i, (name, (x, p)) in enumerate(profiles.items()):

        if name == reference:
            continue

        color = colors.get(name, f"C{i}")

        # Interpolate on reference pressure levels
        x_interp = np.interp(
            p_ref, p, x,
            left=np.nan,
            right=np.nan
        )

        difference = x_interp - x_ref

        ax_diff.plot(
            difference,
            p_ref,
            label=f"{name} - {reference}",
            color=color,
            linewidth=2,
            marker="o",
            markersize=3,
            markevery=max(1, len(p_ref) // 15)
        )

    # Formatting
    ax_abs.invert_yaxis()

    ax_abs.set_xlabel(
        rf"{attr} (mmol m$^{{-3}}$)"
    )
    ax_abs.set_ylabel("Pressure (dbar)")
    ax_abs.set_title("Absolute profiles")

    ax_diff.axvline(
        0,
        color="black",
        linestyle="--",
        linewidth=1,
        alpha=0.7
    )

    ax_diff.set_xlabel(
        rf"$\Delta$ {attr} (mmol m$^{{-3}}$)"
    )
    ax_diff.set_title(f"Differences vs {reference}")

    for ax in (ax_abs, ax_diff):
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.tick_params(direction="in")

    fig.suptitle(
        f"{attr} profile comparison",
        fontsize=14
    )

    fig.tight_layout()

    folder = os.path.join(" vs ".join(list(name_profiles.keys())).lower(), title)

    file_name = (
        f"{title}_{attr}_comparison.png"
        if title else f"{attr}_comparison.png"
    )

    save_plot(fig, file_name, folder)


def save_plot(fig, file_name, folder=""):
    output_dir = os.path.join("graphics/plots", folder)
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, file_name)
    fig.savefig(path)