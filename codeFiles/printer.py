import queue

print_list = []


def print_helper(output):
    # print('\n'.join(print_list))
    output.write('\n'.join(print_list))
    print_list.clear()


def add_line_to_queue(print_queue, output, new_top, f2):
    if f2:
        print_queue.put(new_top, f2)
    else:
        # print(new_top)
        output.write(new_top + '\n')


def print_worker(print_queue, f2, num_test):
    if not f2:
        return
    with open('output_' + str(num_test) + '.dat', 'w') as output:
        ticks = 0
        while ticks < 15:
            try:
                line = print_queue.get(timeout=1)
                ticks = 0
                print_list.append(line)
                if len(print_list) >= 256:
                    print_helper(output)
            except queue.Empty:
                ticks += 1
        print_helper(output)
