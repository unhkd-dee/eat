# I/O routines for HOPS ASCII tables
# 2016-10-11 Lindy Blackburn
# 2024-02-26 Updated to use Polars by Iniyan Natarajan

import polars as pl
import datetime
import sys

def condense_formats(fmtlist):
    return map(lambda fmt: fmt if fmt.count('%') <= 1 else "%s", fmtlist)

# from write_fsumm.c
# format of each field in alist/tlist files
fformat_v5 = condense_formats("%1d %s 2 %2d %3d %3d %3d %4d %s %02d%03d-%02d%02d%02d %4d\
 %03d-%02d%02d%02d %3d %-8s %s %c%c %c%02d %2s %4d %6.2f %#5.4g %5.1f %#5.4g %2s %6.3f %8.5f\
 %6.4f %8.3f %4.1f %4.1f %5.1f %5.1f %7.4g %7.4g %06d %02d%02d %8.2f %5.1f %11.8f\
 %13.6f %5.3f %3d %3d\n".replace(' 2 ', ' %d ').strip().split())

fformat_v6 = condense_formats("%1d %s 2 %2d %3d %3d %3d %4d %8s %04d%03d-%02d%02d%02d\
 %4d %03d-%02d%02d%02d %3d %32s %2s %c%c\
 %c%02d %2s %5d\
 %#13.8g %#13.8g %11.6f %#11.6g %2s\
 %+12.9f %+12.9f %11.9f\
 %+11.6f %5.2f %5.2f %6.2f %6.2f %7.4g %7.4g %06d\
 %02d%02d %9.3f %10.6f %11.8f\
 %13.6f %+9.6f %8d %8d %+10.6f %+10.6f %+13.10f\n".replace(' 2 ', ' %d ').strip().split())

tformat_v6 = condense_formats("%1d %4d 3 %8s %4d %03d-%02d%02d%02d %3d %32s\
 %c%c %4d %3s %20s %11s %14s\
 %3d %3d  %c  %c %06d\
 %10.3f %8.3f %+8.3f %2s %7.4f\
 %8.5f %6.4f %9.5f %14s %11s\
  %02d%02d %10.3f %7d\n".replace(' 3 ', ' %d ').strip().split())

# fields for each version of input alist/tlist files
ffields_v5 = [a.strip() for a in """
version,
root_id,
two,
extent_no,
duration,
length,
offset,
expt_no,
scan_id,
procdate,
year,
timetag,
scan_offset,
source,
baseline,
quality,
freq_code,
polarization,
lags,
amp,
snr,
resid_phas,
phase_snr,
datatype,
sbdelay,
mbdelay,
ambiguity,
delay_rate,
ref_elev,
rem_elev,
ref_az,
rem_az,
u,
v,
esdesp,
epoch,
ref_freq,
total_phas,
total_rate,
total_mbdelay,
total_sbresid,
srch_cotime,
noloss_cotime
""".split(',')]

ffields_v6 = [a.strip() for a in """
version,
root_id,
two,
extent_no,
duration,
length,
offset,
expt_no,
scan_id,
procdate,
year,
timetag,
scan_offset,
source,
baseline,
quality,
freq_code,
polarization,
lags,
amp,
snr,
resid_phas,
phase_snr,
datatype,
sbdelay,
mbdelay,
ambiguity,
delay_rate,
ref_elev,
rem_elev,
ref_az,
rem_az,
u,
v,
esdesp,
epoch,
ref_freq,
total_phas,
total_rate,
total_mbdelay,
total_sbresid,
srch_cotime,
noloss_cotime,
ra_hrs,
dec_deg,
resid_delay
""".split(',')]

tfields_v6 = [a.strip() for a in """
version,
expt_no,
three,
scan_id,
year,
timetag,
scan_offset,
source,
freq_code,
lags,
triangle,
roots,
extents,
lengths,
duration,
offset,
scanqual,
dataqual,
esdesp,
bis_amp,
bis_snr,
bis_phas,
datatype,
csbdelay,
cmbdelay,
ambiguity,
cdelay_rate,
elevations,
azimuths,
epoch,
ref_freq,
cotime
""".split(',')]

fsumm_v5_polarsargs = dict(columns=ffields_v5,)

fsumm_v6_polarsargs = dict(columns=ffields_v6,)

tsumm_polarsargs = dict(columns=tfields_v6,)

# read alist/tlist files using polars
def read_alist_v5(filename):
    """
    Read alist v5 file into polars dataframe.

    Parameters
    ----------
    filename : str
        alist filename.

    Returns
    -------
    polars.DataFrame
        DataFrame with alist contents.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # skip comment lines and strip whitespaces-- comments start with *
    data = [[val.strip() for val in line.split() if val] for line in lines if line[0] != '*']
    df = pl.DataFrame(data).transpose()
    df.columns = ffields_v5

    return df

def read_alist_v6(filename):
    """
    Read alist v6 file into polars dataframe.

    Parameters
    ----------
    filename : str
        alist filename.

    Returns
    -------
    polars.DataFrame
        DataFrame with alist contents.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # skip comment lines and strip whitespaces-- comments start with *
    data = [[val.strip() for val in line.split() if val] for line in lines if line[0] != '*']
    df = pl.DataFrame(data).transpose()
    df.columns = ffields_v6

    return df

def read_tlist_v6(filename):
    """
    Read tlist v6 file into polars dataframe.

    Parameters
    ----------
    filename : str
        tlist filename.

    Returns
    -------
    polars.DataFrame
        DataFrame with tlist contents.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # skip comment lines and strip whitespaces-- comments start with *
    data = [[val.strip() for val in line.split() if val] for line in lines if line[0] != '*']
    df = pl.DataFrame(data).transpose()
    df.columns = tfields_v6

    return df

# write output dataframe containing alist/tlist to stdout or CSV file
def write_alist(df, out=sys.stdout):
    """
    Write alist dataframe to stdout or CSV file.

    Parameters
    ----------
    df : polars.DataFrame
        DataFrame with alist contents.
    out : str or file object, optional
        Output file. The default is sys.stdout.
    """
    if type(out) is str:
        df.write_csv(out, separator=',', include_header=True)
    else:
        with pl.Config(tbl_rows=df.shape[0], tbl_cols=df.shape[1]):
            print(str(df))

# define aliases for the write functions for compatibility with existing code
write_alist_v5 = write_alist_v6 = write_tlist_v6 = write_alist

def get_alist_version(filename):
    code = (a[0] for a in open(filename) if a[0].isdigit())
    return int(next(code))

# read_alist automatically determine version
# ALIST notes:
# mk4 correlated data will have az,el = 0
# difx correlated data will have az,el != 0, but may still have u,v = 0
def read_alist(filename):
    """
    Read alist file into polars dataframe, automatically determining version (v5 or v6).

    Parameters
    ----------
    filename : str
        alist filename.

    Returns
    -------
    polars.DataFrame
        DataFrame with alist contents.
    """
    ver = get_alist_version(filename)
    if ver == 5:
        df = read_alist_v5(filename)
    elif ver == 6:
        df = read_alist_v6(filename)
    else:
        import sys
        sys.exit('alist is not version 5 or 6')
    return df

# master calibration file from vincent
MASTERCAL_FIELDS = (
    ('dd_hhmm', str), # timetag without seconds
    ('source', str),  # radio source name
    ('len', int),     # length of observation in seconds
    ('el_ap', int),   # Ap APEX -- elevation --
    ('el_az', int),   # Az SMTL
    ('el_sm', int),   # Sm JCMTR
    ('el_cm', int),   # Cm CARMA1L
    ('el_pl', int),   # PL PICOL
    ('el_pb', int),   # PB PDBL
    ('pa_ap', int),   # Ap -- parallactic angle --
    ('pa_az', int),   # Az
    ('pa_sm', int),   # Sm
    ('pa_cm', int),   # Cm
    ('pa_pl', int),   # PL
    ('pa_pb', int),   # PB
    ('smt_tsysl', float),    # -- [S/T] SMT --
    ('smt_tsysr', float),
    ('smt_tau', float),
    ('smalow_sefd', float),  # -- [P/Q] SMA low --
    ('smalow_pheff', float),
    ('smahigh_sefd', float), # -- [P/Q] SMA high --
    ('smahigh_pheff', float),
    ('d_sefd', float),       # -- [D] CARMA Ref LCP --
    ('e_sefd', float),       # -- [E] CARMA Ref RCP --
    ('flow_sefd', float),    # -- [F] CARMA Phased LCP low --
    ('fhigh_sefd', float),   # -- [F] CARMA Phased LCP high --
    ('glow_sefd', float),    # -- [G] CARMA Phased RCP low --
    ('ghigh_sefd', float),   # -- [G] CARMA Phased RCP high --
    ('carma_tau', float),    # -- CARMA --
    ('carma_path', float),
    ('carma_phef', float),
    ('jcmt_tsys', float),    # -- [-/J] JCMT --
    ('jcmt_tau', float),
    ('jcmt_gap', float),
)

mastercal_polarsargs = dict(columns = [a[0] for a in MASTERCAL_FIELDS])

def read_mastercal(filename):
    """
    Read mastercal file into polars dataframe.

    Parameters
    ----------
    filename : str
        mastercal filename.

    Returns
    -------
    polars.DataFrame
        DataFrame with mastercal contents.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # skip comment lines and strip whitespaces -- comments start with #
    data = [[val.strip() for val in line.split() if val] for line in lines if line[0] != '#']
    df = pl.DataFrame(data).transpose()
    df.columns = mastercal_polarsargs['columns']

    return df

# calibrated data table, after calibration amplitdues from alist
CALTABLE_FIELDS = (
    ('day', str), # day
    ('hhmm', str),
    ('source', str),
    ('baseline', str),
    ('u', float),
    ('v', float),
    ('uvmag', float),
    ('sefd_1', float),
    ('sefd_2', float),
    ('calamp', float),
    ('amp', float),
    ('snr', float),
    ('el_1', float),
    ('el_2', float),
    ('expt', int),
    ('band', int),
)

caltablefields = 

caltable_polarsargs = dict(columns = [a[0] for a in CALTABLE_FIELDS])

# calibrated data will have uv filled in
def read_caltable(filename):
    """
    Read caltable file into polars dataframe.

    Parameters
    ----------
    filename : str
        caltable filename.

    Returns
    -------
    polars.DataFrame
        DataFrame with caltable contents.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # skip comment lines and strip whitespaces -- comments start with #
    data = [[val.strip() for val in line.split() if val] for line in lines if line[0] != '#']
    df = pl.DataFrame(data).transpose()
    df.columns = caltable_polarsargs['columns']
    # keep missing data (u,v coords still good)
    # df.dropna(how="any", inplace=True)

    return df

# network solution calibrated data 2013 by Michael
# http://eht-wiki.haystack.mit.edu/Event_Horizon_Telescope_Home/EHT_Data/2013_March/Network_Calibration_Solution/Non-Sgr_A*_Network_Solution
# 1: Day
# 2: HourMinute
# 3: Source
# 4: Baseline (note: "p" and "q" are high-band data for the SMA. I use lowercase because the high-band gains at the SMA are not equal to the low-band gains because they have different phasing efficiencies)
# 5-7: u, v, |{u,v}|
# 8: SEFD_1
# 9: SEFD_2
# 10: a-priori visibility amplitude (from cal_2013)
# 11: visibility amplitude in correlator units
# 12: SNR of visibility amplitude, after incoherent averaging (the thermal noise)
# 13: Elevation_1
# 14: Elevation_2
# 15: Experiment Code
# 16: 0=Low-Band, 1=High-Band
# 17: Gain_1
# 18: Formal Uncertainty in Gain_1 from the network solution
# 19: Gain_2
# 20: Formal Uncertainty in Gain_2 from the network solution
# 21: chi^2 of the visibility after using the network solution (i.e., departure from self-consistent solution, in units of \sigma, squared)
# 22. Calibrated Visibility Amplitude (Jy)
# 23. Estimated systematic uncertainty, as a fraction of the Calibrated Visibility Amplitude (#2).
NETWORKSOL_FIELDS = (
    ('day', str), # day
    ('hhmm', str),
    ('source', str),
    ('baseline', str),
    ('u', float),
    ('v', float),
    ('uvmag', float),
    ('sefd_1', float),
    ('sefd_2', float),
    ('calamp_apriori', float),
    ('amp', float),
    ('snr', float),
    ('el_1', float),
    ('el_2', float),
    ('expt', int),
    ('band', int),
    ('gain_1', float),
    ('gainerr_1', float),
    ('gain_2', float),
    ('gainerr_2', float),
    ('chisq', float),
    ('calamp_network', float),
#    ('syserr_fraction', float),
)

networksol_polarsargs = dict(columns = [a[0] for a in NETWORKSOL_FIELDS])

def read_networksol(filename):
    """
    Read networksol file into polars dataframe.

    Parameters
    ----------
    filename : str
        networksol filename.

    Returns
    -------
    polars.DataFrame
        DataFrame with networksol contents.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # skip comment lines and strip whitespaces -- comments start with #
    data = [[val.strip() for val in line.split() if val] for line in lines if line[0] != '#']
    df = pl.DataFrame(data).transpose()
    df.columns = networksol_polarsargs['columns']
    # keep missing data (u,v coords still good)
    # df.dropna(how="any", inplace=True)
    df = df.drop_nulls()

    return df

# modified networksol by Michael with model visibs and flag
NETWORKSOL2_FIELDS = (
    ('day', str), # day
    ('hhmm', str),
    ('source', str),
    ('baseline', str),
    ('u', float),
    ('v', float),
    ('uvmag', float),
    ('sefd_1', float),
    ('sefd_2', float),
    ('calamp_apriori', float),
    ('amp', float),
    ('snr', float),
    ('el_1', float),
    ('el_2', float),
    ('expt', int),
    ('band', int),
	('model', float),
    ('gain_1', float),
    ('gainerr_1', float),
    ('gain_2', float),
    ('gainerr_2', float),
    ('chisq', float),
    ('calamp_network', float),
	('flag', int),
#    ('syserr_fraction', float),
)

networksol2_polarsargs = dict(columns = [a[0] for a in NETWORKSOL2_FIELDS])

def read_networksol2_polars(filename, columns):
    """
    Read networksol2 file into polars dataframe.

    Parameters
    ----------
    filename : str
        networksol2 filename.

    Returns
    -------
    polars.DataFrame
        DataFrame with networksol2 contents.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # skip comment lines and strip whitespaces -- comments start with #
    data = [[val.strip() for val in line.split() if val] for line in lines if line[0] != '#']
    df = pl.DataFrame(data).transpose()
    df.columns = networksol2_polarsargs['columns']
    # keep missing data (u,v coords still good)
    # df.dropna(how="any", inplace=True)
    df = df.drop_nulls()

    return df

# aedit output produced by Vincent with channel-specific amplitudes
# 30 channel mode
#   1. path to fringe file (including experiment number, doy-hhmmss, baseline)
#   2. source
#   3. number of channels
#   4. amplitude (times 10^{-4}) [technically, correlation coefficient]
#   5. signal-to-noise ratio
#   6-35. amplitudes in each of the channels
BANDPASS_FIELDS = [
    ('path', str),
    ('source', str),
    ('nchan', str),
    ('amp', float),
    ('snr', float),
]

bandpass_polarsargs = dict([a[0] for a in BANDPASS_FIELDS])

def read_bandpass(filename):
    """
    Read bandpass file into polars dataframe.

    Parameters
    ----------
    filename : str
        bandpass filename.

    Returns
    -------
    polars.DataFrame
        DataFrame with bandpass contents.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    # skip comment lines and strip whitespaces -- comments start with #
    data = [[val.strip() for val in line.split() if val] for line in lines if line[0] != '#']
    df = pl.DataFrame(data).transpose()
    df.columns = bandpass_polarsargs['columns'] + ['amp_%d' % (i+1) for i in range(len(df.columns) - 5)]

    df.with_columns(pl.col('path').map_elements(lambda x: x.split('/')[0]).alias('experiment'), \
                    pl.col('path').map_elements(lambda x: x.split('/')[1]).alias('scan'), \
                    pl.col('path').map_elements(lambda x: x.split('/')[2]).alias('filename'))

    df = df.with_columns(pl.col('filename').map_elements(lambda x: x[:2]).alias('baseline'))

    return df
