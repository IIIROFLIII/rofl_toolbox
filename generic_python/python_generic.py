import sys
import subprocess
import os
import json
import re
from glob import glob
import colorsys

class Generic:
    def __init__(self):
        pass

    def sequence_to_mp4(self, frame_rate, start, input, output):
        # faut tester ca sous windows quand meme
        cmd = 'ffmpeg -y -framerate {0} -start_number {1} -i "{2}" "{3}"'.format(frame_rate, start, input, output)
        subprocess.check_output(cmd, shell=True)

    def mp4_to_sequence(self, input, output):
        # input = "D:/3D/ffmpeg/output.mp4"
        # output = "D:/3D/ffmpeg/beachWaves__fx3d__main__w002.%04d.jpg"

        cmd = 'ffmpeg -i "{0}" "{1}"'.format(input, output)
        subprocess.check_output(cmd, shell=True)

    def get_all_sequence_files(self, file_path, full_path=False):
        file_name = os.path.basename(file_path)

        # check file folder
        file_folder = os.path.dirname(file_path)
        if not os.path.exists(file_folder):
            return False

        # get files infos
        if not any(char.isdigit() for char in file_name):
            basename = file_name
            files = {basename: file_path}
            start = 1
            end = 1
            return basename, files, start, end

        postfix, prefix = [x[::-1] for x in re.split('[0-9][0-9]*', file_name[::-1], 1)]

        frame_digits = len(file_name) - len(prefix) - len(postfix)
        if prefix[-1] == '-':
            prefix = prefix[0:-1]

        padding = "$F{0}".format(frame_digits)
        sequence_path = os.path.join(file_folder, prefix + padding + postfix)

        frames = sorted(glob(sequence_path.replace(padding, '-' + '[0-9]' * frame_digits)), reverse=True)
        frames += sorted(glob(sequence_path.replace(padding, '[0-9]' * frame_digits)))

        # manage file
        # no files found
        if not frames:
            basename = file_name
            files = {}
            return basename, files, 0, 0

        # just one file found
        if len(frames) == 1:
            basename = file_name
            files = {basename: file_path}
            start = 1
            end = 1
            return basename, files, start, end

        # manage sequence
        frames_numbers = ([int(os.path.basename(i).split(postfix)[0].split(prefix)[-1]) for i in frames])
        start = frames_numbers[0]
        end = frames_numbers[-1]

        files = {}
        for index, file in enumerate(frames):
            files.update({frames_numbers[index]: file})

        basename = os.path.basename(sequence_path) if not full_path else sequence_path

        return basename, files, start, end

    def human_bytes(self, B):
        'Return the given bytes as a human friendly KB, MB, GB, or TB string'
        B = float(B)
        KB = float(1024)
        MB = float(KB ** 2)  # 1,048,576
        GB = float(KB ** 3)  # 1,073,741,824
        TB = float(KB ** 4)  # 1,099,511,627,776

        if B < KB:
            return '{0} {1}'.format(B, 'Bytes' if 0 == B > 1 else 'Byte')
        elif KB <= B < MB:
            return '{0:.2f} KB'.format(B / KB)
        elif MB <= B < GB:
            return '{0:.2f} MB'.format(B / MB)
        elif GB <= B < TB:
            return '{0:.2f} GB'.format(B / GB)
        elif TB <= B:
            return '{0:.2f} TB'.format(B / TB)

    def hsv_to_rgb(self, h, s, v, a=1.0):
        rgb = [round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v)]
        rgb.append(round(a * 255))

        return tuple(rgb)

    def open_folder(self, path):
        if not os.path.exists(path):
            path = os.path.expanduser("~")
        if sys.platform == "win32":
            path = '"{0}"'.format(path.replace("/", "\\"))
            subprocess.Popen(r'explorer {0}'.format(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def read_json(self, data_file):
        datas = {}
        if os.path.exists(data_file):
            with open(data_file, "r") as f:
                datas = json.load(f)

        return datas

    def save_json(self, data_file, data):
        with open(data_file, "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)

if __name__ == '__main__':
    test = Generic()
    print(test.hsv_to_rgb(0.5, 0.5, 0.5, 0.5))