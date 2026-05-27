import torch

pack = torch.load("am_kramer.pt", weights_only=False)
torch.save(pack, "am_kramer.pt")
