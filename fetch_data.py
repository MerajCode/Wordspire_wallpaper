from controller import get_all_quotes, get_all_vocab, initialize_db

class FetchData:
    def __init__(self):
        initialize_db()
        self.quote_index = 0
        self.vocab_index = 0
        self.refresh_count = 0
        self.refresh_data()

    def refresh_data(self):
        self.quotes = get_all_quotes()
        self.vocabs = get_all_vocab()

    def get_next_data(self):
        if self.refresh_count >= 10:  # After every 10 cycles, reload
            self.refresh_data()
            self.refresh_count = 0

        self.refresh_count += 1

        if not self.quotes:
            quote_text = "Wordspire One word, one quote, endless inspiration"
        else:
            quote_id, quote_text = self.quotes[self.quote_index]
            self.quote_index = (self.quote_index + 1) % len(self.quotes)

        if not self.vocabs:
            word = "inspiration"
            meaning = "A feeling or thought that pushes you to do or create something"
            example = "Sometimes, inspiration strikes when you least expect it"
        else:
            vocab_id, word, meaning, example = self.vocabs[self.vocab_index]
            self.vocab_index = (self.vocab_index + 1) % len(self.vocabs)

        return {
            "quote": quote_text,
            "word": word,
            "meaning": meaning,
            "example": example
        }
