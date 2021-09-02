from models import Video

def test_new_video():
    """
    GIVEN a Video model
    WHEN a new Video is created
    THEN check fields are defined correctly
    """
    tmp_filename = 'test.mp4'
    tmp_height = '21313'
    tmp_width = '14325'
    tmp_fps = '32'
    video = Video(tmp_filename, tmp_height, tmp_width, tmp_fps)
    assert video.filename == tmp_filename
    assert video.height == tmp_height
    assert video.width == tmp_width
    assert video.fps == tmp_fps

