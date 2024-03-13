"""
Allocate  batch nodefor exclusive work:
srun --partition milano --reservation=lcls:scaling --account lcls:prjdat21 -n 1 --time=02:00:00 --exclusive --pty /bin/bash
IN OTHER WINDOW:
ssh -Y milanoNNN
cd LCLS/con-py3

source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/psconda.sh
source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/setup_testrel

and run it as
python Detector/examples/test-subproc-output.py
taskset --cpu-list 127 python Detector/examples/test-subproc-output.py
"""

from time import time, sleep

import subprocess

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


cmd = 'perf stat -e stalled-cycles-backend,stalled-cycles-frontend,ls_l1_d_tlb_miss.all,l1_dtlb_misses,l1_data_cache_fills_all,bp_l1_tlb_miss_l2_tlb_miss.if2m,bp_l1_tlb_miss_l2_tlb_miss,l2_dtlb_misses,l2_itlb_misses  python Detector/examples/test-scaling-subproc.py -8'

print('command:', cmd)
#out, err = subproc_wait(command=cmd, env=None, shell=False)
p = subproc(command=cmd, env=None, shell=False)

#def deal_with_stdout():
#    for bstr in p.stdout:
#        print(bstr.decode('utf-8'))

#from threading import Thread
#t = Thread(target=deal_with_stdout, daemon=True)
#t.start()
#t.join()

for i in range(100):
    print('=========== LOOP %03d' % i)
    for line in p.stdout:
       print('stdout:', line)
    for line in p.stderr:
       print('stdout:', line)
    #out, err = p.communicate()
    #out = p.stdout.read().decode('utf-8') # reads entire file
    #err = p.stderr.read().decode('utf-8') # reads entire file
    #out = out.decode('utf-8')
    #err = err.decode('utf-8')err
    #out = p.stdout.readline().decode('utf-8')
    #out = p.stderr.readline().decode('utf-8')
    #out = p.stdout.flush().decode('utf-8')
    #err = p.stderr.flush().decode('utf-8')
    #print('out:', out)
    #print('err:', err)
    sleep(5)

# EOF
