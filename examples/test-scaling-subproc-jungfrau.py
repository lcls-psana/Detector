
"""
Allocate  batch nodefor exclusive work:
srun --partition milano --reservation=lcls:scaling --account lcls:prjdat21 -n 1 --time=02:00:00 --exclusive --pty /bin/bash
IN OTHER WINDOW:
ssh -Y milanoNNN
cd LCLS/con-py3
source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/psconda.sh
source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/setup_testrel
and run it as
python Detector/examples/test-scaling-subproc.py 0 # for algorithm itself OR
python Detector/examples/test-scaling-subproc.py -1 25 # subproc for cpu #25
python Detector/examples/test-scaling-subproc.py -2 # on cpu = (0,1,2,...7)
python Detector/examples/test-scaling-subproc.py -3 # on cpu = (0,8,24,...,96)
python Detector/examples/test-scaling-subproc.py n # for algorithm on cpu n
python Detector/examples/test-scaling-subproc.py -100 # do_perf
"""


import sys
import numpy as np
from time import time, sleep

#import matplotlib
#matplotlib.use('QtAgg') # forse Agg rendering to a Qt canvas (backend)
#print('matplotlib.get_backend() %s' % str(matplotlib.get_backend()))
#import matplotlib.pyplot as plt

import psutil
from CalibManager.GlobalUtils import get_hostname, load_textfile
from CalibManager.PlotImgSpeWidget import proc_stat
from Detector.GlobalUtils import info_ndarr
from PSCalib.GlobalUtils import save_textfile
import pyimgalgos.Graphics as gr

SCRNAME = sys.argv[0].rsplit('/')[-1]

def hist_stat(hi):
    """returns mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w"""
    wei, bins, patches = hi
    return proc_stat(wei, bins)

def hist(arr, amp_range=None, bins=100, figsize=(6,5), axwin=(0.15, 0.12, 0.78, 0.80), title='title', xlabel='xlabel', ylabel='ylabel',titwin=None):
    fig = gr.figure(figsize=figsize, dpi=80, facecolor='w', edgecolor='w', frameon=True, move=None, title=titwin)
    ax = gr.add_axes(fig, axwin=axwin)
    his = gr.hist(ax, arr, bins=bins, amp_range=amp_range, weights=None, color=None, log=False)
    gr.add_title_labels_to_axes(ax, title=title, xlabel=xlabel, ylabel=ylabel, fslab=14, fstit=20, color='k')
    return fig, ax, his

def plot(y, xarr=None, amp_range=None, figsize=(6,5), axwin=(0.15, 0.12, 0.78, 0.80), pfmt='bo', lw=1,\
         title='set_title', xlabel='xlabel', ylabel='ylabel', titwin=None):
    fig = gr.figure(figsize=figsize, dpi=80, facecolor='w', edgecolor='w', frameon=True, move=None, title=titwin)
    x = list(range(len(y))) if xarr is None else xarr
    ax = gr.add_axes(fig, axwin=axwin)
    p = ax.plot(x, y, pfmt, linewidth=lw)
    if amp_range is not None: ax.set_ylim(amp_range)
    gr.add_title_labels_to_axes(ax, title=title, xlabel=xlabel, ylabel=ylabel, fslab=14, fstit=20, color='k')
    return fig, ax, p

def random_standard(shape=(40,60), mu=200, sigma=25, dtype=np.float64):
    a = mu + sigma*np.random.standard_normal(shape)
    return np.require(a, dtype)

def random_arrays(sh2d=(8*512,1024), dtype=np.float64):
    sh3d = (3,) + sh2d
    return random_standard(shape=sh2d, mu=10, sigma=2, dtype=dtype),\
           random_standard(shape=sh3d, mu=20, sigma=3, dtype=dtype)

def time_consuming_algorithm(sh2d=(8*512,1024), dtype=np.float32):
    t01 = time()
    a, b = random_arrays(sh2d=sh2d, dtype=dtype)
    #print(info_ndarr(a, 'arr2d:', last=10))
    #print(info_ndarr(b, 'arr3d:', last=10))

    t02 = time()
    gr1 = a>=11
    gr2 = (a>9) & (a<11)
    gr3 = a<=9
    t03 = time()
    a[gr1] -= b[0, gr1]
    a[gr2] -= b[1, gr2]
    a[gr3] -= b[2, gr3]
    t04 = time()
    return (t01, t02, t03, t04)

#def do_algo(cpu=0, cmt='v0', SHOW_FIGS=False, SAVE_FIGS=False, DO_SUMMARY=True, dtype=np.float64, sh2d=(8*512,1024), nevents=100):
#def do_algo(cpu=0, cmt='v0', SHOW_FIGS=False, SAVE_FIGS=False, DO_SUMMARY=True, dtype=np.float32, sh2d=(8*512,1024), nevents=100):
def do_algo(cpu=0, cmt='v0', SHOW_FIGS=False, SAVE_FIGS=False, DO_SUMMARY=True, dtype=np.float32, sh2d=(512,1024), nevents=100):

    hostname = get_hostname()
    #cpu_num = psutil.Process().cpu_num()
    print('requested cpu:%03d' % cpu)

    ntpoints = 6
    arrts = np.zeros((nevents,ntpoints), dtype=np.float64)
    t05_old = time()

    for nevt in range(nevents):
        t00 = time()
        #times = time_consuming_algorithm(sh2d=(8*512,1024), dtype=dtype)
        times = time_consuming_algorithm(sh2d=sh2d, dtype=dtype)
        cpu_num = psutil.Process().cpu_num()
        #if cpu_num >=16 and cpu_num <=23:
        #    print('cpu_num:%03d nevt:%03d time:%.6f CPU_NUM IN WEKA RANGE [16,23]' % (cpu_num, nevt, dt_sec))
        t05 = time()
        times = (t00,) + times + (t05,)
        arrts[nevt,:] = times
        dt_evt = t05 - t05_old
        t05_old = t05
        if nevt%10>0: continue
        dt_alg = times[4] - times[3]
        dt_in  = times[4] - times[1]
        print('cpu_num:%03d nevt:%03d  times (sec)' % (cpu_num, nevt), \
             ' random arrs: %.6f' % (times[2] - times[1]), \
             ' indeces: %.6f'     % (times[3] - times[2]), \
             ' alg: %.6f'         % (times[4] - times[3]), \
             ' inside algo: %.6f' % (times[4] - times[1]), \
             ' per event: %.6f'   % dt_evt)

        amp_range=(0, 0.2)
        dt_alg = arrts[:,4] - arrts[:,3]
        dt_tot = arrts[:,5] - arrts[:,0]
        dt_evt = arrts[1:,5] - arrts[:-1,5]
        print(info_ndarr(dt_alg, '%s times of alg:' % hostname, last=nevents))
        print(info_ndarr(dt_tot, '%s times alg tot:' % hostname, last=nevents))
        print(info_ndarr(dt_evt, '%s times per event:' % hostname, last=nevents))

    if DO_SUMMARY:
        tit = '%s cpu_num %03d' % (hostname, cpu_num)

        fhi, ahi, his = hist(dt_alg,  amp_range=amp_range, title=tit, xlabel='dt_alg, sec', ylabel='dN/dt', titwin=tit + ' time of alg per event')
        #fpl, apl, spl = plot(dt_alg,  amp_range=amp_range, title=tit, xlabel='event', ylabel='t, sec', titwin=tit + ' time vs event')
        #fht, aht, hit = hist(dt_evt,  amp_range=amp_range, title=tit, xlabel='dt_evt, sec', ylabel='dN/dt', titwin=tit + ' time per event total')

        mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w = hist_stat(his)
        rec = 'hostname:%s cpu:%03d cmt:%s proc time (sec) mean: %.4f +/- %.4f rms: %.4f +/- %.4f\n' % (hostname, cpu, cmt, mean, err_mean, rms, err_rms)
        print(rec)

        fnprefpr = 'figs/fig-subpr32-512k-%s-%s' % (cmt, hostname)
        save_textfile(rec, fnprefpr+'-summary.txt', mode='a')

        if SAVE_FIGS:
            fnprefix = '%s-cpu%03d' % (fnprefpr, cpu)
            gr.save_fig(fhi, fname=fnprefix+'-time-alg.png')
            #gr.save_fig(fpl, fname=fnprefix+'-time-alg-vs-evt.png')
            #gr.save_fig(fht, fname=fnprefix+'-time-evt.png')

        if SHOW_FIGS:
            gr.show()
        else:
            del fhi, ahi, his


#from subprocess import getoutput

import subprocess # for subprocess.Popen


def subproc(command, env=None, shell=False):
    command_seq = command.split()  # for example, command_seq=['bsub', '-q', cp.batch_queue, '-o', 'log-ls.txt', 'ls -l']
    p = subprocess.Popen(command_seq, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, shell=shell) #, stdin=subprocess.STDIN
    print('started subprocess pid: %d for command: %s' % (p.pid, command))
    return p

def subproc_wait(command=None, cmd_seq=None,  env=None, shell=False):
    command_seq = command.split() if cmd_seq is None else cmd_seq  # for example, command_seq=['bsub', '-q', cp.batch_queue, '-o', 'log-ls.txt', 'ls -l']
    p = subprocess.Popen(command_seq, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, shell=shell) #, stdin=subprocess.STDIN
    p.wait()
    out = p.stdout.read().decode('utf-8') # reads entire file
    err = p.stderr.read().decode('utf-8') # reads entire file
    return out, err

def run_subprocs_on_cpus(cpus=(0,), cmt='v0', sleep_sec=1, nchecks=1000):
    print('TBD: subprocs_on_cpus: %s' % str(cpus))
    commands = ['taskset --cpu-list %d python Detector/examples/test-scaling-subproc.py %d %s' % (n, n, cmt) for n in cpus]

    for c in commands: print('command: %s' % c)

    subprocs = [subproc(c, env=None, shell=False) for c in commands]
    for n in range(nchecks):
      print('\n%02d check subprocesses for CPU:' % n)
      for i,p in enumerate(subprocs):
        print('  %02d:%s' % (cpus[i], str(p.poll())), end=' ')

      pstatus = [p.poll() is not None for p in subprocs]
      if all(pstatus): break
      sleep(sleep_sec)

    for i,p in enumerate(subprocs):
        cpu = cpus[i]
        print('==========\ncpu:%02d' % cpu)
        out = p.stdout.read() # reads entire file
        err = p.stderr.read() # reads entire file
        s = out.decode('utf-8')
        print('subprocess on CPU %d out:\n%s' % (cpu, s))
        print('subprocess err:', err)

def sort_records_in_file(fname):
    print('\n\n\nsort_records_in_file: %s' % fname)
    s = load_textfile(fname)
    #print(s)
    recs = sorted(s.split('\n'))
    print('records:')
    means = []
    for s in recs:
        #print(s)
        fields = s.split()
        if len(fields)<7:  continue
        means.append(float(fields[7]))
    means = np.array(means)
    print(info_ndarr(means, 'means:', last=100))
    msg = 'mean time (sec): %0.4f' % means.mean()
    print(msg)

    s = '\n'.join(recs) + '\n%s' % msg
    print(s)
    save_textfile(s, fname.rstrip('.txt')+'-ordered.txt', mode='w')

def sort_records_in_files():
    for fname in (
        #'fig-subpr-v08-1-sdfmilan114-summary.txt',
        #'fig-subpr-v08-2-sdfmilan114-summary.txt',
        #'fig-subpr-v08-3-sdfmilan114-summary.txt',
        #'fig-subpr-v08-4-sdfmilan114-summary.txt',
        #'fig-subpr-v08-5-sdfmilan114-summary.txt',
        #'fig-subpr-vx8-sdfmilan114-summary.txt',
        #'fig-subpr-v16-1-sdfmilan114-summary.txt',
        #'fig-subpr-v16-2-sdfmilan114-summary.txt',
        #'fig-subpr-v16-3-sdfmilan114-summary.txt',
        #'fig-subpr-v16-4-sdfmilan114-summary.txt',
        #'fig-subpr-v24-sdfmilan114-summary.txt',
        #'fig-subpr-v32-1-sdfmilan114-summary.txt',
        #'fig-subpr-v32-2-sdfmilan114-summary.txt',
        #'fig-subpr-v32-3-sdfmilan114-summary.txt',
        #'fig-subpr-v56-sdfmilan114-summary.txt',
        #'fig-subpr-v64-sdfmilan114-summary.txt',
        #'fig-subpr-v120-sdfmilan114-summary.txt',
        #'fig-subpr-v120-2-sdfmilan114-summary.txt',
        #'fig-subpr-v1-sdfmilan216-summary.txt',
        #'fig-subpr-v08-1-sdfmilan216-summary.txt',
        #'fig-subpr-v16-1-sdfmilan216-summary.txt',
        #'fig-subpr-v32-1-sdfmilan216-summary.txt',
        #'fig-subpr-v64-sdfmilan216-summary.txt',
        #'fig-subpr-v120-sdfmilan216-summary.txt',
        #'fig-subpr32-v1-sdfmilan216-summary.txt',
        #'fig-subpr32-v08-1-sdfmilan216-summary.txt',
        #'fig-subpr32-v16-1-sdfmilan216-summary.txt',
        #'fig-subpr32-v32-1-sdfmilan216-summary.txt',
        #'fig-subpr32-v64-sdfmilan216-summary.txt',
        #'fig-subpr32-v120-sdfmilan216-summary.txt',
        'fig-subpr32-512k-v1-sdfmilan216-summary.txt',
        'fig-subpr32-512k-v08-1-sdfmilan216-summary.txt',
        'fig-subpr32-512k-v16-1-sdfmilan216-summary.txt',
        'fig-subpr32-512k-v32-1-sdfmilan216-summary.txt',
        'fig-subpr32-512k-v64-sdfmilan216-summary.txt',
        'fig-subpr32-512k-v120-sdfmilan216-summary.txt',
        ):
        sort_records_in_file('figs/%s' % fname)

def parse_perf_results(txt):
    """in text find all lines like "27,264 cache-references:u" and return them as dict of items {'cache-references':27264}"""
    #print(' parse_perf_results:\n') #, txt)
    d = {}
    d['t_sec'] = time()
    for s in txt.split('\n'):
        print(s)
        flds = s.lstrip().split()  # 7,226 cache-misses:u # 25.584 % of all cache refs
        if len(flds) < 2: continue
        if flds[1][-2:] != ':u': continue
        #for f in flds: print(f, end=' ')
        v = int(flds[0].replace(',',''))  # convert str '7,226' to int 7226
        k = flds[1].rstrip(':u')
        d[k] = v
    return d


def print_perf_results(list_resps, cmt='v0'):
    hostname = get_hostname()
    keys = list_resps[0].keys()
    t0_sec = list_resps[0]['t_sec']
    s = 'host: %s version: %s\n' % (get_hostname(), cmt)\
      + 'test#     ' + ' '.join(['%s'%k.ljust(12) for k in keys])
    for i,d in enumerate(list_resps):
        d['t_sec'] -= t0_sec
        s += '\n%03d ' % i\
          + ' '.join(['%12d' % d[k] for k in keys])
    print(20*'_','\n',s,'\n',20*'_')

    fname = 'figs/fig-perf-%s-%s-results.txt' % (cmt, hostname)
    save_textfile(s, fname, mode='w')


def dict_perf_results_to_table(d, cmt):
    keys = d.keys()
    s = 'host: %s\n' % (get_hostname())\
      + 'test#     ' + ' '.join(['%s'%k.ljust(12) for k in keys])\
      + '\n%s ' % cmt + ' '.join(['%12d' % d[k] for k in keys])
    return s


def convert_perf_results_file(fname):
    print('convert_perf_results_file: %s' % fname)
    s = load_textfile(fname)
    d = parse_perf_results(s)
    txt = dict_perf_results_to_table(d, fname.lstrip('pref-res-').rstrip('.txt'))
    print(20*'_','\n', txt, '\n',20*'_')
    #fnout = fname.lstrip('.txt')+'-table.txt'
    save_textfile(txt, fname, mode='a')


def plot_perf_results(list_resps, cmt='v0', SHOW_PLOTS=False):
    hostname = get_hostname()
    keys = list_resps[0].keys()
    print('number of measurements: %d' % len(list_resps))
    print('keys:', keys)
    list_of_plots = []
    for k in keys:
        y = np.array([d[k] for d in list_resps])
        t = np.array([d['t_sec'] for d in list_resps])
        t -= t[0]
        fig, ax, pl = plot(y, xarr=t, amp_range=None, title='%s vs time' % k, xlabel='t, sec', ylabel=k, titwin='%s vs time' % k)
        list_of_plots.append((fig, ax, pl))
        fname = 'figs/fig-perf-%s-%s-%s.png' % (cmt, hostname, k)
        gr.save_fig(fig, fname=fname)

    if SHOW_PLOTS:
        gr.show()


def do_perf(cmt='v0'):  #nloops=5, mode=-13,
    print('do_perf is started')
    #cmd  = 'perf stat -e cache-references,cache-misses,cycles,instructions,branches,faults,migrations sleep 5'
    #cmd  = 'perf stat python Detector/examples/test-scaling-subproc.py %d' % mode
    cmd0  = 'perf stat -e stalled-cycles-backend,stalled-cycles-frontend,ls_l1_d_tlb_miss.all,l1_dtlb_misses,l1_data_cache_fills_all,bp_l1_tlb_miss_l2_tlb_miss.if2m,bp_l1_tlb_miss_l2_tlb_miss,l2_dtlb_misses,l2_itlb_misses  python Detector/examples/test-scaling-subproc.py %d'

    list_resps = []

#    modes = (-1, -2, -8, -13, -17, -18)
#    modes = (-1, -2, -8, -13, -17, -18)
#    modes = (-1,   -1,  -1,  -1,  -1,
#             -2,   -2,  -2,  -2,  -2,
#             -8,   -8,  -8,  -8,  -8,
#             -13, -13, -13, -13, -13,
#             -17, -17, -17, -17, -17,
#             -18, -18, -18, -18, -18,
#             )

    modes = (-2,-2,-2,-2,-2,)

    #for i in range(nloops):
    for i,mode in enumerate(modes):
        cmd = cmd0 % mode
        print('loop %02d/%02d mode: %d\n command: %s' % (i, len(modes), mode, str(cmd)))
        out, err = subproc_wait(command=cmd, env=None, shell=False)
        print('out:', out)
        print('err:', err)
        d = parse_perf_results(err)
        print(d)
        if out: print('out:', out)
        list_resps.append(d)
        print(4*'=')
    print_perf_results(list_resps, cmt=cmt)
    plot_perf_results(list_resps, cmt=cmt, SHOW_PLOTS=True)


def subproc_cpu_single():
    """python Detector/examples/test-scaling-subproc.py -1 25 # subproc for cpu #25"""
    cpu = 5 if len(sys.argv)<3 else int(sys.argv[2])
    run_subprocs_on_cpus(cpus=(cpu,), cmt='v1')

def subproc_cpu_08_1():
    run_subprocs_on_cpus(cpus=tuple(range(8)), cmt='v08-1')

def subproc_cpu_08_2():
    run_subprocs_on_cpus(cpus=tuple(range(8,16)), cmt='v08-2')

def subproc_cpu_08_3():
    run_subprocs_on_cpus(cpus=tuple(range(24,32)), cmt='v08-3')

def subproc_cpu_08_4():
    run_subprocs_on_cpus(cpus=tuple(range(64,80)), cmt='v08-4')

def subproc_cpu_08_5():
    run_subprocs_on_cpus(cpus=tuple(range(120,128)), cmt='v08-5')

def subproc_cpu_x8():
    run_subprocs_on_cpus(cpus=(0, 8, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120), cmt='vx8')

def subproc_cpu_16_1():
    run_subprocs_on_cpus(cpus=tuple(range(16)), cmt='v16-1')

def subproc_cpu_16_2():
    run_subprocs_on_cpus(cpus=tuple(range(32,48)), cmt='v16-2')

def subproc_cpu_16_3():
    run_subprocs_on_cpus(cpus=tuple(range(64,80)), cmt='v16-3')

def subproc_cpu_16_4():
    run_subprocs_on_cpus(cpus=tuple(range(112,128)), cmt='v16-4')

def subproc_cpu_24():
    run_subprocs_on_cpus(cpus=tuple(range(16))+tuple(range(24,32)), cmt='v24')

def subproc_cpu_32_1():
    run_subprocs_on_cpus(cpus=tuple(range(32,64)), cmt='v32-1')

def subproc_cpu_32_2():
    run_subprocs_on_cpus(cpus=tuple(range(64,96)), cmt='v32-2')

def subproc_cpu_32_3():
    run_subprocs_on_cpus(cpus=tuple(range(96,128)), cmt='v32-3')

def subproc_cpu_56():
    run_subprocs_on_cpus(cpus=tuple(range(16))+tuple(range(24,64)), cmt='v56')

def subproc_cpu_64():
    run_subprocs_on_cpus(cpus=tuple(range(64,128)), cmt='v64')

def subproc_cpu_120():
    run_subprocs_on_cpus(cpus=tuple(range(16))+tuple(range(24,128)), cmt='v120')

def selector(mode):
    print('sys.argv:', sys.argv)
    print('selector for mode: %s' % str(mode))
    if mode >-1 and mode<128: do_algo(cpu=mode, cmt='v0' if len(sys.argv)<3 else sys.argv[2], SHOW_FIGS=False, SAVE_FIGS=False)
    elif mode == -1: subproc_cpu_single() # test on single CPU (number is sys.argv[1]) in subprocess
    elif mode == -2: subproc_cpu_08_1()
    elif mode == -3: subproc_cpu_08_2()
    elif mode == -4: subproc_cpu_08_3()
    elif mode == -5: subproc_cpu_08_4()
    elif mode == -6: subproc_cpu_08_5()
    elif mode == -7: subproc_cpu_x8()
    elif mode == -8: subproc_cpu_16_1()
    elif mode == -9: subproc_cpu_16_2()
    elif mode ==-10: subproc_cpu_16_3()
    elif mode ==-11: subproc_cpu_16_4()
    elif mode ==-12: subproc_cpu_24()
    elif mode ==-13: subproc_cpu_32_1()
    elif mode ==-14: subproc_cpu_32_2()
    elif mode ==-15: subproc_cpu_32_3()
    elif mode ==-16: subproc_cpu_56()
    elif mode ==-17: subproc_cpu_64()
    elif mode ==-18: subproc_cpu_120()
    elif mode ==-99: sort_records_in_files()
    #elif mode ==-100: do_perf(nloops=2, mode=-13, cmt='v32_1')
    elif mode ==-100: do_perf(cmt='v5x-2')  #nloops=10, mode=-1,
    elif mode ==-101: convert_perf_results_file(fname=sys.argv[2])
    else: print ('ERROR: NON-IMPLEMENTED mode: %s' % str(mode))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        import inspect
        USAGE = '\nUsage: %s <tname>\n' % sys.argv[0].split('/')[-1]\
              + '\n'.join([s for s in inspect.getsource(selector).split('\n') if "mode ==" in s or "mode >" in s])
        print('\n%s\n' % USAGE)
    else:
        mode = int(sys.argv[1])
        selector(mode)

# EOF

