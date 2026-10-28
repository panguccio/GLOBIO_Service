
import gsw
import matplotlib.pyplot as plt


def plot_doxy_comparison(ap_sample: dict, sf_sample: dict):

    # argopy
    valid = ap_sample['PRES_DOXY'].notnull() & ap_sample['DOXY'].notnull()
    ap_doxy = ap_sample["DOXY"].where(valid, drop=True)
    ap_pres = ap_sample["PRES_DOXY"].where(valid, drop=True)

    # superfloat
    sf_doxy = sf_sample["DOXY"]
    sf_pres = sf_sample["PRES_DOXY"]

    # plot fig
    fig, ax = plt.subplots(figsize=(6, 8))
    ax.plot(ap_doxy, ap_pres, color='tab:orange', label='ARGOPY')
    ax.plot(sf_doxy, sf_pres, color='dodgerblue', label='SUPERFLOAT')
    ax.invert_yaxis()
    ax.set_xlabel(r'DOXY (mmol m$^{-3}$)')
    ax.set_ylabel('Pressure (dbar)')
    ax.set_title('Oxygen profile comparison')
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig('DOXY_profile_comparison.png')
