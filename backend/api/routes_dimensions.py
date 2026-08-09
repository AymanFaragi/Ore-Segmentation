import logging

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse

from backend import config
from backend.constants import CONFIG_YAML_PATH

router = APIRouter()


@router.get("/dimensions/")
async def get_dimensions():
    try:
        width_cm = config["sieve_dimensions"]["width_cm"]
        height_cm = config["sieve_dimensions"]["height_cm"]

        return JSONResponse(
            {
                "dimensions": {
                    "width_cm": width_cm,
                    "height_cm": height_cm,
                },
            },
            200,
        )
    except Exception as e:
        logging.error(f"Get dimensions error: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)}, 500)


@router.post("/update_dimensions/")
async def update_dimensions(
    sieve_width_cm: float = Form(...), sieve_height_cm: float = Form(...)
):
    try:
        if sieve_width_cm <= 0 or sieve_height_cm <= 0:
            return JSONResponse(
                {"status": "error", "message": "Dimensions must be positive"}, 400
            )

        # Update in-memory config
        config["sieve_dimensions"]["width_cm"] = sieve_width_cm
        config["sieve_dimensions"]["height_cm"] = sieve_height_cm

        try:
            # Read existing config file as text to preserve comments and format
            with open(CONFIG_YAML_PATH, "r") as f:
                config_lines = f.readlines()

            # Look for the lines containing the width and height values and update them
            width_pattern = "  width_cm:"
            height_pattern = "  height_cm:"

            for i, line in enumerate(config_lines):
                if width_pattern in line:
                    config_lines[i] = f"  width_cm: {sieve_width_cm}\n"
                elif height_pattern in line:
                    config_lines[i] = f"  height_cm: {sieve_height_cm}\n"

            # Write the modified content back to the file
            with open(CONFIG_YAML_PATH, "w") as f:
                f.writelines(config_lines)

            logging.info(
                f"Updated config.yaml with new dimensions: {sieve_width_cm}x{sieve_height_cm}cm"
            )
        except Exception as yaml_error:
            logging.error(f"Failed to update config.yaml: {str(yaml_error)}")
            # Continue execution - we've already updated the in-memory config

        logging.info(f"Updated dimensions: {sieve_width_cm}x{sieve_height_cm}cm")
        return JSONResponse(
            {
                "status": "success",
                "dimensions": {
                    "width_cm": sieve_width_cm,
                    "height_cm": sieve_height_cm,
                },
            },
            200,
        )
    except Exception as e:
        logging.error(f"Update dimensions error: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)}, 500)
