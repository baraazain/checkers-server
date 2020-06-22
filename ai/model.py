import tensorflow as tf
import tensorflow.keras as tk


def softmax_cross_entropy_with_logits(y_true, y_pred):
    """Calculates the loss for the policy head of AlphaZero model

    :param y_true:
    :param y_pred:
    :return:
    """
    p = y_pred
    pi = y_true

    # Mask the illegal actions
    zero = tf.zeros(shape=tf.shape(pi))
    where = tf.equal(pi, zero)

    # Remove the logits of illegal actions
    negatives = tf.fill(tf.shape(pi), -100.0)
    p = tf.where(where, negatives, p)

    # Normalize the logits vector to get the probability vector then calculate the loss
    loss = tf.nn.softmax_cross_entropy_with_logits(labels=pi, logits=p)

    return loss


def cnn_block(input_block, filters, kernel_size, regularization_const):
    """Creates the convolution block as defined in AlphaZero paper

    :param input_block:
    :param filters:
    :param kernel_size:
    :param regularization_const:
    :return:
    """
    x = tk.layers.Conv2D(filters,
                         kernel_size,
                         padding='same',
                         activation='linear',
                         kernel_regularizer=tk.regularizers.l2(regularization_const))(input_block)

    x = tk.layers.BatchNormalization(axis=1)(x)

    x = tk.layers.LeakyReLU()(x)

    return x


def residual_block(input_block, filters, kernel_size, regularization_const):
    """Creates the residual block as defined in AlphaZero paper

    :param input_block:
    :param filters:
    :param kernel_size:
    :param regularization_const:
    :return:
    """
    x = cnn_block(input_block, filters, kernel_size, regularization_const)

    x = tk.layers.Conv2D(filters,
                         kernel_size,
                         padding='same',
                         activation='linear',
                         kernel_regularizer=tk.regularizers.l2(regularization_const))(x)

    x = tk.layers.BatchNormalization(axis=1)(x)

    x = tk.layers.add([input_block, x])

    x = tk.layers.LeakyReLU()(x)

    return x


def value_head(input_block, regularization_const):
    """Creates the value head of AlphaZero model as defined in AlphaZero paper

    :param input_block:
    :param regularization_const:
    :return:
    """
    head = tk.layers.Conv2D(filters=1,
                            kernel_size=(1, 1),
                            padding='same',
                            activation='linear',
                            kernel_regularizer=tk.regularizers.l2(regularization_const))(input_block)

    head = tk.layers.BatchNormalization(axis=1)(head)

    head = tk.layers.LeakyReLU()(head)

    head = tk.layers.Flatten()(head)

    head = tk.layers.Dense(units=128,
                           activation='linear',
                           kernel_regularizer=tk.regularizers.l2(regularization_const))(head)

    head = tk.layers.LeakyReLU()(head)

    head = tk.layers.Dense(units=1,
                           activation='tanh',
                           kernel_regularizer=tk.regularizers.l2(regularization_const),
                           name='value_head')(head)

    return head


def policy_head(input_block, output_dim, regularization_const):
    """Creates the policy head of AlphaZero model as defined in AlphaZero paper

    :param input_block:
    :param output_dim:
    :param regularization_const:
    :return:
    """
    head = tk.layers.Conv2D(filters=2,
                            kernel_size=(1, 1),
                            padding='same',
                            activation='linear',
                            kernel_regularizer=tk.regularizers.l2(regularization_const))(input_block)

    head = tk.layers.BatchNormalization(axis=1)(head)

    head = tk.layers.LeakyReLU()(head)

    head = tk.layers.Flatten()(head)

    head = tk.layers.Dense(output_dim,
                           activation='linear',
                           kernel_regularizer=tk.regularizers.l2(regularization_const),
                           name='policy_head')(head)

    return head


def build_alphazero_model(input_dim, output_dim, residual_blocks, filters, regularization_const) -> tk.models.Model:
    """Creates AlphaZero model as defined in AlphaZero paper

    :param input_dim:
    :param output_dim:
    :param residual_blocks:
    :param filters:
    :param regularization_const:
    :return:
    """

    main_input = tk.layers.Input(shape=input_dim, name='main_input', dtype='float32')

    x = cnn_block(main_input, filters, 3, regularization_const)

    for _ in range(residual_blocks):
        x = residual_block(x, filters, 3, regularization_const)

    v_head = value_head(x, regularization_const)

    p_head = policy_head(x, output_dim, regularization_const)

    return tk.models.Model(inputs=[main_input], outputs=[v_head, p_head])
