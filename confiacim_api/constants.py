MAX_TAG_NAME_LENGTH = 30
MIN_TAG_NAME_LENGTH = 3

PROP_MAT_POSITION = {
    # cement
    "E_c": 2,
    "poisson_c": 3,
    "thermal_expansion_c": 4,
    "thermal_conductivity_c": 7,
    "volumetric_heat_capacity_c": 8,
    "friction_angle_c": 13,
    "cohesion_c": 14,
    # formation
    "E_f": 2,
    "poisson_f": 3,
    "thermal_expansion_f": 4,
    "thermal_conductivity_f": 7,
    "volumetric_heat_capacity_f": 8,
}

HIDRATIONPROP_E_C = 1
HIDRATIONPROP_POISSON_C = 2
HIDRATIONPROP_COHESION_C = 13

HIDRATIONPROP_MAP = {
    HIDRATIONPROP_E_C: "E_c",
    HIDRATIONPROP_POISSON_C: "poisson_c",
    HIDRATIONPROP_COHESION_C: "cohesion_c",
}

PROP_CEMENT = (
    "E_c,poisson_c,thermal_expansion_c,thermal_conductivity_c,volumetric_heat_capacity_c,friction_angle_c,cohesion_c"
)
PROP_FORMANTION = "E_f,poisson_f,thermal_expansion_f,thermal_conductivity_f,volumetric_heat_capacity_f"
MATERIALS = (PROP_CEMENT + "," + PROP_FORMANTION).split(",")
LINE_CEMENT_MATERIAL = 3
LINE_FORMATION_MATERIAL = 4

LOADS_EXTERNAL_TEMPERATURE = "external_temperature"
LOADS_INTERNAL_PRESSURE = "internal_pressure"
LOADS_INTERNAL_TEMPERATURE = "internal_temperature"

LOADS = (
    LOADS_EXTERNAL_TEMPERATURE,
    LOADS_INTERNAL_PRESSURE,
    LOADS_INTERNAL_TEMPERATURE,
)

HIDRATIONPROP = "E_c,poisson_c,cohesion_c".split(",")
