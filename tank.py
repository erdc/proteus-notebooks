from math import *
import proteus.MeshTools
from proteus.Gauges import LineGauges, LineIntegralGauges
from proteus import Domain
from proteus.default_n import * 

# 2D dam breaking
# Collapse of a water column on a rigid horizontal plane 
# According to the experiments of Martin and Moyce (1952)
# We use surge front position and remaining water column height
# Hybrid VOF-LS is used for tracking the free surface
 
#  Discretization -- input options  
genMesh=True
movingDomain=False
applyRedistancing=True
useOldPETSc=False
useSuperlu=False
timeDiscretization='be'#'vbdf'#'be','flcbdf'
spaceOrder = 1
useHex     = False
useRBLES   = 0.0
useMetrics = 1.0
applyCorrection=True

# Free surface tracking and turbulence models

useVF = 1.0

try:
    with open('vof_only.txt') as f:
        vof_option = bool(f.readline())
except:
    vof_option = False

useOnlyVF = False
useRANS = 0 # 0 -- None
            # 1 -- K-Epsilon
            # 2 -- K-Omega
    
#  Discretization   
nd = 2
hFactor=1.0
basis=C0_AffineLinearOnSimplexWithNodalBasis
elementQuadrature = SimplexGaussQuadrature(nd,3)
elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,3) 	    
    
# Model setup:Domain and mesh
# a = 2.25 inches
a= 0.05715
Lx = (2 + 1)*a
L = (Lx, 0.15875)
# Refinement of 10 corresponds to he = 0.0176388888889
# Run this against 10, 20, 40, 80
# Refinement 80 should run in an hour or two on a fast workstation
with open('refinement_level.txt') as f:
    refinement_option = int(f.readline())

he = L[1]/float(refinement_option-1)
weak_bc_penalty_constant = 100.0
nLevels = 1
parallelPartitioningType = proteus.MeshTools.MeshParallelPartitioningTypes.node
nLayersOfOverlapForParallel = 0
structured=False

boundaries=['left','right','bottom','top','front','back']
boundaryTags=dict([(key,i+1) for (i,key) in enumerate(boundaries)])

vertices=[[0.0,0.0],#0
          [L[0],0.0],#1
          [L[0],L[1]],#2
          [0.0,L[1]]]#3
vertexFlags=[boundaryTags['bottom'],
             boundaryTags['bottom'],
             boundaryTags['top'],
             boundaryTags['top']]
segments=[[0,1],
          [1,2],
          [2,3],
          [3,0]]
segmentFlags=[boundaryTags['bottom'],
              boundaryTags['right'],
              boundaryTags['top'],
              boundaryTags['left']]
regions=[[0.5*L[0],0.5*L[1]]]
regionFlags=[1]
domain = Domain.PlanarStraightLineGraphDomain(vertices=vertices,
                                              vertexFlags=vertexFlags,
                                              segments=segments,
                                              segmentFlags=segmentFlags,
                                              regions=regions,
                                              regionFlags=regionFlags)
#go ahead and add a boundary tags member 
domain.boundaryTags = boundaryTags
domain.writePoly("mesh")
domain.writePLY("mesh")
domain.writeAsymptote("mesh")
triangleOptions="VApq30Dena%8.8f" % ((he**2)/2.0,)

# Time stepping

T=1.0
dt_fixed = 0.01
dt_init = min(0.1*dt_fixed,0.001)
runCFL=0.9
nDTout = int(round(T/dt_fixed))

# Numerical parameters
backgroundDiffusionFactor=0.01
ns_forceStrongDirichlet = False

ns_shockCapturingFactor  = 0.75
ns_lag_shockCapturing = True
ns_lag_subgridError = True
ls_shockCapturingFactor  = 0.75
ls_lag_shockCapturing = True
ls_sc_uref  = 1.0
ls_sc_beta  = 1.0
vof_shockCapturingFactor = 0.75
vof_lag_shockCapturing = True
vof_sc_uref = 1.0
vof_sc_beta = 1.0
rd_shockCapturingFactor  = 0.75
rd_lag_shockCapturing = False
epsFact_density    = 3.0
epsFact_viscosity  = epsFact_curvature  = epsFact_vof = epsFact_consrv_heaviside = epsFact_consrv_dirac = epsFact_density
epsFact_redistance = 0.33
epsFact_consrv_diffusion = 1.0
redist_Newton = False
kappa_shockCapturingFactor = 0.1
kappa_lag_shockCapturing = True#False
kappa_sc_uref = 1.0
kappa_sc_beta = 1.0
dissipation_shockCapturingFactor = 0.1
dissipation_lag_shockCapturing = True#False
dissipation_sc_uref = 1.0
dissipation_sc_beta = 1.0

ns_nl_atol_res = max(1.0e-10,0.001*he**2)
vof_nl_atol_res = max(1.0e-10,0.001*he**2)
ls_nl_atol_res = max(1.0e-10,0.001*he**2)
rd_nl_atol_res = max(1.0e-10,0.005*he)
mcorr_nl_atol_res = max(1.0e-10,0.001*he**2)
kappa_nl_atol_res = max(1.0e-10,0.001*he**2)
dissipation_nl_atol_res = max(1.0e-10,0.001*he**2)

#Turbulence closure model

ns_closure=2 #1-classic smagorinsky, 2-dynamic smagorinsky, 3 -- k-epsilon, 4 -- k-omega

# Water
rho_0 = 998.2
nu_0  = 1.004e-6

# Air
rho_1 = 1.205
nu_1  = 1.500e-5 

# Surface tension
sigma_01 = 0.0

# Gravity
g = [0.0,-9.80665]

# Initial condition
waterLine_x = a
# n^2 = 1
waterLine_z = a

def signedDistance(x):
    phi_x = x[0]-waterLine_x
    phi_z = x[1]-waterLine_z 
    if phi_x < 0.0:
        if phi_z < 0.0:
            return max(phi_x,phi_z)
        else:
            return phi_z
    else:
        if phi_z < 0.0:
            return phi_x
        else:
            return sqrt(phi_x**2 + phi_z**2)

fields = ('vof',)

lineColumn = ((0, 0, 0), (0, L[1], 0))
columnLines = [lineColumn]

columnGauge = LineIntegralGauges(gauges=((fields, columnLines),),
                                 fileName='column_gauge.csv')

lineSurge = ((0, 0, 0), (L[0], 0, 0))
surgeLines = [lineSurge]

surgeGauge = LineGauges(gauges=((fields, surgeLines),),
                        fileName='surge_gauge.csv')
