from gymnasium.envs.registration import register

register(
    id='MushrBlock-v0',
    entry_point='mushr_mujoco_gym.envs.block:MushrBlockEnv',
    max_episode_steps=1000,
)

register(
    id='MultiAgentMushrBlockObstacles-v0',
    entry_point='mushr_mujoco_gym.envs.multi_robot_custom_block_obstacles:MultiAgentMushrBlockEnv',
    max_episode_steps=1000,
)