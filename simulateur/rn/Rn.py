import bpy
import logging
import itertools
import moveController
import sys
sys.path.insert(0, '../')
import pathConfig

logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)

class Rn:


	# Future rewards discount
    Y = 0.95
	# Exploration/exploitation ration (Learning ratio)
	ALPHA = 1e-2
    #ALPHA_Max = 1
	#ALPHA_Min = 1e-2 
	# 5 actions possibles:
	# ---------------------
	#   0=tourne a fond a gauche
	#   1=tourne un peu a gauche
	#   2=tout droit
	#   3=tourne a fond a droite
	#   4=tourne un peu a droite
	ACTIONS = [0, 1, 2, 3, 4]
	DEFAULT_ACTION = round(len(ACTIONS)/2)

    def __init__(self, y):
        self.alpha = self.ALPHA_Max
        self.y = y
        self.V = 0
		self.previousAction = self.DEFAULT_ACTION
        tf.reset_default_graph()
		self.sess = tf.Session()
		self.saver = tf.train.Saver()
        self._q_s_a = tf.placeholder(dtype=tf.float32, shape=(None, len(self.ACTIONS))

        self.make_network()
		
        
	def make_network():

        # input: angle, distance, hauteur, actionPrecedente => 4
		  inputs = tf.placeholder(dtype=tf.float32, shape=(None, 4)
        # outputs : autant que d'actions possibles (meme actions possibles quel que soit l'etat)
		  actions = tf.placeholder(dtype=tf.float32, shape=(None, len(self.ACTIONS))
        # recompense
		  rewards = tf.placeholder(dtype=tf.float32, shape=(None,1))

        # either use variable scope or attributes ???
		  with tf.variable_scope('policy'):
            # une seule couche de 4 neurones (autant que d'entrées), fully connected => dense
    			hidden = tf.layers.dense(inputs, 4, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
			   # couche de sortie,  autant que d'actions possibles sans fonction d'activation
            logits = tf.layers.dense(hidden, len(self.ACTIONS), activation=None, kernel_initializer = tf.contrib.layers.xavier_initializer())

			   # traitement de la sortie
            out = tf.sigmoid(logits, name="sigmoid")
			   cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(
				    labels=actions, logits=logits, name="cross_entropy")
			   loss = tf.reduce_sum(tf.multiply(rewards, cross_entropy, name="rewards"))

            # Autre façon de faire:
            #loss = tf.losses.mean_squared_error(self._q_s_a, logits)
            #self._optimizer = tf.train.AdamOptimizer().minimize(loss)
            
		  decay_rate=0.99
		  optimizer = tf.train.RMSPropOptimizer(ALPHA, decay=decay_rate).minimize(loss)

		  tf.summary.histogram("hidden_out", hidden)
		  tf.summary.histogram("logits_out", logits)
		  tf.summary.histogram("prob_out", out)
		  merged = tf.summary.merge_all()

		  # grads = tf.gradients(loss, [hidden_w, logit_w])
		  # return pixels, actions, rewards, out, opt, merged, grads
		  return inputs, actions, rewards, out, optimizer, merged
      
		# Autre facon de faire:
        #self._states = tf.placeholder(shape=[None, self._num_states], dtype=tf.float32)
        #self._q_s_a = tf.placeholder(shape=[None, self._num_actions], dtype=tf.float32)
        # create a couple of fully connected hidden layers
        #fc1 = tf.layers.dense(self._states, 50, activation=tf.nn.relu)
        #fc2 = tf.layers.dense(fc1, 50, activation=tf.nn.relu)
        #self._logits = tf.layers.dense(fc2, self._num_actions)
        
        
        
self._var_init = tf.global_variables_initializer()
        
	
	def start():
		tf.reset_default_graph()
		pix_ph, action_ph, reward_ph, out_sym, opt_sym, merged_sym = make_network(pixels_num, hidden_units)

		resume = True
		render = True

		sess = tf.Session()
		saver = tf.train.Saver()
		# writer = tf.summary.FileWriter('./log/train', sess.graph)

		weight_path = sys.argv[1]
		if resume:
		  # saver.restore(sess, tf.train.latest_checkpoint('./log/checkpoints'))
		  saver.restore(sess, tf.train.latest_checkpoint(weight_path))
		else:
		  sess.run(tf.global_variables_initializer())
		
		
	def _choose_action(self, state):
        if random.random() < self._eps:
            return random.randint(0, self._model.num_actions - 1)
        else:
            return np.argmax(self._model.predict_one(state, self._sess))
			
    def compute(pointilles):
        
		# par defaut angle=90, distance=0, hauteur=1, action precedente
		inputs = [self.previousAction, 90, 0, 1];
        last = len(pointilles)-1
		if len(pointilles) > 0:
			# On ne prend que le dernier (le plus haut)
			inputs = [self.previousAction, pointilles[last]["angle"], pointilles[last]["distance"], pointilles[last]["hauteur"]];
		            
		# normalize inputs histoire de ne pas donner inutilement du poids aux unes plus qu'aux autres
		for input in inputs:
			# angle is converted from a range of 0 to 180 to [-1, 1]
			input["angle"] = (input["angle"]-90)/90
	
		# flatten the inputs into a one dimension array
		inputs = list(itertools.chain.from_iterable(inputs))
		
        # traitement RN ici !!!
		
		result = self.sess.run(out_sym, feed_dict={pix_ph:x.reshape((-1,x.size))})
		# convert result to action
		action = result
        self.previousAction = action
		
        return action
	
	def applyReward(reward):
		self.V = 
        
        
        
    def predict_one(self, state, sess):
		return sess.run(self._logits, feed_dict={self._states:
                                                 state.reshape(1, self.num_states)})

    def predict_batch(self, states, sess):
        return sess.run(self._logits, feed_dict={self._states: states})
    
    def train_batch(self, sess, x_batch, y_batch):
        sess.run(self._optimizer, feed_dict={self._states: x_batch, self._q_s_a: y_batch})
    
    		
        