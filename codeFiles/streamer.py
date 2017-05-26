import post
import comment
import utils
import dateutil.parser
from datetime import timedelta
from printer import add_line_to_queue

POST_S = "post"
COMMENT_S = "comment"
TIME_S = "time"

data_switcher_G = {POST_S: post.AddPost, COMMENT_S: comment.AddComment, TIME_S: utils.updateCurrentTime}


# change the date to a time format
def parse_date(s):
    return dateutil.parser.parse(s)


def read_file_lines(dat_file):
    for line in dat_file.readlines():
        line = line[:-1]
        data = line.split('|')
        yield data


def get_oldest_data(data_dict, data_queue):
    oldest_data = None
    oldest_type = None
    oldest_date = None

    if data_dict[POST_S] is not None:
        oldest_data = data_dict[POST_S]
        oldest_type = POST_S
        oldest_date = parse_date(oldest_data[0])

    if data_dict[COMMENT_S] is not None:
        cur_date = parse_date(data_dict[COMMENT_S][0])
        if oldest_date is None or oldest_date > cur_date:
            oldest_data = data_dict[COMMENT_S]
            oldest_type = COMMENT_S
            oldest_date = cur_date

    if not data_queue and not oldest_date:
        return None, None, None

    if not data_queue:
        oldest_data[0] = parse_date(oldest_data[0])
        return oldest_type, oldest_data, False

    if not oldest_date:
        return TIME_S, data_queue[0], None

    if data_queue[0] < oldest_date:
        return TIME_S, data_queue[0], None
    else:
        oldest_data[0] = parse_date(oldest_data[0])
        if data_queue[0] == oldest_date:
            return oldest_type, oldest_data, True
        else:
            return oldest_type, oldest_data, False

# f1 - streamer optimization of res
# f2 - printer thread optimization
# f3 - mongodb access optimization
# f4 - mongodb- delete inactive documents
def streamer(print_queue, f1, f2, f3, f4, num_test):
    with open('data/posts.dat', 'r', encoding='utf-8') as posts,\
            open('data/comments.dat', 'r', encoding='utf-8') as comments:
        output = None
        if not f2:
            output = open('output_' + str(num_test) + '.dat', 'w')
        data_dict_gen = dict()
        data_dict_gen[POST_S] = read_file_lines(posts)
        data_dict_gen[COMMENT_S] = read_file_lines(comments)

        data_queue = []

        data_dict = dict()
        for data_type in data_dict_gen:
            try:
                data_dict[data_type] = next(data_dict_gen[data_type])
            except StopIteration:
                data_dict[data_type] = None

        while True:
            data_type, data, update_time = get_oldest_data(data_dict, data_queue)
            if data is None:
                break

            if data_type == TIME_S:
                res = data_switcher_G[data_type](data, f3, f4)
                data_queue.pop(0)
                if res or not f1:
                    data_queue.append(data + timedelta(days=1))
                    new_top = post.checkNewTop(data)
                    if new_top:
                        add_line_to_queue(print_queue, output, new_top, f2)
            else:
                data_queue.append(data[0] + timedelta(days=1))
                data_switcher_G[data_type](*data)
                if update_time:
                    data_switcher_G[TIME_S](data[0], f3, f4)
                    data_queue.pop(0)
                try:
                    data_dict[data_type] = next(data_dict_gen[data_type])
                except StopIteration:
                    data_dict[data_type] = None
                new_top = post.checkNewTop(data[0])
                if new_top:
                    add_line_to_queue(print_queue, output, new_top, f2)