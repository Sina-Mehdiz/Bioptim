import time

import biorbd

from biorbd_optim import OptimalControlProgram
from biorbd_optim.problem_type import ProblemType
from biorbd_optim.objective_functions import ObjectiveFunction
from biorbd_optim.constraints import Constraint
from biorbd_optim.path_conditions import Bounds, QAndQDotBounds, InitialConditions


def prepare_ocp(biorbd_model_path="eocar.bioMod", show_online_optim=True):
    # --- Options --- #
    # Model path
    biorbd_model = biorbd.Model(biorbd_model_path)

    # Problem parameters
    number_shooting_points = 1000
    final_time = 60
    torque_min, torque_max, torque_init = -100, 100, 0

    # Add objective functions
    objective_functions = ((ObjectiveFunction.minimize_torque, 100),)

    # Dynamics
    variable_type = ProblemType.torque_driven

    # Constraints
    constraints = (
        (Constraint.Type.MARKERS_TO_PAIR, Constraint.Instant.START, (0, 1)),
        (Constraint.Type.MARKERS_TO_PAIR, Constraint.Instant.END, (0, 2)),
    )

    # Path constraint
    X_bounds = QAndQDotBounds(biorbd_model)

    for i in range(1, 6):
        X_bounds.first_node_min[i] = 0
        X_bounds.last_node_min[i] = 0
        X_bounds.first_node_max[i] = 0
        X_bounds.last_node_max[i] = 0
    X_bounds.last_node_min[2] = 1.57
    X_bounds.last_node_max[2] = 1.57

    # Initial guess
    X_init = InitialConditions([0] * (biorbd_model.nbQ() + biorbd_model.nbQdot()))

    # Define control path constraint
    U_bounds = Bounds(
        [torque_min] * biorbd_model.nbGeneralizedTorque(),
        [torque_max] * biorbd_model.nbGeneralizedTorque(),
    )
    U_init = InitialConditions([torque_init] * biorbd_model.nbGeneralizedTorque())

    # ------------- #

    return OptimalControlProgram(
        biorbd_model,
        variable_type,
        number_shooting_points,
        final_time,
        objective_functions,
        X_init,
        U_init,
        X_bounds,
        U_bounds,
        constraints,
        show_online_optim=show_online_optim,
    )


if __name__ == "__main__":
    ocp = prepare_ocp(show_online_optim=True)

    # --- Solve the program and show --- #
    sol = ocp.solve()

    # Admire the graph for 10 more seconds
    time.sleep(10)
