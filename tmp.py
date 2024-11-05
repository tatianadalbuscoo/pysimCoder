import os

from supsisim.RCPblk import RCPblk

dirs = os.listdir("/mnt/c/Users/lucia/Desktop/pysimCoder/resources/blocks/rcpBlk")
for el in dirs:
    files = os.listdir("/mnt/c/Users/lucia/Desktop/pysimCoder/resources/blocks/rcpBlk" + "/" + el)
    for f in files:
        if not f.endswith(".py"):
            continue
        f = f.rstrip("*.py")
        if True: #try:
            cmd = "from " + el + "." + f + " import *"
            exec(cmd)
        #except:
        #    print("import of block class failed " + cmd)
        #    pass
from supsisim.RCPgen import *
from control import *


blks = []

realParNames = ()
intParNames = ()
sysPath = []

tmp = 0
for item in realParNames:
  for par in item:
    blks[tmp].realParNames.append(par)
  tmp += 1

tmp = 0
for item in intParNames:
  for par in item:
    blks[tmp].intParNames.append(par)
  tmp += 1

tmp = 0
for item in sysPath:
  blks[tmp].sysPath = item
  tmp += 1

os.environ["SHV_USED"] = "False"
os.environ["SHV_BROKER_IP"] = "127.0.0.1"
os.environ["SHV_BROKER_PORT"] = "3755"
os.environ["SHV_BROKER_USER"] = "admin"
os.environ["SHV_BROKER_PASSWORD"] = "admin!123"
os.environ["SHV_BROKER_DEV_ID"] = "untitled"
os.environ["SHV_BROKER_MOUNT"] = "test/untitled"
os.environ["SHV_TREE_TYPE"] = "GAVL"

fname = 'untitled'
os.chdir("./untitled_gen")
genCode(fname, 0.01, blks)
genMake(fname, 'sim.tmf', addObj = '')

import os
os.system("make clean")
os.system("make")
os.chdir("..")
