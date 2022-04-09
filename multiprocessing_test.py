import logging
from multiprocessing import Process, log_to_stderr

print("Running main script...")


def my_process(my_var):
    print(99)
    print(f"Running my_process with {my_var}...")

# Initialize logging for multiprocessing.
# log_to_stderr(logging.DEBUG)

# Start the process.
my_var = 100
process = Process(target=my_process, args=(my_var,))
process.start()
# process.kill()
process.join()
