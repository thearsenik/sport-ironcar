import logging
import sys
sys.path.insert(0, '../')
import pathConfig
import tensorflow as tf
import numpy as np
import random


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)
    
            
class Rn:


    # Future rewards discount
    Y = 0.95
    # Exploration/exploitation ration (Learning ratio)
    ALPHA = 0.01
    #ALPHA_Max = 1
    #ALPHA_Min = 1e-2 
    # 5 actions possibles:
    # ---------------------
    #   0=tourne a fond a gauche
    #   1=tourne un peu a gauche
    #   2=tout droit (action par defaut)
    #   3=tourne a fond a droite
    #   4=tourne un peu a droite
    DEFAULT_PREVIOUS_ACTION = [0, 0, 1, 0, 0]
    NB_ACTIONS = len(DEFAULT_PREVIOUS_ACTION)



    def __init__(self):
        self.alpha = 1
        self.V = 0
        self.previousAction = self.DEFAULT_PREVIOUS_ACTION
        tf.reset_default_graph()
        self.sess = tf.Session()
        self.optimizer = None
        self.inputs = None
        self.actions = None
        self.rewards = None
        #self.saver = tf.train.Saver()
        self._q_s_a = tf.placeholder(dtype=tf.float32, shape=(None, self.NB_ACTIONS))

        self._make_network()
        
        
    def _make_network(self):

        # input: angle, distance, hauteur, actionPrecedentesPossibles => 8
        nb_inputs = 3+self.NB_ACTIONS
        inputs = tf.placeholder(dtype=tf.float32, shape=(None, nb_inputs))
        # outputs : autant que d'actions possibles (on a toujours les meme actions possibles quel que soit l'etat)
        actions = tf.placeholder(dtype=tf.float32, shape=(None, self.NB_ACTIONS))
        # recompense
        rewards = tf.placeholder(dtype=tf.float32, shape=(None,1))

        # either use variable scope or attributes ???
        with tf.variable_scope('policy'):
            # trois couches de nb_inputs neurones (autant que d'entrees), fully connected => dense
            hidden1 = tf.layers.dense(inputs, nb_inputs, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
            hidden2 = tf.layers.dense(hidden1, nb_inputs, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
            hidden3 = tf.layers.dense(hidden2, nb_inputs, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
            # couche de sortie,  autant que d'actions possibles sans fonction d'activation
            logits = tf.layers.dense(hidden3, self.NB_ACTIONS, activation=None, kernel_initializer = tf.contrib.layers.xavier_initializer())

            # traitement de la sortie
            out = tf.sigmoid(logits, name="sigmoid")
            cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(labels=actions, logits=logits, name="cross_entropy")
            loss = tf.reduce_sum(tf.multiply(rewards, cross_entropy, name="rewards"))

            # Autre façon de faire:
            #loss = tf.losses.mean_squared_error(self._q_s_a, logits)
            #self._optimizer = tf.train.AdamOptimizer().minimize(loss)
            decay_rate=0.99
            self.optimizer = tf.train.RMSPropOptimizer(self.ALPHA, decay=decay_rate).minimize(loss)

        tf.summary.histogram("hidden_out", hidden3)
        tf.summary.histogram("logits_out", logits)
        tf.summary.histogram("prob_out", out)
        merged = tf.summary.merge_all()

        # grads = tf.gradients(loss, [hidden_w, logit_w])
        # return pixels, actions, rewards, out, optimizer, merged, grads
        return out, merged
      
            # Autre facon de faire:
            #self._states = tf.placeholder(shape=[None, self._num_states], dtype=tf.float32)
            #self._q_s_a = tf.placeholder(shape=[None, self._num_actions], dtype=tf.float32)
            # create a couple of fully connected hidden layers
            #fc1 = tf.layers.dense(self._states, 50, activation=tf.nn.relu)
            #fc2 = tf.layers.dense(fc1, 50, activation=tf.nn.relu)
            #self._logits = tf.layers.dense(fc2, self._num_actions)
        
        
    
    def start(self, resume, render):
        tf.reset_default_graph()
        out_sym, merged_sym = self.make_network()

        # writer = tf.summary.FileWriter('./log/train', self.sess.graph)

        weight_path = pathConfig.rnCheckpointsFile
        if resume:
          # saver.restore(self.sess, tf.train.latest_checkpoint('./log/checkpoints'))
          self.saver.restore(self.sess, tf.train.latest_checkpoint(weight_path))
        else:
          self.sess.run(tf.global_variables_initializer())
        

        
    # method used to process a new state provided by the environment
    def compute(self, inputs):
        
        # inputs are already well formatted

        ##### Traitement RN #####
        # Get the Rn output for the given input
        # In fact, as we are exploring, either get Rn output either get random...
        result = self._choose_action(inputs)

        return result
    

    # Replay a batch to train the nn.
    # each item of batch is composed of:
    #    - the inputs (angle, distance, height, the previous previous action (as array of all possible action))
    #    - the previous action
    #    - the reward
    #    - the next state as (new angle, new distance, new height, the action (as array of all possible action) that lead to this state (previous action)
    def replay(self, batch):
        
        states = np.array([val[0] for val in batch])
        next_states = np.array([(np.zeros(4) if val[3] is None else val[3]) for val in batch])
        # predict Q(s,a) given the batch of states
        q_s_a = self._predict_batch(states, self.sess)
        # predict Q(s',a') - so that we can do gamma * max(Q(s'a')) below
        q_s_a_d = self._predict_batch(next_states, self.sess)
        # setup training arrays
        x = np.zeros((len(batch), 4))
        y = np.zeros((len(batch), self.NB_ACTIONS))
        for i, b in enumerate(batch):
            state, action, reward, next_state = b[0], b[1], b[2], b[3]
            # get the current q values for all actions in state
            current_q = q_s_a[i]
            # update the q value for action
            if next_state is None:
                # in this case, the game completed after action, so there is no max Q(s',a')
                # prediction possible
                current_q[action] = reward
            else:
                current_q[action] = reward + self.alpha * np.amax(q_s_a_d[i])
            x[i] = state
            y[i] = current_q
        self.train_batch(self.sess, x, y)
        
        
        
                
    def _choose_action(self, inputs):
        if random.random() < self._eps:
            choosen_index = random.randint(0, self.NB_ACTIONS - 1)
            actions = [0]*self.NB_ACTIONS
            actions[choosen_index] = 1
        else:
            return self._predict_one(inputs)
        
    def _predict_one(self, inputs):
        return self.sess.run(self._logits, feed_dict={self.inputs: inputs })
                                                # feed_dict={self.inputs: inputs.reshape(1, self.num_states)})

    def _predict_batch(self, inputs):
        return self.sess.run(self._logits, feed_dict={self._states: inputs})
    
    def _train_batch(self, x_batch, y_batch):
        return self.sess.run(self._optimizer, feed_dict={self._states: x_batch, self._q_s_a: y_batch})
        