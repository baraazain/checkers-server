import tensorflow as tf
from tensorflow.keras import regularizers
from tensorflow.keras.layers import Input, Dense, Conv2D, Flatten, BatchNormalization, LeakyReLU, add
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.optimizers import Adam


run_folder = 'data/alphazero/models/'


def softmax_cross_entropy_with_logits(y_true, y_pred):

    p = y_pred
    pi = y_true

    zero = tf.zeros(shape = tf.shape(pi), dtype=tf.float32)
    where = tf.equal(pi, zero)

    negatives = tf.fill(tf.shape(pi), -100.0) 
    p = tf.where(where, negatives, p)

    loss = tf.nn.softmax_cross_entropy_with_logits(labels = pi, logits = p)

    return loss


class NeuralNetwork:
    def __init__(self, reg_const, learning_rate, input_dim, output_dim, hidden_layers):
        self.reg_const = reg_const
        self.learning_rate = learning_rate
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_layers = hidden_layers
        self.numLayers = len(hidden_layers)
        self.model = self.build_model()

    def cnn_layer(self, input_block, filters, kernel_size):
        layer = Conv2D(filters=filters
                       , kernel_size=kernel_size
                       , data_format="channels_first", padding='same'
                       , use_bias=False, activation='linear'
                       , kernel_regularizer=regularizers.l2(self.reg_const))(input_block)

        layer = BatchNormalization(axis=1)(layer)

        layer = LeakyReLU()(layer)

        return layer

    def residual_layer(self, input_block, filters, kernel_size):
        layer = self.cnn_layer(input_block, filters, kernel_size)

        layer = Conv2D(filters=filters
                       , kernel_size=kernel_size
                       , data_format="channels_first", padding='same'
                       , use_bias=False, activation='linear'
                       , kernel_regularizer=regularizers.l2(self.reg_const))(layer)

        layer = add([input_block, layer])

        layer = LeakyReLU()(layer)

        return layer

    def value_head(self, input_block):
        head = Conv2D(filters=1, kernel_size=(1, 1), data_format="channels_first"
            , padding='same', use_bias=False, activation='linear'
            , kernel_regularizer=regularizers.l2(self.reg_const))(input_block)

        head = BatchNormalization(axis=1)(head)

        head = LeakyReLU()(head)

        head = Flatten()(head)

        head = Dense(20, use_bias=False, activation='linear'
                     , kernel_regularizer=regularizers.l2(self.reg_const))(head)

        head = Dense(1, use_bias=False, activation='tanh'
                     , kernel_regularizer=regularizers.l2(self.reg_const), name='value_head')(head)

        return head

    def policy_head(self, input_block):
        head = Conv2D(filters=2, kernel_size=(1, 1), data_format="channels_first"
            , padding='same', use_bias=False, activation='linear'
            , kernel_regularizer=regularizers.l2(self.reg_const))(input_block)

        head = BatchNormalization(axis=1)(head)

        head = LeakyReLU()(head)

        head = Flatten()(head)

        head = Dense(self.output_dim, use_bias=False, activation='linear'
                     , kernel_regularizer=regularizers.l2(self.reg_const), name='policy_head')(head)

        return head

    def build_model(self):
        main_input = Input(shape=self.input_dim, name='main_input')

        layers = self.cnn_layer(main_input, self.hidden_layers[0]['filters'], self.hidden_layers[0]['kernel_size'])

        if len(self.hidden_layers) > 1:
            for hidden in self.hidden_layers[1:]:
                layers = self.residual_layer(layers, hidden['filters'], hidden['kernel_size'])

        value_head = self.value_head(layers)

        policy_head = self.policy_head(layers)

        model = Model(inputs=[main_input], outputs=[value_head, policy_head])
        
        model.compile(loss={'value_head': 'mean_squared_error', 
                            'policy_head': softmax_cross_entropy_with_logits
                            }
                      , optimizer=Adam(learning_rate=self.learning_rate)
                      , loss_weights={'value_head': 0.5, 'policy_head': 0.5})
        return model

    def predict(self, x):
        return self.model.predict(x)

    def fit(self, states, targets, epochs, verbose, validation_split, batch_size):
        return self.model.fit(states, targets, epochs=epochs, verbose=verbose, validation_split=validation_split,
                              batch_size=batch_size)

    def write(self, version):
        self.model.save(run_folder + 'alphazero ' + f"{version}" + '.h5')
