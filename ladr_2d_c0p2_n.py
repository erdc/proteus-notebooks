from pyadh import *
from pyadh.default_n import *
from ladr_2d_p import *
timeIntegration = BackwardEuler
femSpaces = {0:C0_AffineQuadraticOnSimplexWithNodalBasis}
elementQuadrature = SimplexGaussQuadrature(nd,5)
elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,5)
nnx=11; nny=11
nLevels=1
tnList=[float(i)/10.0 for i in range(11)]
matrix = SparseMatrix
multilevelLinearSolver = LU
subgridError = AdvectionDiffusionReaction_ASGS(coefficients,nd)
shockCapturing = ResGradQuad_SC(coefficients,nd,shockCapturingFactor=0.99,lag=True)
