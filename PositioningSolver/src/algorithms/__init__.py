# general info for each estimation algorithm available
__algorithms_description__ = {
    0: {
        "code": "gnss_spp",
        "description": "GNSS Single Point Positioning"
    },

    1: {
        "code": "gnss_plots",
        "description": "Plotting GNSS PVT results"
    }
}

# Mandatory configuration tags
__algorithms_config_info__ = {
    "gnss_spp": {"inputs": "rinex_obs_dir_path"},
}
