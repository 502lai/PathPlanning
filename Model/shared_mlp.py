import numpy as np
import tensorflow as tf
from .util import model
from .util import shared


@shared
class StateModel:
    def __init__(self, eval_model: bool, size_splits, n_layers):
        self.d_obs, d_goal = size_splits
        self.obs = tf.placeholder(tf.float64, (None, self.d_obs), name='obs')
        self.goal = tf.placeholder(tf.float64, (None, d_goal), name='goal')
        layer = self.obs
        for n_layer in n_layers:
            layer = tf.layers.dense(layer, n_layer, activation=tf.nn.relu, trainable=eval_model,
                                    kernel_initializer=tf.random_normal_initializer(0., .1),
                                    bias_initializer=tf.constant_initializer(0.1))
        self.out = tf.concat((layer, self.goal), axis=1)

    def __call__(self, state):
        obs_state, goal_state = np.split(state, indices_or_sections=(self.d_obs,), axis=1)
        return {self.obs: obs_state, self.goal: goal_state}


@model
class ActorModel:
    def __init__(self, special_info, eval_model: bool):
        """eval_model不允许提供默认参数，否则导致__new__无法获取该默认参数，且必须以字典方式提供参数"""
        self.state = StateModel(eval_model, special_info['size_splits'], special_info['state_n_layers'])
        layer = self.state.out
        for n_layer in special_info['actor_n_layers']:
            layer = tf.layers.dense(layer, n_layer, activation=tf.nn.relu, trainable=eval_model,
                                    kernel_initializer=tf.random_normal_initializer(0., .1),
                                    bias_initializer=tf.constant_initializer(0.1))
        self.out = tf.layers.dense(layer, 1, activation=tf.nn.tanh, trainable=eval_model,
                                   kernel_initializer=tf.random_normal_initializer(0., .1),
                                   bias_initializer=tf.constant_initializer(0.1))

    def __call__(self, state):
        return self.state(state)


@model
class CriticModel:
    def __init__(self, action, special_info: dict, eval_model: bool):
        """eval_model不允许提供默认参数，否则导致__new__无法获取该默认参数，且必须以字典方式提供参数"""
        """action是ActorModel的输出"""
        self.state = StateModel(eval_model, special_info['size_splits'], special_info['state_n_layers'])
        layer = tf.concat((self.state.out, action), axis=1)
        for n_layer in special_info['critic_n_layers']:
            layer = tf.layers.dense(layer, n_layer, activation=tf.nn.relu, trainable=eval_model,
                                    kernel_initializer=tf.random_normal_initializer(0., .1),
                                    bias_initializer=tf.constant_initializer(0.1))
        self.out = tf.layers.dense(layer, 1, trainable=eval_model,
                                   kernel_initializer=tf.random_normal_initializer(0., .1),
                                   bias_initializer=tf.constant_initializer(0.1))

    def __call__(self, state):
        return self.state(state)


@model
class ActionModel:
    def __init__(self, n_actions, special_info: dict, eval_model: bool):
        """eval_model不允许提供默认参数，否则导致__new__无法获取该默认参数，且必须以字典方式提供参数"""
        self.state = StateModel(eval_model, special_info['size_splits'], special_info['state_n_layers'])
        layer = self.state.out
        for n_layer in special_info['actor_n_layers']:
            layer = tf.layers.dense(layer, n_layer, activation=tf.nn.relu, trainable=eval_model,
                                    kernel_initializer=tf.random_normal_initializer(0., .1),
                                    bias_initializer=tf.constant_initializer(0.1))
        self.out = tf.layers.dense(layer, n_actions, activation=tf.nn.softmax, trainable=eval_model,
                                   kernel_initializer=tf.random_normal_initializer(0., .1),
                                   bias_initializer=tf.constant_initializer(0.1))

    def __call__(self, state):
        return self.state(state)


@model
class ValueModel:
    def __init__(self, n_actions, special_info: dict, eval_model: bool):
        """eval_model不允许提供默认参数，否则导致__new__无法获取该默认参数，且必须以字典方式提供参数"""
        self.state = StateModel(eval_model, special_info['size_splits'], special_info['state_n_layers'])
        layer = self.state.out
        for n_layer in special_info['critic_n_layers']:
            layer = tf.layers.dense(layer, n_layer, activation=tf.nn.relu, trainable=eval_model,
                                    kernel_initializer=tf.random_normal_initializer(0., .1),
                                    bias_initializer=tf.constant_initializer(0.1))
        self.out = tf.layers.dense(layer, n_actions, trainable=eval_model,
                                   kernel_initializer=tf.random_normal_initializer(0., .1),
                                   bias_initializer=tf.constant_initializer(0.1))

    def __call__(self, state):
        return self.state(state)
