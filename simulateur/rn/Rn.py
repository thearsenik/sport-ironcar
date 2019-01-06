import logging
import sys
sys.path.insert(0, '../')
import config
import tensorflow as tf
import numpy as np
import random
import math


logging.basicConfig(filename=config.logFile,level=logging.DEBUG)
    
            
class Rn:


    # Future rewards discount
    Y = 0.95
    # Exploration/exploitation ration (Learning ratio)
    ALPHA = 0.01
    MIN_ALPHA = 0.01
    MAX_ALPHA = 1
    LAMBDA = 0.0001
    # how far we consider future reward shall be considered when computing qsa
    # 1 means all future states are inportant (may be divergent)
    # 0 means only the current reward is taken into account
    GAMMA = 0.99
    # 13 actions possibles:
    # ---------------------
    #   0=tourne a fond a gauche
    #   ...
    #   6=tout droit (action par defaut)
    #   ...
    #   12=tourne a fond a droite
    DEFAULT_PREVIOUS_ACTION = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    NB_ACTIONS = len(DEFAULT_PREVIOUS_ACTION)
    
    DEFAULT_INPUTS = [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    NB_INPUTS = len(DEFAULT_INPUTS)


    def __init__(self):
        self.alpha = 1
        self._steps = 0
        self.V = 0
        self.previousAction = self.DEFAULT_PREVIOUS_ACTION
        tf.reset_default_graph()
        self.sess = tf.Session()
        self.optimizer = None
        self.inputs = None
        self.actions = None
        self.rewards = None
        #self.saver = tf.train.Saver()
        self._q_s_a = None
        
        
    # cf https://github.com/adventuresinML/adventures-in-ml-code/blob/master/r_learning_tensorflow.py
    def _build_network(self):
        
        self.inputs = tf.placeholder(dtype=tf.float32, shape=(None, self.NB_INPUTS))
        self._q_s_a = tf.placeholder(dtype=tf.float32, shape=(None, self.NB_ACTIONS))
        # outputs : autant que d'actions possibles (on a toujours les meme actions possibles quel que soit l'etat)
        #self.actions = tf.placeholder(dtype=tf.float32, shape=(None, self.NB_ACTIONS))
        # recompense
        #rewards = tf.placeholder(dtype=tf.float32, shape=(None,1))

        
        #with tf.variable_scope('policy'):
        # trois couches de nb_inputs neurones (autant que d'entrees), fully connected => dense
        hidden1 = tf.layers.dense(self.inputs, self.NB_INPUTS, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
        hidden2 = tf.layers.dense(hidden1, self.NB_INPUTS, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
        hidden3 = tf.layers.dense(hidden2, self.NB_INPUTS, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
        # couche de sortie,  autant que d'actions possibles sans fonction d'activation
        self.actions = tf.layers.dense(hidden3, self.NB_ACTIONS, activation=None, kernel_initializer = tf.contrib.layers.xavier_initializer())

        # traitement de la sortie
        out = tf.sigmoid(self.actions, name="sigmoid")
        

        # façon de faire originelle:
        loss = tf.losses.mean_squared_error(self._q_s_a, self.actions)
        self._optimizer = tf.train.AdamOptimizer().minimize(loss)
        # Autre façon de faire:
        #cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(labels=actions, logits=self.actions, name="cross_entropy")
        #loss = tf.reduce_sum(tf.multiply(rewards, cross_entropy, name="rewards"))
        #decay_rate=0.99
        #self.optimizer = tf.train.RMSPropOptimizer(self.ALPHA, decay=decay_rate).minimize(loss)

        tf.summary.histogram("hidden_out", hidden3)
        tf.summary.histogram("logits_out", self.actions)
        tf.summary.histogram("prob_out", out)
        merged = tf.summary.merge_all()

        # grads = tf.gradients(loss, [hidden_w, logit_w])
        # return pixels, actions, rewards, out, optimizer, merged, grads
        return out, merged
        
        
    # resumeFromFile: indicate if we have to restart from stored data from a file
    def start(self, resumeFromFile):
        if self.sess != None:
            self.sess.close()
        
        tf.reset_default_graph()
        out_sym, merged_sym = self._build_network()

        # Init new session with default graph
        self.sess = tf.Session()
        
        # writer = tf.summary.FileWriter('./log/train', self.sess.graph)
        if resumeFromFile:
            weight_path = config.rnCheckpointsFile
            self.saver.restore(self.sess, tf.train.latest_checkpoint(weight_path))
        else:
            self.sess.run(tf.global_variables_initializer())
        

        
    # method used to process a new state provided by the environment
    def compute(self, inputs):
        
        # inputs are already well formatted

        ##### Traitement RN #####
        # Get the Rn output for the given input
        # In fact, as we are exploring, either get Rn output, either get random output...
        result = self._choose_action(inputs)

        return result
    

    # Replay a batch to train the nn.
    # each item of batch is composed of:
    #    - the inputs (angle, distance, height, the previous previous action (as flat array of all possible action))
    #    - the previous action
    #    - the reward
    #    - the next state as (new angle, new distance, new height, the action (as flat array of all possible action) that lead to this state (previous action)
    def replay(self, batch):
        
        states = np.array([val[0] for val in batch])
        notDeterminedNextState = np.zeros(self.NB_INPUTS)
        next_states = np.asarray([(notDeterminedNextState if val[3] is None else val[3]) for val in batch])
        # predict Q(s,a) given the batch of states
        q_s_a = self._predict_batch(states)
        # predict Q(s',a') - so that we can do gamma * max(Q(s'a')) below
        q_s_a_d = self._predict_batch(next_states)
        # setup training arrays
        x = np.zeros((len(batch), self.NB_INPUTS))
        y = np.zeros((len(batch), self.NB_ACTIONS))
        for i, b in enumerate(batch):
            state, action, reward, next_state = b[0], b[1], b[2], b[3]
            # get the current q values for all actions in state
            current_q = q_s_a[i]
            # update the q value for action
            if next_state is None:
                # in this case, the game completed after action, so there is no max Q(s',a')
                # prediction possible
                current_q[np.argmax(action)] = reward
            else:
                current_q[np.argmax(action)] = reward + self.GAMMA * np.amax(q_s_a_d[i])
            x[i] = state
            y[i] = current_q
        self._train_batch(x, y)
        
        
    # As we are exploring, either get Rn output, either get random output by comparing
    # random value to a predetermined value alpha...
    # At the beginning as there is no knowledge on the environment we explore a lot and set alpha to 1.
    # At each step we reduce the probability to choose a random output and reduce alpha value      
    def _choose_action(self, inputs):
        # exponentially decay the alpha value at each choice
        self._steps += 1
        self.alpha = self.MIN_ALPHA + (self.MAX_ALPHA - self.MIN_ALPHA) * math.exp(-self.LAMBDA * self._steps)

        if random.random() < self.alpha:
            actions = [0]*self.NB_ACTIONS
            choosen_index = random.randint(0, self.NB_ACTIONS - 1)
            actions[choosen_index] = 1
            return np.array(actions)
        else:
            return self._predict_one(inputs)
        
    def _predict_one(self, inputs):
        return self.sess.run(self.actions, feed_dict={self.inputs: inputs.reshape(1, self.NB_INPUTS)})

    def _predict_batch(self, inputs):
        return self.sess.run(self.actions, feed_dict={self.inputs: np.array(inputs)})
    
    def _train_batch(self, x_batch, y_batch):
        return self.sess.run(self._optimizer, feed_dict={self.inputs: x_batch, self._q_s_a: y_batch})
        