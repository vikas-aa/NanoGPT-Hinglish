import torch
import torch.nn as nn
import torch.nn.functional as F


# ============================================================
# 1. CONFIGURATION
# ============================================================

class GPTConfig:
    vocab_size = 1438

    block_size = 128

    n_embd = 256
    n_head = 4
    n_layer = 4

    dropout = 0.1


# ============================================================
# 2. SELF ATTENTION
# ============================================================

class CausalSelfAttention(nn.Module):

    def __init__(self, config):
        super().__init__()

        assert config.n_embd % config.n_head == 0

        self.n_head = config.n_head

        self.key = nn.Linear(config.n_embd, config.n_embd)
        self.query = nn.Linear(config.n_embd, config.n_embd)
        self.value = nn.Linear(config.n_embd, config.n_embd)

        self.proj = nn.Linear(config.n_embd, config.n_embd)

        self.dropout = nn.Dropout(config.dropout)

        # Causal mask
        self.register_buffer(
            "mask",
            torch.tril(
                torch.ones(
                    config.block_size,
                    config.block_size
                )
            ).view(
                1,
                1,
                config.block_size,
                config.block_size
            )
        )

    def forward(self, x):

        B, T, C = x.size()

        head_dim = C // self.n_head

        # Q, K, V
        q = self.query(x)
        k = self.key(x)
        v = self.value(x)

        # Split into heads
        q = q.view(B, T, self.n_head, head_dim).transpose(1, 2)
        k = k.view(B, T, self.n_head, head_dim).transpose(1, 2)
        v = v.view(B, T, self.n_head, head_dim).transpose(1, 2)

        # Attention scores
        att = (q @ k.transpose(-2, -1)) / (head_dim ** 0.5)

        # Causal masking
        att = att.masked_fill(
            self.mask[:, :, :T, :T] == 0,
            float("-inf")
        )

        att = F.softmax(att, dim=-1)

        att = self.dropout(att)

        # Attention output
        y = att @ v

        # Combine heads
        y = y.transpose(1, 2).contiguous().view(B, T, C)

        y = self.proj(y)

        return y


# ============================================================
# 3. FEED FORWARD NETWORK
# ============================================================

class FeedForward(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.net = nn.Sequential(

            nn.Linear(
                config.n_embd,
                4 * config.n_embd
            ),

            nn.GELU(),

            nn.Linear(
                4 * config.n_embd,
                config.n_embd
            ),

            nn.Dropout(config.dropout)
        )

    def forward(self, x):
        return self.net(x)


# ============================================================
# 4. TRANSFORMER BLOCK
# ============================================================

class Block(nn.Module):

    def __init__(self, config):
        super().__init__()

        self.ln1 = nn.LayerNorm(config.n_embd)

        self.attention = CausalSelfAttention(config)

        self.ln2 = nn.LayerNorm(config.n_embd)

        self.ffn = FeedForward(config)

    def forward(self, x):

        # Attention + residual
        x = x + self.attention(self.ln1(x))

        # Feed forward + residual
        x = x + self.ffn(self.ln2(x))

        return x


# ============================================================
# 5. GPT MODEL
# ============================================================

class NanoGPT(nn.Module):

    def __init__(self, config):

        super().__init__()

        self.config = config

        # Token embeddings
        self.token_embedding = nn.Embedding(
            config.vocab_size,
            config.n_embd
        )

        # Position embeddings
        self.position_embedding = nn.Embedding(
            config.block_size,
            config.n_embd
        )

        self.dropout = nn.Dropout(config.dropout)

        # Transformer blocks
        self.blocks = nn.ModuleList(
            [
                Block(config)
                for _ in range(config.n_layer)
            ]
        )

        self.ln_f = nn.LayerNorm(config.n_embd)

        # Language model head
        self.lm_head = nn.Linear(
            config.n_embd,
            config.vocab_size,
            bias=False
        )

        # Weight tying
        self.lm_head.weight = self.token_embedding.weight

        self.apply(self._init_weights)

    # --------------------------------------------------------
    # Weight initialization
    # --------------------------------------------------------

    def _init_weights(self, module):

        if isinstance(module, nn.Linear):

            nn.init.normal_(
                module.weight,
                mean=0.0,
                std=0.02
            )

            if module.bias is not None:
                nn.init.zeros_(module.bias)

        elif isinstance(module, nn.Embedding):

            nn.init.normal_(
                module.weight,
                mean=0.0,
                std=0.02
            )

    # --------------------------------------------------------
    # Forward pass
    # --------------------------------------------------------

    def forward(self, idx, targets=None):

        B, T = idx.size()

        assert T <= self.config.block_size

        # Token embeddings
        tok_emb = self.token_embedding(idx)

        # Position embeddings
        positions = torch.arange(
            T,
            device=idx.device
        )

        pos_emb = self.position_embedding(positions)

        # Combine
        x = self.dropout(
            tok_emb + pos_emb
        )

        # Transformer
        for block in self.blocks:
            x = block(x)

        # Final normalization
        x = self.ln_f(x)

        # Logits
        logits = self.lm_head(x)

        loss = None

        # Next-token prediction loss
        if targets is not None:

            B, T, C = logits.size()

            logits = logits.view(
                B * T,
                C
            )

            targets = targets.view(
                B * T
            )

            loss = F.cross_entropy(
                logits,
                targets
            )

        return logits, loss


# ============================================================
# 6. TEST MODEL
# ============================================================

if __name__ == "__main__":

    config = GPTConfig()

    model = NanoGPT(config)

    print(model)

    # Fake input
    x = torch.randint(
        0,
        config.vocab_size,
        (2, config.block_size)
    )

    y = torch.randint(
        0,
        config.vocab_size,
        (2, config.block_size)
    )

    logits, loss = model(x, y)

    print("\nInput shape:", x.shape)
    print("Logits shape:", logits.shape)
    print("Loss:", loss.item())

    parameters = sum(
        p.numel()
        for p in model.parameters()
    )

    print(
        "\nTotal parameters:",
        f"{parameters:,}"
    )