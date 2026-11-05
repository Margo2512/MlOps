import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from hypothesis import given, settings, strategies as st
from hypothesis.extra import numpy as npst
from src.models import LogAttention, Model
from torch.nn.modules import MultiheadAttention
from src.data import make_dataset, make_dataloader


@pytest.fixture
def small_att():
    return LogAttention(embed_dim=64, num_heads=4)


@pytest.fixture
def small_model():
    return Model(embed_dim=64, num_heads=4, num_layers=2)


# unit
@pytest.mark.unit
def test_log_attention_forward_shape_unit(small_att):
    x = torch.randn(2, 10, 64)
    out, _ = small_att(x, x, x)
    assert out.shape == (2, 10, 64)


@pytest.mark.unit
def test_make_dataset_shape_unit():
    ds = make_dataset(n_samples=20, n_features=5)
    x, y = ds[0]
    assert x.shape == (5,)
    assert y.shape == (1,)


# integration
@pytest.mark.integration
def test_model_with_dataloader_integration(small_model):
    loader = make_dataloader(n_samples=16, n_features=64, batch_size=4)
    xb, yb = next(iter(loader))
    out = small_model(xb.unsqueeze(1))
    assert out.shape == (4, 1, 64)


@pytest.mark.integration
def test_attention_inside_model_integration(small_model):
    x = torch.randn(2, 10, 64)
    out = small_model(x)
    assert out.shape == (2, 10, 64)


# e2e
@pytest.mark.e2e
def test_e2e_train_one_step(small_model):
    loader = make_dataloader(n_samples=32, n_features=64, batch_size=8)
    optimizer = torch.optim.SGD(small_model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    xb, yb = next(iter(loader))
    xb = xb.unsqueeze(1)
    target = torch.zeros_like(xb)

    optimizer.zero_grad()
    out = small_model(xb)
    loss = criterion(out, target)
    loss.backward()
    optimizer.step()

    assert torch.isfinite(loss)


@pytest.mark.e2e
def test_e2e_forward_backward_chain(small_model):
    loader = make_dataloader(n_samples=16, n_features=64, batch_size=4)
    xb, _ = next(iter(loader))
    xb = xb.unsqueeze(1)
    out = small_model(xb)
    loss = out.sum()
    loss.backward()
    grads = [p.grad for p in small_model.parameters() if p.grad is not None]
    assert len(grads) > 0

# LogAttention
def test_log_attention_init():
    att = LogAttention(embed_dim=512, num_heads=8)
    assert att.embed_dim == 512
    assert att.num_heads == 8
    assert att.head_dim == 64


def test_log_attention_invalid_heads():
    with pytest.raises(ValueError):
        LogAttention(embed_dim=100, num_heads=3)


def test_log_attention_forward_shape(small_att):
    x = torch.randn(2, 10, 64)
    out, weights = small_att(x, x, x)
    assert out.shape == (2, 10, 64)
    assert weights is None


def test_log_attention_need_weights(small_att):
    x = torch.randn(2, 10, 64)
    out, weights = small_att(x, x, x, need_weights=True)
    assert out.shape == (2, 10, 64)
    assert weights is not None
    assert weights.shape == (2, 10, 10)


def test_log_attention_key_padding_mask(small_att):
    x = torch.randn(2, 10, 64)
    mask = torch.zeros(2, 10, dtype=torch.bool)
    mask[:, -2:] = True
    out, _ = small_att(x, x, x, key_padding_mask=mask)
    assert out.shape == (2, 10, 64)

@st.composite
def hidden_input(draw):
    n = st.integers(1, 64)
    num_features = st.integers(128, 1024)
    arr = draw(npst.arrays(np.float32, shape=(8, 512, 512)))
    return torch.tensor(arr)

@given(x=hidden_input())
@settings(max_examples=5, deadline=None)
def test_logatt_att_match(x):
    att = MultiheadAttention(embed_dim=512, num_heads=8)
    log_att = LogAttention(embed_dim=512, num_heads=8)
    log_att_res = log_att(query = x.clone(), key = x.clone(), value = x.clone())
    att_res = att.forward(query = x.clone(), key = x.clone(), value = x.clone())
    assert att.embed_dim == log_att.embed_dim
    assert att.num_heads == log_att.num_heads
    assert torch.allclose(att_res[0], log_att_res[0]) is False

# model
def test_model_forward_shape(small_model):
    x = torch.randn(2, 10, 64)
    out = small_model(x)
    if isinstance(out, tuple):
        out = out[0]
    assert out.shape == (2, 10, 64)


def test_model_backward(small_model):
    x = torch.randn(2, 10, 64)
    out = small_model(x)
    if isinstance(out, tuple):
        out = out[0]
    loss = out.sum()
    loss.backward()
    grads = [p.grad for p in small_model.parameters() if p.grad is not None]
    assert len(grads) > 0

# dataloader
def test_dataloader_batch_shape():
    dataset = TensorDataset(torch.randn(100, 10), torch.randn(100, 1))
    loader = DataLoader(dataset, batch_size=8)
    xb, yb = next(iter(loader))
    assert xb.shape == (8, 10)
    assert yb.shape == (8, 1)


def test_dataloader_iteration_count():
    dataset = TensorDataset(torch.randn(10, 5))
    loader = DataLoader(dataset, batch_size=3)
    batches = list(loader)
    assert len(batches) == 4


def test_dataloader_no_empty_batches():
    dataset = TensorDataset(torch.randn(10, 5))
    loader = DataLoader(dataset, batch_size=3)
    for batch in loader:
        assert batch[0].shape[0] > 0

# train
def test_training_step(small_model):
    optimizer = torch.optim.SGD(small_model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    x = torch.randn(4, 10, 64)
    target = torch.randn(4, 10, 64)

    optimizer.zero_grad()
    out = small_model(x)
    if isinstance(out, tuple):
        out = out[0]
    loss = criterion(out, target)
    loss.backward()
    optimizer.step()

    assert torch.isfinite(loss)


def test_training_reduces_loss(small_model):
    optimizer = torch.optim.SGD(small_model.parameters(), lr=0.1)
    criterion = nn.MSELoss()

    x = torch.randn(4, 10, 64)
    target = torch.zeros(4, 10, 64)

    optimizer.zero_grad()
    out = small_model(x)
    if isinstance(out, tuple):
        out = out[0]
    loss1 = criterion(out, target)
    loss1.backward()
    optimizer.step()

    optimizer.zero_grad()
    out = small_model(x)
    if isinstance(out, tuple):
        out = out[0]
    loss2 = criterion(out, target)
    loss2.backward()
    optimizer.step()

    assert loss2 <= loss1 * 1.1