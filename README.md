PositioningSolver
======

This is an educational project about GNSS positioning algorithms. It is intended for all people giving their first steps
in these kind of algorithms. The idea here is to explore the positioning algorithms, simulating common procedures and practises
used in the industry.

Currently, the only algorithm implemented is:

- GPS Single Point Positioning (SPP).

SPP is the most basic GNSS positioning solution, using just data from one GPS receiver available at real time. That is,
to implement an SPP solver we need:

- GPS observational data (raw observables - pseudorange and carrier phase)
- GPS navigational data (navigation message with information about the satellites, atmosphere, ...)

Observational data is provided through RINEX Observation files, and navigational data through RINEX navigational files.
The RINEX is a standard (widely-used) format to exchange GNSS data. Learn more about the RINEX format in

- [GNSS Data Formats.pdf](Theory/gnss/GNSS%20Data%20Formats.pdf)
- [RINEX 303.pdf](Theory/gnss/RINEX%20303.pdf)


GPS transmits data in 3 frequency bands (L1, L2 and L5 bands). Currently, this software only permits the use of L1/L2 data.
The following models to the GPS SPP solution are available:

- Single Frequency Estimation:
    - L1 Raw Observables
    - L2 Raw Observables
    - Ionospheric-free Observables (L1 + L2 Iono free)

- Dual Frequency Estimation:
    - GPS L1 + L2 (Dual Frequency Estimation)

In the upcoming future, (hopefully) this repository will also perform and explore other algorithms, namely:

- GNSS/INS data fusion. For that, we need to set up an Inertial Navigation System (INS), with
    - Inertial Measurement Unit (IMU) emulation, providing gyroscope and accelerometer readouts
    - GNSS/INS hybridization algorithms (loosely coupled)
    
- Expand the GPS algorithms with PPP and RTK modes
- Allow the processing of other GNSS constellations, namely Galileo


Installation
------------

PositioningSolver has been developed with Python 3.9. It requires [numpy](https://numpy.org/) and [matplotlib](https://matplotlib.org/).

Clone this software to a location of your choice, using:


```console
$ git clone https://github.com/rodrigo-moliveira/PositioningSolver
```


Run
------------

<b>Usage</b>

To run this software, you need to provide the ``algorithm_id`` and the path to the configuration json file(s). 
The main script has the following parameters

```console
$ main.py algorithm_id <path_to_config_file1.json> <path_to_config_file.json2> <...>
```

Note that you can pass multiple json files, each one containing the configuration of a specific scenario. 

___
<b>Table of algorithms</b>


| algorithm_id | Algorithm Name | Description | Configuration File (JSON)
| - | - | - | - |
| 0 | `GNSS Single Point Positioning` | This is the main script to run SPP solver algorithm. | Example: [GPS L1](./workspace/outputs_gnss/gnss_1/spp_1c/config.json) |
| 1 | `Plotting GNSS PVT results` | To plot various PVT results (clock, RMS, DOPs, etc).  | Example: [Scenario GNSS_1 Plots](./workspace/outputs_gnss/gnss_1/plot_config.json) |

I provide two sample datasets: [GNSS 1](./workspace/datasets/gnss_1) and [GNSS 2](./workspace/datasets/gnss_2). For each 
dataset, you can find the corresponding navigation and observation files (in separate folders).

The configuration json files can be found in [GNSS 1](./workspace/outputs_gnss/gnss_1) and [GNSS 2](./workspace/outputs_gnss/gnss_2)
Feel free to add more content, if you want to set your own dataset and run other RINEX data.

You can download observational / navigational data in CDDIS.
The ftp server is this https://cddis.nasa.gov/archive/gnss/data/daily/ (you need to create a free account to access). 


Examples
----------

To run the [GNSS 1](./workspace/datasets/gnss_1) dataset you can use the following pre-configured json config files


L1 data
```console
$ main.py 0  ./workspace/outputs_gnss/gnss_1/spp_1c/config.json
```

L2 data
```console
$ main.py 0  ./workspace/outputs_gnss/gnss_1/spp_2w/config.json
```

Iono Free L1 + L2
```console
$ main.py 0  ./workspace/outputs_gnss/gnss_1/spp_1c_2w_if/config.json
```

Dual Frequency Estimation L1 + L2
```console
$ main.py 0  ./workspace/outputs_gnss/gnss_1/spp_1c_2w_df/config.json
```

When you run these commands, various plots will be produced, containing clock, DOP, position error, sky plots, Root Mean Square error, etc.
If you want to produce plots for all the 4 runs together, you can run the following command:

```console
$ main.py 1 ./workspace/outputs_gnss/gnss_1/plot_config.json
```

Configuration Files
----------

The configuration files are in [json format](https://en.wikipedia.org/wiki/JSON).
To run the ``algorithm 0``, you need to use files with a specific format, 
[like in this example](./workspace/outputs_gnss/gnss_1/spp_1c/config.json)
You can change the parameters, and you have some tuning parameters. They are relatively straightforward, and some additional information is provided in comment sections.

Notably, the following parameters are of note:

- ``model/observations`` - you can select the observations to use (in RINEX format). The selected observations <b>must</b> be available in the provided RINEX file
- ``outputs/output_path`` - you can select the output path. Various files will be produced during the execution of the SPP solver


The following GPS services are allowed (see RINEX 303.pdf file for more info)
```python
GPSAvailableObservations = {'1C', '1S', '1L', '1X', '1P', '1W', '1Y', '1M',
                            '2C', '2D', '2S', '2L', '2X', '2P', '2W', '2Y', '2M'}
```

References
----------
You can find various (open-access) references used to implement this software in
[Theory](./Theory/gnss)