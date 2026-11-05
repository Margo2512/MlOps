import torch.nn as nn
import torch
import torch.nn.functional as F

class LogAttention(nn.Module):
    def __init__(self, embed_dim, num_heads, dropout = 0.0, bias=True):
        super().__init__()
        if embed_dim % num_heads != 0:
            raise ValueError("embed_dim must be divisible by num_heads")
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim**-0.5

        self.q_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.k_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.v_proj = nn.Linear(embed_dim, embed_dim, bias=bias)
        self.out_proj = nn.Linear(embed_dim, embed_dim, bias=bias)

        self.dropout = dropout

    def forward(self, query, key, value, key_padding_mask=None, attn_mask=None, need_weights = False, is_causal = False) -> torch.Tensor:
        B, Lq, E = query.shape
        Lk = key.shape[1]

        q = (
            self.q_proj(query)
            .view(B, Lq, self.num_heads, self.head_dim)
            .transpose(1, 2)
        )
        k = (
            self.k_proj(key)
            .view(B, Lk, self.num_heads, self.head_dim)
            .transpose(1, 2)
        )
        v = (
            self.v_proj(value)
            .view(B, Lk, self.num_heads, self.head_dim)
            .transpose(1, 2)
        )

        q = torch.log(F.softplus(q) + 1e-8)
        k = torch.log(F.softplus(k) + 1e-8)
        
        if key_padding_mask is not None:
            mask = key_padding_mask[:, None, None, :]
            if attn_mask is None:
                attn_mask = torch.zeros_like(mask, dtype=q.dtype)
                attn_mask = attn_mask.masked_fill(mask, float("-inf"))
            else:
                if attn_mask.dim() == 2:
                    attn_mask = attn_mask[None, None, :, :]
                attn_mask = attn_mask.masked_fill(mask, float("-inf"))

        if need_weights:
            scores = torch.matmul(q, k.transpose(-2, -1)) * self.scale
            if attn_mask is not None:
                scores = scores + attn_mask
            weights = F.softmax(scores, dim=-1)
            weights = F.dropout(weights, p=self.dropout, training=self.training)
            out = torch.matmul(weights, v)
            attn_weights = weights.mean(dim=1)
        else:
            out = F.scaled_dot_product_attention(q, k, v, attn_mask=attn_mask, dropout_p=self.dropout if self.training else 0.0, is_causal=is_causal)
            attn_weights = None

        out = out.transpose(1, 2).contiguous().view(B, Lq, E)
        out = self.out_proj(out)

        return out, attn_weights


class Model(nn.Module):
    def __init__(self, embed_dim, num_heads, num_layers):
        super().__init__()
        self.layers = nn.ModuleList([
            LogAttention(embed_dim, num_heads) for _ in range(num_layers)
        ])
        self.norm = nn.LayerNorm(embed_dim)

    def forward(self, x):
        for layer in self.layers:
            out, _ = layer(x, x, x)
            x = self.norm(x + out)
        return x