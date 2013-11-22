import signal
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from time import sleep
from threading import Thread
try:
    import Queue as queue
except:
    # Python 3
    import queue

class GenericQueue(BaseCommand):
    args = ""
    help = ""
    option_list = BaseCommand.option_list + (
        make_option(
            "-c", "--num_consumers",
            action="store",
            type="int",
            dest="num_consumers",
            default=1,
            help="Number of queue consumers to use."
        ),
    )
    _num_consumers = None
    _queue = None
    _running = True
    _threads = []

    def populate_queue(self):
        pass

    def process_item(self, item):
        pass

    def handle(self, *args, **options):
        print "Starting up..."

        self.validate_args(**options)
        self.initialize_queue()
        self.initialize_consumers()

        try:
            self.keep_fetching_items()
        except KeyboardInterrupt:
            self.warm_shutdown()

        print "Exiting..."

    def validate_args(self, **options):
        if options["num_consumers"] < 1:
            raise CommandError("Number of consumers must be greater than 0.")
        self._num_consumers = options["num_consumers"]

    def initialize_queue(self):
        def _catch_term_signal(*args, **kwargs):
            raise KeyboardInterrupt()
        signal.signal(signal.SIGTERM, _catch_term_signal)
        self._queue = queue.Queue()

    def worker(self):
        print "Starting worker..."
        while self._running:
            try:
                item = self._queue.get(block=True, timeout=5)
                self.process_item(item)
            except queue.Empty:
                pass
        print "Exiting worker..."

    def get_worker_method(self):
        def _worker_method():
            self.worker()
        return _worker_method

    def initialize_consumers(self):
        for i in range(self._num_consumers):
            t = Thread(target=self.get_worker_method())
            t.daemon = False
            t.start()
            self._threads.append(t)

    def keep_fetching_items(self):
        while True:
            self.populate_queue()
            sleep(60)

    def warm_shutdown(self):
        print "Beginning warm shutdown..."
        self._running = False
        while True:
            count = 0
            for thread in self._threads:
                if thread.is_alive():
                    count += 1
            if count == 0:
                break
            sleep(1)
        print "Warm shutdown complete."


