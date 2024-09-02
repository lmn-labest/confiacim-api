from faker import Faker

faker = Faker()

CASE_FILE = """\
mesh
    nnode 83 numel 82 numat 4 ndf 1 therm 1 maxno 2 dim 1 npi 3
    insert materials.dat
    insert mesh.dat
    insert initialtemperature.dat
    insert loads.dat
end mesh
tmaxnlit 200
maxnlit 200
solvtrac 0
dt 1.0
loop 10
solvt
solvm
next
dt 2.0
loop 10
solvt
solvm
next
dt 5.0
loop 20
solvt
solvm
next
stop"""


RES_CASE_FILE_1 = """\
mesh
    nnode 83 numel 82 numat 4 ndf 1 therm 1 maxno 2 dim 1 npi 3
    insert materials.dat
    insert mesh.dat
    insert initialtemperature.dat
    insert loads.dat
end mesh
tmaxnlit 200
maxnlit 200
solvtrac 0
dt 1.0
loop 1
solvt
solvm
next
stop"""

RES_CASE_FILE_2 = """\
mesh
    nnode 83 numel 82 numat 4 ndf 1 therm 1 maxno 2 dim 1 npi 3
    insert materials.dat
    insert mesh.dat
    insert initialtemperature.dat
    insert loads.dat
end mesh
tmaxnlit 200
maxnlit 200
solvtrac 0
dt 1.0
loop 9
solvt
solvm
next
stop"""


RES_CASE_FILE_3 = """\
mesh
    nnode 83 numel 82 numat 4 ndf 1 therm 1 maxno 2 dim 1 npi 3
    insert materials.dat
    insert mesh.dat
    insert initialtemperature.dat
    insert loads.dat
end mesh
tmaxnlit 200
maxnlit 200
solvtrac 0
dt 1.0
loop 10
solvt
solvm
next
dt 2.0
loop 1
solvt
solvm
next
stop"""

RES_CASE_FILE_4 = """\
mesh
    nnode 83 numel 82 numat 4 ndf 1 therm 1 maxno 2 dim 1 npi 3
    insert materials.dat
    insert mesh.dat
    insert initialtemperature.dat
    insert loads.dat
end mesh
tmaxnlit 200
maxnlit 200
solvtrac 0
dt 1.0
loop 10
solvt
solvm
next
dt 2.0
loop 10
solvt
solvm
next
stop"""


NEW_CASE_FILE_LAST_STEP_3 = """\
mesh
nnode 83 numel 82 numat 4 ndf 1 therm 1 maxno 2 dim 1 npi 3
insert materials.dat
insert mesh.dat
insert initialtemperature.dat
insert initialstress.dat
insert loads.dat
insert adiabat.dat
end mesh
nocliprc
tmaxnlit 200
maxnlit 200
solvtrac 0
dt 1e-08
loop 1
solvt
solvm
next
dt 0.1
loop 2
solvt
solvm
next
stop\
"""
