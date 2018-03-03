import numpy as np

class Wave:
    """Represented the waves propagating from explosion"""

    def __init__(self, frequency):
        """Initializes the wae"""

        # System constants
        self.gravity = 9.81                     # m/s

        # System parameters
        self.frequency = frequency

        # Calculated dimensional parameters

        # Lagrangian Parameters
