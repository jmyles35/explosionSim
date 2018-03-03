import numpy as np

class Object:
    """Represented the arbitrary object being perturbed by the blast waves"""

    def __init__(self, density, shape, location):
        """Initializes the object"""

        # System constants
        self.gravity = 9.81                     # m/s

        # System parameters
        self.density = density                  # kg/m^3
        self.shape = shape
        self.location = location

        # Calculated dimensional parameters
        self.volume = self.volume               # m^3
        self.mass = self.volume * self.density  # kg
        self.CoM  = self.centre_of_mass

        # Lagrangian Parameters
        self.initialKE = 0
        self.initialPE = self.mass*self.graity*self.location[1] #mgy
        self.KE = [].append(self.initialKE)
        self.PE = [].append(self.initialPE)


    def volume(self):
        """Calculates the volume of the object"""
        #TODO: Implement
        return 0

    def centre_of_mass(self):
        """Calculates the centre of mass of the object.
           Applicable to both 2D or 3D renderings """
        #TODO: Implement
        return 0

    def kinetic_energy(self):
        """Determines the KE of the object"""
        #TODO: Implement
        return 0

    def potential_energy(self):
        """Determines the PE of the object"""
        #TODO: Implement
        return 0
