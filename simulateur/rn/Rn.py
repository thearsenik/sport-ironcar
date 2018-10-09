import bpy
import logging
import moveController
import sys
sys.path.insert(0, '../')
import pathConfig

logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)

class Rn:


	# Future rewards discount
    Y = 0.95
	# Learning ratio
    ALPHA = 1e-3
	# 5 actions possibles:
	# ---------------------
	#   0=tourne a fond a gauche
	#   1=tourne un peu a gauche
	#   2=tout droit
	#   3=tourne a fond a droite
	#   4=tourne un peu a droite
	ACTIONS = [0, 1, 2, 3, 4]
	DEFAULT_ACTION = round(len(ACTIONS)/2)

    def __init__(self, alpha, y):
        self.alpha = alpha
        self.y = y
        self.V = 0
		self.previousAction = self.DEFAULT_ACTION
		self.sess = tf.Session()
		self.saver = tf.train.Saver()
        
        
    def reset(self):
        self.V = 0
		self.make_network(4, 200)
		tf.reset_default_graph()
		self.sess = tf.Session()
		self.saver = tf.train.Saver()
		
        
	def make_network(inputNb, hidden_units):

		  inputs = tf.placeholder(dtype=tf.float32, shape=(None, inputNb)    
		  actions = tf.placeholder(dtype=tf.float32, shape=(None, len(self.ACTIONS))
		  rewards = tf.placeholder(dtype=tf.float32, shape=(None,1))

		  with tf.variable_scope('policy'):
			hidden = tf.layers.dense(inputs, hidden_units, activation=tf.nn.relu, kernel_initializer = tf.contrib.layers.xavier_initializer())
			logits = tf.layers.dense(hidden, 1, activation=None, kernel_initializer = tf.contrib.layers.xavier_initializer())

			out = tf.sigmoid(logits, name="sigmoid")
			cross_entropy = tf.nn.sigmoid_cross_entropy_with_logits(
				labels=actions, logits=logits, name="cross_entropy")
			loss = tf.reduce_sum(tf.multiply(rewards, cross_entropy, name="rewards"))

		  # lr=1e-4
		  lr=1e-3
		  decay_rate=0.99
		  opt = tf.train.RMSPropOptimizer(ALPHA, decay=decay_rate).minimize(loss)

		  tf.summary.histogram("hidden_out", hidden)
		  tf.summary.histogram("logits_out", logits)
		  tf.summary.histogram("prob_out", out)
		  merged = tf.summary.merge_all()

		  # grads = tf.gradients(loss, [hidden_w, logit_w])
		  # return pixels, actions, rewards, out, opt, merged, grads
		  return pixels, actions, rewards, out, opt, merged
        
	
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
		
		
    def compute(pointilles):
        
		# par defaut angle=90, distance=0, hauteur=1, action precedente
		inputs = [self.previousAction, 90, 0, 1];
        last = len(pointilles)-1
		if len(pointilles) > 0:
			# On ne prend que le dernier (le plus haut)
			inputs = [self.previousAction, pointilles[last]["angle"], pointilles[last]["distance"], pointilles[last]["hauteur"]];
		            
        # traitement RN ici !!!
		result = self.sess.run(out_sym, feed_dict={pix_ph:x.reshape((-1,x.size))})
		# convert result to action
		action = result
        self.previousAction = action
		
        return action
	
	def applyReward(reward):
		self.V = 
		
        