import argparse
import json
import cv2

parser = argparse.ArgumentParser('Visualize annotation in NIST format')
parser.add_argument('annotation', help='annotation json file')
parser.add_argument('video', help='video file')
parser.add_argument('vid', help='video name in annotation')
parser.add_argument('output', help='output video')

args = parser.parse_args()

colors = [(255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

anno_frame = {}

with open(args.annotation) as f:
    annotation = json.load(f)
assert args.vid in annotation['filesProcessed'], 'Video not annotated'
activities = [a for a in annotation['activities'] if args.vid in a['localization']]

for index, act in enumerate(activities):
    act_name = str(act['activityID'])+'/'+act['activity']
    color = colors[index%len(colors)]
    for obj in act['objects']:
        obj_name = obj['objectType']
        localization = obj['localization'][args.vid]
        frames = list(map(int, localization.keys()))
        start_frame, end_frame = min(frames), max(frames)
        last_frame = None
        for frame in range(start_frame, end_frame+1):
            anno_frame[frame] = anno_frame[frame] if frame in anno_frame else []
            if str(frame) in localization:
                if 'boundingBox' in localization[str(frame)]:
                    last_frame = (localization[str(frame)]['boundingBox'], act_name+'/'+obj_name, color)
                else:
                    last_frame = None
            if last_frame is not None:
                anno_frame[frame].append(last_frame)

capture = cv2.VideoCapture(args.video)
_, frame = capture.read()
height, width, _ = frame.shape
output_video = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*'XVID'), 30, (width, height))
capture = cv2.VideoCapture(args.video)

frame_id = 0
while True:
    ret, frame = capture.read()
    if not ret: break
    if frame_id in anno_frame:
        for bbx, anno, color in anno_frame[frame_id]:
            frame = cv2.rectangle(frame, (bbx['x'], bbx['y']), (bbx['x']+bbx['w'], bbx['y']+bbx['h']), color, 3)
            frame = cv2.putText(frame, anno, (bbx['x'], bbx['y']), cv2.FONT_HERSHEY_SIMPLEX, 1, color)

    output_video.write(frame)
    frame_id += 1
    if frame_id % 500 == 0: print(frame_id)

capture.release()
output_video.release()
