import os


class EmailFilter:
    def __init__(self, *args, **kwargs):
        # Where to find the censored mails
        self._BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        self._words_file = os.path.join(self._BASE_DIR, 'domains.txt')
        self._load_words()

    def _load_words(self):
        """ Loads the list of blocked mails from file. """
        with open(self._words_file, encoding='utf-8', mode='r') as f:
            self._block_list = [line.strip() for line in f.readlines()]

    def get_bad_mails(self):
        """ Gets all bad mails """
        bad_mails = [w for w in self._block_list]

        bad_mails = list(set(bad_mails))

        return bad_mails

    def check(self, input_text):
        bad_items = self.get_bad_mails()

        for foo in bad_items:
            if input_text.endswith(foo):
                return True

        return False
