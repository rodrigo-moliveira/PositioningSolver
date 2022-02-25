import sys

from PositioningSolver import __algorithms_description__, PositioningSolver


def main():
    if "--help" in sys.argv or len(sys.argv) < 3:
        print("USAGES:")
        print("\t./main.py algorithm_id <path_to_config_file.json>    -> Simple Run")
        print("\t./main.py algorithm_id <path_to_config_file1.json> <path_to_config_file.json2> ...   -> Multiple Runs")

        print("Example:")
        print("\t ./main.py 0 ./workspace/outputs_gnss/gnss_1/spp_1c/config.json ./workspace/outputs_gnss/gnss_1/spp_2w/config.json")

        str_info = ""
        for alg_id, val in __algorithms_description__.items():
            str_info += str(alg_id) + " - " + val["description"] + "\n\t"

        print(f"Table of algorithms (algorithm_id - description):\n\t{str_info}")
        exit()

    # fetch argument
    algorithm_id = int(sys.argv[1])
    path_to_config_files = sys.argv[2:]

    for config_file in path_to_config_files:
        PositioningSolver(algorithm_id, config_file)



print("#-------------------------------------------------#")
print("#               Positioning Solver                #")
print("#-------------------------------------------------#\n")

if __name__ == "__main__":
    main()
