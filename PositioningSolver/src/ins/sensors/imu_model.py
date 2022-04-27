# Class to store the IMU Model (stochastic model stats)
# até posso colocar aqui a adição dos valores dos erros...

"""
Available stochastic models:
    - White Noise
    - Gauss Markov (may resort to Random Walk)
    - Random Constant
    - Constant

Definir o sensors model:
    - scale factor
        * constant or random constant or Gauss Markov
    - misalignment
        * constant or random constant or Gauss Markov
    - observation noise
        * White Noise
    - bias constant + bias stability drift
        * (Random constant or Constant) + ( Gauss Markov or Random Walk)


"""


class IMU:

    def __init__(self, accuracy):
        # pode ser a string 'mid-end', 'high-end', e isso vai automaticamente buscar o ficheiro certo (com um mapa)
        # ou entao o utilizador dá o caminho do ficheiro que quer..

        if isinstance(accuracy, str):
            pass

        elif isinstance(accuracy, dict):
            pass

        else:
            raise AttributeError(f"Provided 'accuracy' argument is not valid. Must be either 'string' or 'dict'")

        # call function to read and validate the file
        # then, after it is validated, put the info here, in the appropriate units after conversion..
