import os
from pathlib import Path
from torch import nn
import torch

ENCODER_MODEL_NAME = "dinov2_vits14"

DINOV2_SUBMODULE_PATH = Path(__file__).resolve().parents[3] / "third_party" / "dinov2"
DINOV2_WEIGHTS_ENV = "DINOV2_WEIGHTS"
DEFAULT_DINOV2_WEIGHTS = DINOV2_SUBMODULE_PATH / "checkpoints" / "dinov2_vits14.pth"

N_HEATMAPS = 3
N_CHANNELS = 50  # Number of intermediate channels for Nonlinearity
INPUT_SIZE = (448, 448)

DINO_CHANNELS = 384


def _resolve_weights_path() -> Path:
    """Get local weights path from env or default location."""

    candidate = os.getenv(DINOV2_WEIGHTS_ENV, str(DEFAULT_DINOV2_WEIGHTS))
    weights_path = Path(candidate).expanduser().resolve()
    if not weights_path.exists():
        raise FileNotFoundError(
            "DINOv2 weights not found. Ensure the Docker build downloaded them "
            f"or set {DINOV2_WEIGHTS_ENV} accordingly (expected {weights_path})."
        )
    return weights_path


class Encoder(nn.Module):
    def __init__(self, pretrained=True):
        super().__init__()
        if not DINOV2_SUBMODULE_PATH.exists():
            raise FileNotFoundError(
                "dinov2 submodule missing. Run 'git submodule update --init --recursive'."
            )

        self.model = torch.hub.load(
            DINOV2_SUBMODULE_PATH.as_posix(),
            ENCODER_MODEL_NAME,
            source="local",
            # pretrained=pretrained, Online weights loading is disabled
            pretrained=False,  # Loading from local weights file instead
        )
        weights_path = _resolve_weights_path()
        # Explicit weights_only=False to remain compatible with PyTorch >=2.6 defaults
        state_dict = torch.load(weights_path, map_location="cpu", weights_only=False)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        for param in self.model.parameters():
            param.requires_grad = False

    # pylint: disable=no-self-use
    def get_number_output_channels(self):
        return DINO_CHANNELS

    def forward(self, x):
        # pylint: disable=unused-variable
        B, C, H, W = x.shape
        with torch.no_grad():
            x = self.model.forward_features(x)["x_norm_patchtokens"]
        width_out = W // 14
        height_out = H // 14
        return (
            x.reshape(B, height_out, width_out, DINO_CHANNELS)
            .detach()
            .permute(0, 3, 1, 2)
        )


class Decoder(nn.Module):
    def __init__(self, n_input_channels, n_inter_channels, out_size, n_heatmaps):
        super().__init__()
        self.upsampling = nn.Sequential(
            nn.Upsample(size=out_size, mode="bilinear", align_corners=False),
            nn.Sigmoid(),
        )
        self.heatmaphead = nn.Sequential(
            nn.Conv2d(n_input_channels, n_inter_channels, (1, 1), bias=True),
            nn.ReLU(),
            nn.Conv2d(n_inter_channels, n_heatmaps, (1, 1), bias=True),
        )

    def forward(self, x):
        processed_features = self.heatmaphead(x)
        heatmap = self.upsampling(processed_features)
        return heatmap


class EncoderDecoder(nn.Module):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder

    def forward(self, x):
        x = self.encoder(x)
        x = self.decoder(x)
        return x


def load_model(model_path):
    encoder = Encoder(pretrained=False)
    n_feature_channels = encoder.get_number_output_channels()
    decoder = Decoder(n_feature_channels, N_CHANNELS, INPUT_SIZE, N_HEATMAPS)

    model = EncoderDecoder(encoder, decoder)
    # DDP-saved checkpoints require weights_only=False starting in PyTorch 2.6
    model.load_state_dict(torch.load(model_path, weights_only=False))
    return model
