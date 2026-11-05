import torch
from torch.utils.data import DataLoader, TensorDataset


def make_dataset(n_samples: int = 100, n_features: int = 10) -> TensorDataset:
    x = torch.randn(n_samples, n_features)
    y = torch.randn(n_samples, 1)
    return TensorDataset(x, y)


def make_dataloader(
    n_samples: int = 100,
    n_features: int = 10,
    batch_size: int = 8,
    shuffle: bool = True,
) -> DataLoader:
    dataset = make_dataset(n_samples, n_features)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)