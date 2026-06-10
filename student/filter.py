# imports
import numpy as np

# add project directory to python path to enable relative imports
import os
import sys
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))
import misc.params as params 


class Filter:
    '''Kalman filter class'''
    def __init__(self):
        self.dim_state = params.dim_state # process model dimension
        self.dt = params.dt # time increment
        self.q = params.q # process noise variable for Kalman filter Q

    def F(self):
        ############
        # TODO Step 1: implement and return 6x6 system matrix F
        ############
        dt = self.dt

        return np.matrix([[1, 0, 0, dt, 0,  0 ],
                          [0, 1, 0, 0,  dt, 0 ],
                          [0, 0, 1, 0,  0,  dt],
                          [0, 0, 0, 1,  0,  0 ],
                          [0, 0, 0, 0,  1,  0 ],
                          [0, 0, 0, 0,  0,  1 ]])

        ############
        # END student code
        ############

    def Q(self):
        ############
        # TODO Step 1: implement and return process noise covariance Q
        ############
        q = self.q
        dt = self.dt

        q1 = dt * q
        q2 = (dt**2 * q) / 2
        q3 = (dt**3 * q) / 3

        return np.matrix([[q3, 0,  0,  q2, 0,  0 ],
                          [0,  q3, 0,  0,  q2, 0 ],
                          [0,  0,  q3, 0,  0,  q2],
                          [q2, 0,  0,  q1, 0,  0 ],
                          [0,  q2, 0,  0,  q1, 0 ],
                          [0,  0,  q2, 0,  0,  q1]])

        ############
        # END student code
        ############

    def predict(self, track):
        F = self.F()
        Q = self.Q()
        ############
        # TODO Step 1: predict state x and estimation error covariance P to next timestep, save x and P in track
        ############
        x = F * track.x
        P = F * track.P * F.T + Q
        track.set_x(x)
        track.set_P(P)

        ############
        # END student code
        ############

    def update(self, track, meas):
        ############
        # TODO Step 1: update state x and covariance P with associated measurement, save x and P in track
        ############
        H = meas.sensor.get_H(track.x)
        x = track.x
        P = track.P
        R = meas.R

        gamma = self.gamma(track, meas)
        S = self.S(track, meas, H)
        K = P * H.T * np.linalg.inv(S)
        x = x + K * gamma
        I = np.matrix(np.eye(self.dim_state))
        P = (I - K * H) * P

        ############
        # END student code
        ############
        track.update_attributes(meas)

        track.set_x(x)
        track.set_P(P)
    
    def gamma(self, track, meas):
        ############
        # TODO Step 1: calculate and return residual gamma
        ############
        return meas.z - meas.sensor.get_hx(track.x)

        ############
        # END student code
        ############

    def S(self, track, meas, H):
        ############
        # TODO Step 1: calculate and return covariance of residual S
        ############
        H = meas.sensor.get_H(track.x)
        P = track.P
        R = meas.R
        S = H * P * H.T + R
        return S

        ############
        # END student code
        ############