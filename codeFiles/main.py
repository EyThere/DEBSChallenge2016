import utils
from streamer import streamer
from printer import print_worker
import multiprocessing
import sys

print_queue = multiprocessing.Queue()

# f1 - streamer optimization of res
# f2 - printer thread optimization
# f3 - mongodb access optimization
# f4 - mongodb- delete inactive documents
def initializer(run_time, f1, f2, f3, f4, num_test):
    utils.posts.drop()
    utils.comments.drop()
    worker_print = multiprocessing.Process(target=print_worker, args=(print_queue, f2, num_test))
    worker_print.start()
    worker_streamer = multiprocessing.Process(target=streamer, args=(print_queue, f1, f2, f3, f4, num_test))
    worker_streamer.start()

    # Wait for 10 seconds or until process finishes
    worker_streamer.join(run_time)

    # If thread is still active
    if worker_streamer.is_alive():
        # Terminate
        worker_streamer.terminate()
        worker_streamer.join()

    worker_print.join()

    utils.posts.drop()
    utils.comments.drop()


if __name__== '__main__':
    if len(sys.argv) < 5:
        print("Error: fill run time")
        exit()

    run_time = float(sys.argv[1])
    f1 = bool(sys.argv[2])
    f2 = bool(sys.argv[3])
    f3 = bool(sys.argv[4])
    f4 = bool(sys.argv[5])
    initializer(run_time, f1, f2, f3, f4, 0)
