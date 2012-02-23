from pyadh import *
from pyadh.default_n import *
from ladr_2d_p import *
timeIntegration = BackwardEuler
femSpaces = {0:DG_AffineP1_OnSimplexWithMonomialBasis}
elementQuadrature = SimplexGaussQuadrature(nd,4)
elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,4)
#numericalFluxType=Advection_DiagonalUpwind_Diffusion_LDG
numericalFluxType = Advection_DiagonalUpwind_Diffusion_IIPG
nnx=41; nny=41
tnList=[float(i)/10.0 for i in range(11)]
matrix = SparseMatrix
multilevelLinearSolver = LU
