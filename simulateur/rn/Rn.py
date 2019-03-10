import logging
import sys
sys.path.insert(0, '../')
import config
from tensorflow.python.tools import inspect_checkpoint as chkp
import tensorflow as tf
import numpy as np
import random



logging.basicConfig(filename=config.logFile,level=config.logLevelPlayer, format='%(asctime)s %(message)s')
    
            
class Rn:


    # Future rewards discount
    Y = 0.95
    # Exploration/exploitation ration (Learning ratio)
    ALPHA = 0.01
    MIN_ALPHA = 0.1
    MAX_ALPHA = 0.85
    LAMBDA = 0.0001
    NB_EPISODE = 3000
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
    DEFAULT_PREVIOUS_ACTION = [0, 1, 0]
    NB_ACTIONS = len(DEFAULT_PREVIOUS_ACTION)
    
    DEFAULT_INPUTS = [0, 0, 1, 0, 1, 0]
    NB_INPUTS = len(DEFAULT_INPUTS)
    
    NB_NEURON_BY_LAYER = NB_INPUTS * 4


    def __init__(self, performTraining):
        self.isTrainingOn = performTraining
        self.alpha = 1
        self._steps = 0
        self.V = 0
        self.previousAction = self.DEFAULT_PREVIOUS_ACTION
        tf.reset_default_graph()
        self.sess = None
        self.optimizer = None
        self.inputs = None
        self.hidden1 = None
        self.hidden2 = None
        self.hidden3 = None
        self.actions = None
        self.rewards = None
        self.saver = None
        self._q_s_a = None
        self.num_episode = 0
        self._start()
        
        
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
        self.hidden1 = tf.layers.dense(self.inputs, self.NB_NEURON_BY_LAYER, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
        self.hidden2 = tf.layers.dense(self.hidden1, self.NB_NEURON_BY_LAYER, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
#        self.hidden3 = tf.layers.dense(self.hidden2, self.NB_NEURON_BY_LAYER, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
        # couche de sortie,  autant que d'actions possibles sans fonction d'activation
        # on voudrait que la sortie colle avec l'esperance de reward ?
        self.actions = tf.layers.dense(self.hidden2, self.NB_ACTIONS, activation=None, kernel_initializer = tf.contrib.layers.xavier_initializer())

        # traitement de la sortie pour avoir que un 1 et des 0       
        #threshold_to_max = tf.less_equal(tf.reduce_max(self.actions), self.actions)
        #cast booleans to float32 (True => 1, False => 0)
        #self.out = tf.cast(threshold_to_max, tf.float32)
        

        # façon de faire originelle:
        loss = tf.losses.mean_squared_error(self._q_s_a, self.actions)
        self._optimizer = tf.train.AdamOptimizer().minimize(loss)
        # Autre façon de faire:
        #cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(labels=actions, logits=self.actions, name="cross_entropy")
        #loss = tf.reduce_sum(tf.multiply(rewards, cross_entropy, name="rewards"))
        #decay_rate=0.99
        #self.optimizer = tf.train.RMSPropOptimizer(self.ALPHA, decay=decay_rate).minimize(loss)

#        tf.summary.histogram("input_data", self.inputs)
#        tf.summary.histogram("hidden_1", self.hidden1)
#        tf.summary.histogram("hidden_2", self.hidden2)
#        tf.summary.histogram("hidden_3", self.hidden3)
#        tf.summary.histogram("sortie", self.actions)
#        tf.summary.histogram("action", self.out)
        merged = tf.summary.merge_all()
        
        self.saver = tf.train.Saver()

        # grads = tf.gradients(loss, [hidden_w, logit_w])
        # return pixels, actions, rewards, out, optimizer, merged, grads
        return merged
        
        
    
    def _start(self):
        if self.sess != None:
            self.sess.close()
        
        tf.reset_default_graph()
        merged_sym = self._build_network()

        # Init new session with default graph
        self.sess = tf.Session()
        
        # writer = tf.summary.FileWriter('./log/train', self.sess.graph)
        try:
            weights = open(config.rnCheckpointsFile+'.index', 'r')
            weights.close
            logging.debug("RN initialized from file :"+config.rnCheckpointsFile)
            self.saver.restore(self.sess, tf.train.latest_checkpoint(config.rnCheckpointsDir))
        except FileNotFoundError:
            logging.debug("RN initialized randomly...")
            self.sess.run(tf.global_variables_initializer())
        
    def startNewGame(self):
        self.num_episode += 1
        self._steps = 0
        

    #save model
    def save(self):
        self.saver.save(self.sess, config.rnCheckpointsFile)
        
    # method used to process a new state provided by the environment
    def compute(self, inputs):
        
        # inputs are already well formatted

        ##### Traitement RN #####
        # Get the Rn output for the given input
        # In fact, as we are exploring, either get Rn output, either get random output...
        result, isRandomChoice = self._choose_action(inputs)

        return result, isRandomChoice
    

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
        
        #logging.info("AFTER TRAIN BATCH...")
        self._log_weights()
        
        
    # As we are exploring, either get Rn output, either get random output by comparing
    # random value to a predetermined value alpha...
    # At the beginning as there is no knowledge on the environment we explore a lot and set alpha to 1.
    # At each step we reduce the probability to choose a random output and reduce alpha value      
    def _choose_action(self, inputs):
        # exponentially decay the alpha value at each choice
        self._steps += 1
        #alpha = self.MIN_ALPHA + (self.MAX_ALPHA - self.MIN_ALPHA) * max(0, (1-self.num_episode/self.NB_EPISODE))
        #alpha = 0.1
        alpha = 0.1 + (0.9) * max(0, (1-self.num_episode/80))

        logging.debug("alpha="+str(alpha))
        if self.isTrainingOn and random.random() < alpha:
            logging.debug("step="+str(self._steps)+" ACTION ALEATOIRE")
            actions = [0]*self.NB_ACTIONS
            choosen_index = random.randint(0, self.NB_ACTIONS - 1)
            actions[choosen_index] = 1
            return np.array(actions), True
        else:
            logging.debug("step="+str(self._steps)+" ACTION CALCULEE")
            return self._predict_one(inputs), False
        
    def _predict_one(self, inputs):
        logging.info("PREDICT ONE !!!")
        result = self.sess.run(self.actions, feed_dict={self.inputs: inputs.reshape(1, self.NB_INPUTS)})
        
        self._log_weights()
        #var = [v for v in tf.trainable_variables() if v.name == "hidden1/weights:0"][0]
        #logging.info("hidden1 : %s" % self.sess.run(self.hidden1.eval())
        #logging.info("hidden2 : %s" % self.hidden2.eval())
        #logging.info("hidden3 : %s" % self.hidden3.eval())
#        logging.info("output : %s" % self.actions.eval())
        return result

    def _predict_batch(self, inputs):
        #logging.info("PREDICT BATCH !!!")
        self._log_weights()
            
        return self.sess.run(self.actions, feed_dict={self.inputs: np.array(inputs)})
    
    def _train_batch(self, x_batch, y_batch):
        #logging.info("TRAIN BATCH !!!")
        self._log_weights()
            
        return self.sess.run(self._optimizer, feed_dict={self.inputs: x_batch, self._q_s_a: y_batch})
    
    def _log_weights(self):
        if False:
           for v in tf.trainable_variables():
               logging.info(v.name+":")
               logging.info(self.sess.run(v))
            