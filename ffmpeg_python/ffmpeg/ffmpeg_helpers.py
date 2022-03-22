import subprocess
import os


FFMPEG_ROOT = os.getcwd() + '/ffmpeg-5.0.0/'


def create_video_from_seq(seq_path, output_path, framerate=24, crf=21, preset="fast", audio_path=None):
    exec_path = FFMPEG_ROOT + 'ffmpeg'

    if not os.path.exists(exec_path):
        print("Executable does not exist, please check path {0}".format(exec_path))
        return

    ffmpeg_cmd = '{0}'.format(exec_path)
    ffmpeg_cmd += ' -y'
    ffmpeg_cmd += ' -framerate {0}'.format(framerate)
    ffmpeg_cmd += ' -i {0}'.format(seq_path)

    if audio_path:
        ffmpeg_cmd += ' -i {0}'.format(audio_path)

    # video codec
    ffmpeg_cmd += " -c:v libx264 -crf {0} -preset {1}".format(crf, preset)

    # audio codec
    if audio_path:
        ffmpeg_cmd += ' -c:a aac -filter_complex "[1:0] apad" -shortest'

    ffmpeg_cmd += ' {0}'.format(output_path)

    print(ffmpeg_cmd)
    subprocess.call(ffmpeg_cmd, shell=True)


if __name__ == '__main__':

    # input and output files path can be changed
    img_seq_path = os.path.abspath(os.path.expanduser('~/Documents/ffmpeg/resources/img_seq/img_seq.%04d.png'))
    output_file_path = os.path.abspath(os.path.expanduser('~/Documents/ffmpeg/resources/output.mp4'))

    create_video_from_seq(img_seq_path, output_file_path)
