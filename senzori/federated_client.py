import flwr as fl
import numpy as np
import tensorflow as tf


def create_autoencoder():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(16, activation="relu", input_shape=(3,)),
        # 3 caracteristici: temperatură, umiditate, lumină
        tf.keras.layers.Dense(8, activation="relu"),
        tf.keras.layers.Dense(16, activation="relu"),
        tf.keras.layers.Dense(3, activation="linear")
    ])
    model.compile(optimizer="adam", loss="mse")
    return model


model = create_autoencoder()


# Simulăm date normale de la senzor
def generate_normal_data():
    temp = np.random.uniform(20, 30)
    humidity = np.random.uniform(40, 60)
    light = np.random.uniform(50, 80)
    return np.array([[temp, humidity, light]])



class SensorClient(fl.client.NumPyClient):
    def get_parameters(self, config):
        print("🔄 [CLIENT] Trimit parametrii către server FL...")
        return model.get_weights()

    def fit(self, parameters, config):
        print("🚀 [CLIENT] Antrenare model FL...")  # Afișează un mesaj când începe antrenarea
        model.set_weights(parameters)

        x_train = np.array([generate_normal_data() for _ in range(100)]).reshape(100, 3)

        # Începem antrenarea
        history = model.fit(x_train, x_train, epochs=5, verbose=1)

        print("✅ [CLIENT] Modelul FL a fost antrenat!")
        print(f"📉 [CLIENT] Pierderea finală: {history.history['loss'][-1]}")

        return model.get_weights(), len(x_train), {}

    def evaluate(self, parameters, config):
        print("📊 [CLIENT] Evaluare model FL...")
        model.set_weights(parameters)

        x_test = np.array([generate_normal_data() for _ in range(20)]).reshape(20, 3)

        loss = model.evaluate(x_test, x_test, verbose=1)  # Evaluare cu verbose activat
        print(f"📉 [CLIENT] Pierderea modelului în evaluare: {loss}")

        return loss, len(x_test), {}


if __name__ == "__main__":
    print("📡 [CLIENT] Conectare la serverul FL...")
    fl.client.start_numpy_client(server_address="127.0.0.1:8080", client=SensorClient())
