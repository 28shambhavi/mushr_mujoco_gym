from typing import Dict, Union

import numpy as np

import gymnasium as gym
from gymnasium import utils
from gymnasium.envs.mujoco import MujocoEnv
from gymnasium.spaces import Box
import importlib_resources as pkg_resources

import mujoco


from scipy.spatial.transform import Rotation as R


DEFAULT_CAMERA_CONFIG = {
    "trackbodyid": -1,
    "distance": 4.0,
}


class MushrBlockEnv(MujocoEnv, utils.EzPickle):

    """
    qpos order(21,): [Car 3D cartesian(x,y,z), Car quaternion(w,x,y,z), joint angles(7 joints), block 3d cartesian (x,y,z), block quaternion(w,x,y,z)]
    qvel order(19,): [Car 3D velocity(x,y,z), Car 3D angular velocity(x,y,z), joint velocities(7 joints), block 3D velocity(x,y,z), block 3D angular velocity(x,y,z)]

    Observation space: (x,y, Th) of block wrt to frame of car
    """

    metadata = {
        "render_modes": [
            "human",
            "rgb_array",
            "depth_array",
        ],
    }

    def __init__(
        self,
        xml_file: str = "block.xml",
        frame_skip: int = 50,
        default_camera_config: Dict[str, Union[float, int]] = DEFAULT_CAMERA_CONFIG,
        cost_function = None,
        **kwargs
    ):
        
        utils.EzPickle.__init__(
            self,
            xml_file,
            frame_skip,
            default_camera_config,
            **kwargs,
        )
        
        if cost_function is not None:
            self._get_rew = cost_function
        else:
            self._get_rew = self._default_get_rew

        observation_space = Box(low=-np.inf, high=np.inf, shape=(12,), dtype=np.float64)

        with pkg_resources.path('mushr_mujoco_gym.include.models', xml_file) as xml_path:
            model_path = str(xml_path)

        MujocoEnv.__init__(
            self,
            model_path,
            frame_skip,
            observation_space=observation_space,
            default_camera_config=default_camera_config,
            **kwargs,
        )

        # Action is [turning angle, velocity]
        self.action_space = Box(low=np.array([-0.33, 0]), high=np.array([0.33, 1.2]), dtype=np.float64)

        self.metadata = {
            "render_modes": [
                "human",
                "rgb_array",
                "depth_array",
            ],
            "render_fps": int(np.round(1.0 / self.dt)),
        }

    def step(self, action):
        """
        action: [angle, velocity]
        """

        self.do_simulation(action, self.frame_skip)

        observation = self._get_obs()
        reward, reward_info = self._get_rew(action)
        info = reward_info

        if self.render_mode == "human":
            self.render()

        return observation, reward, False, False, info

    def _default_get_rew(self, action):
        return 0, {}

    def set_init_states(self, init_states):
        '''
        init_states represent initial value for observed states 
        
        car_pos - states[0:2]
        car_quats - states[2:6]
        block_pos - states[6:8]
        block_quats - states[8:12]
        '''
        qpos = self.unwrapped.data.qpos.flatten()
        qvel = self.unwrapped.data.qvel.flatten()
        qpos[0:2] = init_states[0:2]
        qpos[3:7] = init_states[2:6]
        qpos[14:16] = init_states[6:8]
        qpos[16:20] = init_states[8:12]
        self.set_state(qpos, qvel)
        observation = self._get_obs()
        return observation

    def reset_model(self):
        qpos = self.init_qpos 
        qvel = self.init_qvel

        self.set_state(qpos, qvel)

        observation = self._get_obs()

        return observation

    def _get_obs(self):
        # pos = self.unwrapped.data.qpos
        # vel = self.unwrapped.data.qvel

        position = self.unwrapped.data.qpos.flatten()
        velocity = self.unwrapped.data.qvel.flatten()
        car = position[:7].copy()
        block = position[-7:].copy()
        car_vel = velocity[:6].copy()
        block_vel = velocity[-6:].copy()

        # block_pos, block_quat = np.array(block[:3]), R.from_quat(np.roll(block[-4:], -1))
        # block_pos[2] = 0
        # car_pos, car_quat = np.array(car[:3]), R.from_quat(np.roll(car[-4:], -1))

        # delta_world = block_pos - car_pos

        # car_quat_inv = car_quat.inv()

        # delta_xy = car_quat_inv.apply(delta_world)
        # rel_orientation = car_quat_inv * block_quat

        # b_angle_wrt_c = rel_orientation.as_euler('xyz', degrees=False)[2]
        # car_angle = car_quat.as_euler('xyz', degrees=False)[2]
        
        car_no_z = np.concatenate([car[:2], car[-4:]])
        block_no_z = np.concatenate([block[:2], block[-4:]])
        car_vel = np.concatenate([car_vel[:2], car_vel[-3:-1]])
        block_vel = np.concatenate([block_vel[:2], block_vel[-3:-1]])
        return np.concatenate([np.array(block_no_z),
                                np.array(car_no_z),
                                np.array(block_vel),
                                np.array(car_vel)])
                            #   np.array([car_pos[0], car_pos[1], car_angle])])