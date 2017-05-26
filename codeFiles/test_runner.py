import main
import csv
if __name__ == '__main__':
    time_list = [30, 60, 180, 300]
    lister = [False, True]
    test_num = 0
    for run_time in time_list:
        for f1 in lister:
            for f2 in lister:
                for f3 in lister:
                    for f4 in lister:
                        print("f1: {}, f2: {}, f3: {}, f4: {}".format(f1, f2, f3, f4))
                        main.initializer(run_time, f1, f2, f3, f4, test_num)
                        test_num += 1

    with open('results.csv', 'w', newline='') as results:
        writer = csv.writer(results)
        test_num = 0
        num_of_lines = 0
        for run_time in time_list:
            for f1 in lister:
                for f2 in lister:
                    for f3 in lister:
                        for f4 in lister:
                            num_of_lines =  sum(1 for line in open('output_' + str(test_num) + '.dat'))
                            writer.writerow([str(f1), str(f2), str(f3), str(f4), str(run_time), str(num_of_lines)])
                            test_num += 1
