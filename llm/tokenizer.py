"""Tokenizer implementation for tokenizing text sequences into discrete IDs."""

from typing import List, Dict, Set


class SimpleTokenizer:
    """A whitespace-and-punctuation tokenizer with support for special tokens."""

    PAD_TOKEN: str = "<pad>"
    UNK_TOKEN: str = "<unk>"
    BOS_TOKEN: str = "<bos>"
    EOS_TOKEN: str = "<eos>"

    def __init__(self) -> None:
        """Initialize the tokenizer vocabulary and reverse mapping."""
        self.special_tokens: List[str] = [
            self.PAD_TOKEN,
            self.UNK_TOKEN,
            self.BOS_TOKEN,
            self.EOS_TOKEN,
        ]
        self.token_to_id: Dict[str, int] = {}
        self.id_to_token: Dict[int, str] = {}
        self._reset_vocab()

    def _reset_vocab(self) -> None:
        """Reset the internal vocabulary to only special tokens."""
        self.token_to_id = {token: idx for idx, token in enumerate(self.special_tokens)}
        self.id_to_token = {idx: token for idx, token in enumerate(self.special_tokens)}

    @property
    def pad_token_id(self) -> int:
        """Return the token ID assigned to the padding token."""
        return self.token_to_id[self.PAD_TOKEN]

    @property
    def unk_token_id(self) -> int:
        """Return the token ID assigned to the unknown token."""
        return self.token_to_id[self.UNK_TOKEN]

    @property
    def bos_token_id(self) -> int:
        """Return the token ID assigned to the beginning-of-sequence token."""
        return self.token_to_id[self.BOS_TOKEN]

    @property
    def eos_token_id(self) -> int:
        """Return the token ID assigned to the end-of-sequence token."""
        return self.token_to_id[self.EOS_TOKEN]

    @property
    def vocab_size(self) -> int:
        """Return the total number of unique tokens in the vocabulary."""
        return len(self.token_to_id)

    def _tokenize(self, text: str) -> List[str]:
        """Split raw text into normalized words and punctuation marks."""
        import re

        clean_text = text.strip().lower()
        if not clean_text:
            return []
        return re.findall(r"\w+|[^\w\s]", clean_text)

    def build_vocab(self, texts: List[str]) -> None:
        """Build vocabulary mapping from a list of input text documents."""
        self._reset_vocab()
        unique_tokens: Set[str] = set()
        for text in texts:
            tokens = self._tokenize(text)
            unique_tokens.update(tokens)

        for token in sorted(unique_tokens):
            if token not in self.token_to_id:
                idx = len(self.token_to_id)
                self.token_to_id[token] = idx
                self.id_to_token[idx] = token

    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """Encode raw text into a sequence of vocabulary token IDs."""
        tokens = self._tokenize(text)
        token_ids: List[int] = []
        if add_special_tokens:
            token_ids.append(self.bos_token_id)

        for token in tokens:
            token_ids.append(self.token_to_id.get(token, self.unk_token_id))

        if add_special_tokens:
            token_ids.append(self.eos_token_id)
        return token_ids

    def decode(self, token_ids: List[int], skip_special_tokens: bool = True) -> str:
        """Decode a list of token IDs back into a reconstructed text string."""
        tokens: List[str] = []
        special_ids = {
            self.pad_token_id,
            self.unk_token_id,
            self.bos_token_id,
            self.eos_token_id,
        }

        for token_id in token_ids:
            if skip_special_tokens and token_id in special_ids:
                continue
            tokens.append(self.id_to_token.get(token_id, self.UNK_TOKEN))

        import re

        text = " ".join(tokens)
        return re.sub(r'\s+([.,!?;:])', r'\1', text)
