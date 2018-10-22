import bpy
import logging
import itertools
import RnMemory
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
	#   2=tout droit (action par defaut)
	#   3=tourne a fond a droite
	#   4=tourne un peu a droite
	DEFAULT_PREVIOUS_ACTION = [0, 0, 1, 0, 0]
	#Input :
	# angle in degrees-90/90,
	# centered and normalized x (0 when at the center of screen, -1 left, +1 right),
	# normalized y from the bottom of the screen (from 1 at the top to 0 at the bottom of the screen),
	# was action 0 previously selected,
	# was action 1 previously selected,
	# ...
	# was action n previously selected
	DEFAULT_INPUT = [0, 0, 1, 0, 0, 1, 0, 0]


    def __init__(self, y):
        self.alpha = self.ALPHA_Max
        self.y = y
        self.V = 0
		self.previousAction = self.DEFAULT_ACTION
        tf.reset_default_graph()
		self.sess = tf.Session()
		self.optimizer = None
		self.inputs = None
		self.actions = None
		self.rewards = None
		self.saver = tf.train.Saver()
        self._q_s_a = tf.placeholder(dtype=tf.float32, shape=(None, len(self.ACTIONS))
		self.memory = RnMemory(50000)

        self.make_network()
		
        
	def make_network():

        # input: angle, distance, hauteur, actionPrecedente => 4
		  inputs = tf.placeholder(dtype=tf.float32, shape=(None, 4)
        # outputs : autant que d'actions possibles (on a toujours les meme actions possibles quel que soit l'etat)
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
		  self.optimizer = tf.train.RMSPropOptimizer(ALPHA, decay=decay_rate).minimize(loss)

		  tf.summary.histogram("hidden_out", hidden)
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
        
        
        
	
	def start(resume, render):
		tf.reset_default_graph()
		out_sym, merged_sym = self.make_network()

		# writer = tf.summary.FileWriter('./log/train', self.sess.graph)

		weight_path = pathConfig.rnCheckpointsFile
		if resume:
		  # saver.restore(self.sess, tf.train.latest_checkpoint('./log/checkpoints'))
		  saver.restore(self.sess, tf.train.latest_checkpoint(weight_path))
		else:
		  sess.run(tf.global_variables_initializer())
		
		
	def _choose_action(self, state):
        if random.random() < self._eps:
            return random.randint(0, self._model.num_actions - 1)
        else:
            return np.argmax(self._model.predict_one(state, self._sess))
			
	# normalize angle from -1 (0°) to +1 (180°)
	def _normalizeAngle(angleInDegrees):
		return (angleInDegrees-90)/90
		
		
	# method used to process a new state provided by the environment
    def compute(pointilles):
        
		##### Formatage des inputs #####
		# chaque entree va etre de la forme : angle/180, distance au centre, hauteur, wasPreviousActionAction1, wasPreviousActionAction2, ... , wasPreviousActionActionN
		# par defaut angle=90, distance=0, hauteur=1, action precedente = index nbAction/2
		inputs = [DEFAULT_INPUT];
		
        last = len(pointilles)-1
		if len(pointilles) > 0:
			# On ne prend que le dernier pointille de la liste (le plus haut sur l'image)
			inputs = [_normalizeAngle([pointilles[last]["angle"]), pointilles[last]["distance"], pointilles[last]["hauteur"]];
		            
	
		# flatten the inputs into a one dimension array
		inputs = list(itertools.chain.from_iterable(inputs))
		#inputs = inputs.reshape((-1,inputs.size))
		
		
		##### Traitement RN #####
		#result = self.sess.run(self.actions, feed_dict={self.inputs:inputs})
		result = _train_batch(self, self.sess, inputs, self.actions)
		# Store result as previous action choice
        self.previousAction = result
		# convert result to action. Simply return index of the most significant output.
		action = result.index(max(result))
		
		# store result in memory for batch replay
		self.memory.add_sample((inputs[0], action, reward, next_state))
		
        return action
	
	
	def _applyReward(reward):
		#self.V = 
        
        
        
    def _predict_one(self, state, sess):
		return sess.run(self._logits, feed_dict={self._states:
                                                 state.reshape(1, self.num_states)})

    def _predict_batch(self, states, sess):
        return sess.run(self._logits, feed_dict={self._states: states})
    
    def _train_batch(self, sess, x_batch, y_batch):
        return sess.run(self._optimizer, feed_dict={self._states: x_batch, self._q_s_a: y_batch})
    
    		
        