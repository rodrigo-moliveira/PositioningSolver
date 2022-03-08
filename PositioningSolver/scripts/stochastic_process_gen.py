from PositioningSolver.src.stochastic_process import WhiteNoise, RandomConstant


def main():
    process = RandomConstant(10, 1)
    print(process.compute())
    print(process)


if __name__ == "__main__":
    # example
    main()
