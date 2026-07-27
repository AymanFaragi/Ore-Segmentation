from pathlib import Path

CAM_RAW_IMAGES_PATH = Path("assets/raw_images/")  # Directory to save captured images.
SAM_OUTPUT_IMAGE_PATH = Path("assets/sam_output_images/")  #
SAM_CHECKPOINT_VIT_B_PATH = Path("assets/checkpoints/sam_vit_b_01ec64.pth")
SAM_CHECKPOINT_VIT_L_PATH = Path("assets/checkpoints/sam_vit_l_0b3195.pth")
SAM_CHECKPOINT_VIT_H_PATH = Path("assets/checkpoints/sam_vit_h_4b8939.pth")

CONFIG_YAML_PATH = Path("config.yaml")  # Path to the configuration file.
