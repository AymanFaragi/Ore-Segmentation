import os
import tempfile
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

from backend.video_capture.video_capture import VideoCapture


@pytest.fixture
def video_capture_fixture():
    with patch("cv2.VideoCapture") as mock_cv2:
        # Mock the VideoCapture object returned by cv2.VideoCapture
        mock_cap = mock_cv2()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, MagicMock())
        mock_cap.get.return_value = 30  # Mock FPS
        mock_cv2.return_value = mock_cap

        # Create an instance of the VideoCapture class with mocked dependencies
        video_capture = VideoCapture()
        yield video_capture, mock_cap  # Return both the VideoCapture instance and the mock object

        # Clean-up can be done here if necessary


# Test that a RuntimeError is raised if self.cap.isOpened() is False
@patch("cv2.VideoCapture")
def test_video_capture_initialization_failure(mock_cv2, video_capture_fixture):
    video_capture, mock_cap = video_capture_fixture
    mock_cv2.return_value = mock_cap
    mock_cap.isOpened.return_value = False

    with pytest.raises(RuntimeError):
        video_capture.start_capture()


# Test start_capture() method
def test_video_capture_start_capture(video_capture_fixture):
    video_capture, mock_cap = video_capture_fixture

    video_capture.start_capture()

    assert video_capture.fps is not None
    assert isinstance(video_capture.fps, int)
    mock_cap.get.assert_called_with(cv2.CAP_PROP_FPS)


# Test stop_capture() method
def test_video_capture_stop_capture(video_capture_fixture):
    video_capture, mock_cap = video_capture_fixture

    # Adding debug information to check self.cap before calling stop_capture
    print(f"Before stop_capture: video_capture.cap = {video_capture.cap}")
    video_capture.cap = mock_cap
    video_capture.stop_capture()

    print(f"After stop_capture: video_capture.cap = {video_capture.cap}")

    mock_cap.release.assert_called_once()
    assert video_capture.cap is None


# Test capture_frame() method
def test_video_capture_capture_frame(video_capture_fixture):
    video_capture, mock_cap = video_capture_fixture

    mock_cap.read.return_value = (False, None)

    with pytest.raises(RuntimeError):
        video_capture.capture_frame()

    mock_cap.read.assert_called()


# Test save_frame() method
@patch("cv2.VideoCapture")
def test_video_capture_save_frame(mock_cv2):
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cv2.return_value = mock_cap

    with tempfile.TemporaryDirectory() as temp_dir:
        video_capture = VideoCapture(output_dir=temp_dir)

        # Create a dummy frame (numpy array)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)  # A black image
        video_capture.save_frame(frame)

        saved_files = os.listdir(temp_dir)
        assert len(saved_files) > 0
        assert saved_files[0].endswith(".png")


# Test capture_single() method
def test_video_capture_capture_single(video_capture_fixture):
    video_capture, mock_cap = video_capture_fixture

    with patch.object(
        video_capture, "capture_frame"
    ) as mock_capture_frame, patch.object(
        video_capture, "save_frame"
    ) as mock_save_frame, patch.object(
        video_capture, "stop_capture"
    ) as mock_stop_capture:

        video_capture.capture_single()

        mock_capture_frame.assert_called_once()
        mock_save_frame.assert_called_once()
        mock_stop_capture.assert_called_once()


# Test run() method
def test_video_capture_run(video_capture_fixture):
    video_capture, mock_cap = video_capture_fixture

    with patch.object(
        video_capture, "capture_single"
    ) as mock_capture_single, patch.object(
        video_capture, "capture_periodic"
    ) as mock_capture_periodic:

        video_capture.mode = "single"
        video_capture.run()
        mock_capture_single.assert_called_once()

        video_capture.mode = "periodic"
        video_capture.run()
        mock_capture_periodic.assert_called_once()
