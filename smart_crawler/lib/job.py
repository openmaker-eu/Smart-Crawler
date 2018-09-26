class JobException(Exception):
    pass


class Job:
    def __init__(self, _name, _classifiers, _crawling_strategy, _seed_list, _access_token,
                 _access_secret):
        self.name = _name

        if type(_classifiers) != list and not all(map(lambda x : callable(x), _classifiers)):
            raise TypeError("Classifiers should be a list of functions")
        self.classifiers = _classifiers

        if not callable(_crawling_strategy):
            raise TypeError("Crawling strategy should be a function")
        self.crawling_strategy = _crawling_strategy

        self.seed_list = _seed_list
        self.access_token = _access_token
        self.access_secret = _access_secret
    # TODO : refactor code so that this version of job.py works
