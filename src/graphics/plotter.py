from pathlib import Path

import matplotlib.pyplot as plt
import xarray as xr

_DIR = Path(__file__).parent / 'plots'

def plot_profiles(profiles: dict[str, xr.Dataset], attr: str = "DOXY", title: str = None):
    title = title or f"{attr.lower()} profiles"

    """Overlay one profile per dataset: value on x, pressure on y (inverted)."""
    fig, ax = plt.subplots(figsize=(6, 8))

    for name, ds in profiles.items():
        pres = ds[f"PRES_{attr}"] if f"PRES_{attr}" in ds else ds["PRES"]
        ax.plot(ds[attr].values, pres.values, label=name)

    ax.invert_yaxis()
    ax.set(xlabel=f"{attr} (mmol m$^{{-3}}$)", ylabel="Pressure (dbar)", title=f"{title}")
    ax.grid(alpha=0.3)
    ax.legend()

    path = unique_path(title)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    plt.show()
    plt.close(fig)


def unique_path(title: str) -> Path:
    """If the file already exists it adds an index."""
    path = _DIR / Path(f"{title}.png")
    candidate, i = path, 1
    while candidate.exists():
        candidate = path.with_stem(f"{path.stem}_{i}")
        i += 1
    return candidate