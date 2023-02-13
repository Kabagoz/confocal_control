import time
import json
import numpy as np
import matplotlib.pyplot as plt

FILEPATH = 'event_log.txt'
PARAMETERS_PATH = 'parameters.json'


def get_logs(filepath=FILEPATH):
    """ Reads a text file and return the list of
    to do items.
    """
    with open(filepath, "r") as file_local:
        logs_local = file_local.readlines()
    return logs_local


def write_logs(logs_arg, filepath=FILEPATH):
    """ Write the to-do items list in the text file."""
    with open(filepath, 'w') as file_local:
        file_local.writelines(logs_arg)


def update_event_log(message='beep bop'):
    event_log = get_logs()
    time_stamp = time.strftime("%b %d, %Y %H:%M:%S") + "  -  "
    new_log = time_stamp + message + '\n'
    event_log.append(new_log)
    write_logs(event_log)
    event_log_r = event_log
    event_log_r.reverse()
    return event_log_r[0]


def read_parameters(parameters_path=PARAMETERS_PATH):
    with open(parameters_path, 'r') as file:
        content = file.read()
    parameters = json.loads(content)
    return parameters


def write_parameters(params_arg, parameters_path=PARAMETERS_PATH):
    with open(parameters_path, 'w') as file_local:
        json.dump(params_arg, file_local)


def calculate_start_end_points(center, step_size, num_pixels):
    start_point = center - step_size * (num_pixels - 1) / 2
    end_point = center + step_size * (num_pixels - 1) / 2
    return start_point, end_point


def do_every(period, f, *args):
    print("inside do_every")
    counter = 0

    def g_tick():
        t = time.time()
        while True:
            t += period
            yield max(t - time.time(), 0)

    g = g_tick()
    while True:
        if not counter == 10:
            time.sleep(next(g))
            f(*args)
            counter += 1
        else:
            break


def plotting_data():
    arrayim = np.loadtxt('DATA_ARRAY.txt', delimiter=',')
    # print(arrayim)
    fig = plt.figure(figsize=(6, 3.2))
    ax = fig.add_subplot(111)
    ax.set_title('colorMap')
    plt.imshow(arrayim)
    ax.set_aspect('equal')

    cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
    cax.get_xaxis().set_visible(False)
    cax.get_yaxis().set_visible(False)
    cax.patch.set_alpha(0)
    cax.set_frame_on(False)
    plt.colorbar(orientation='vertical')
    plt.show()
    message = 'Data plotted.'
    return message


def saving_data():
    arrayim = np.loadtxt('DATA_ARRAY.txt', delimiter=',')
    time_stamp = time.strftime("%b%d_%Y_%H_%M_%S")
    data_file_name = f"data_array_{time_stamp}.txt"
    np.savetxt(data_file_name, np.array(arrayim), delimiter=', ')
    message = 'Data saved.'
    return message



# print(__name__)  # the name is only __main__
# when functions is the main function being run
if __name__ == "__main__":
    print("Hello")
    # print(get_todos())
