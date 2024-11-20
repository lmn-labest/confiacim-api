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
stop
"""


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
stop
"""

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
stop
"""


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
stop
"""

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
stop
"""


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
stop
"""

MATERIALS_FILE = """\
materials
    1 1 1.999e+11 0.3000 1.400e-05 0 0 4.292e+01 3.894e+06 0 0 0
    2 2 1.000e+10 0.3100 0 0 0 3.360e+00
    3 1 1.0190e+10 0.3200 9.810e-06 0 7 3.360e+00 2.077e+06 0 1 0 3.200e+06 1.500e+01 2.540e+07 0 0 0 0 0 0 3 8 3.000e-03
    4 1 2.040e+10 0.3600 1.000e-05 0 0 6.006e+00 1.901e+06 0 0 0
end materials
return"""  # noqa: E501

WRONG_MAT_NUMBER_MATERIALS_FILE = """\
materials
    d 1 1.999e+11 0.3000 1.400e-05 0 0 4.292e+01 3.894e+06 0 0 0
end materials
return"""


LOADS_FILE = """\
constraindisp
83 1
end constraindisp
constraintemp
83 1
end constraintemp
nodalloads
1 1
end nodalloads
nodalthermloads
1 2
end nodalthermloads
nodalsources
83 291.639
end nodalsources
loads
1 11 0.11123 4
0    0.0000e+00
600  0.0000e+00
1200 6.8947e+07
1800 6.8947e+07
2 4 3
600  15 299.073
1200 15 299.073
1800 15 299.073
end loads
return
"""

hidration_FILE = """\
hidrprop
3 1 7
0.0 2.200e+08
0.04 2.200e+08
0.045 8.592e+08
0.08 2.429e+09
0.2 4.858e+09
0.49 8.148e+09
1.0 1.190e+10
3 2 4
0.0 4.900e-01
0.04 4.900e-01
0.08 1.800e-01
1.0 1.800e-01
3 7 3
0.00 2.420e+06
0.50 1.936e+06
1.00 1.936e+06
3 11 3
0.00 8.000e+04
0.04 8.000e+04
1.00 4.708e+06
3 13 3
0.00 8.000e+05
0.04 8.000e+05
1.00 1.970e+07
end hidrprop
return
"""
