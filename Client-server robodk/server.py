# This macro shows an example to draw a polygon of radius R and n_sides vertices using the RoboDK API for Python
# More information about the RoboDK API here:
# https://robodk.com/doc/en/RoboDK-API.html
from robodk.robolink import Robolink, ITEM_TYPE_ROBOT
from robolink import *    # API to communicate with RoboDK
from robodk import *      # robodk robotics toolbox
import flask
from flask import request, jsonify

# Any interaction with RoboDK must be done through RDK:
RDK = Robolink()
# Select a robot (popup is displayed if more than one robot is available)
# robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)
# if not robot.Valid():
#     raise Exception('No robot selected or available')


# get the current position of the TCP with respect to the reference frame:
# (4x4 matrix representing position and orientation)
def moveRobot(robot):
    target_ref = robot.Pose()
    pos_ref = target_ref.Pos()
    print("Drawing a polygon around the target: ")
    print(Pose_2_TxyzRxyz(target_ref))

    # move the robot to the first point:
    robot.MoveJ(target_ref)

    # It is important to provide the reference frame and the tool frames when generating programs offline
    robot.setPoseFrame(robot.PoseFrame())
    robot.setPoseTool(robot.PoseTool())
    # Set the rounding parameter (Also known as: CNT, APO/C_DIS, ZoneData, Blending radius, cornering, ...)
    robot.setZoneData(10)
    robot.setSpeed(200)  # Set linear speed in mm/s

    # Set the number of sides of the polygon:
    n_sides = 6
    R = 100

    # make a hexagon around reference target:
    for i in range(n_sides+1):
        ang = i*2*pi/n_sides  # angle: 0, 60, 120, ...

        # -----------------------------
        # Movement relative to the reference frame
        # Create a copy of the target
        target_i = Mat(target_ref)
        pos_i = target_i.Pos()
        pos_i[0] = pos_i[0] + R*cos(ang)
        pos_i[1] = pos_i[1] + R*sin(ang)
        target_i.setPos(pos_i)
        print("Moving to target %i: angle %.1f" % (i, ang*180/pi))
        print(str(Pose_2_TxyzRxyz(target_i)))
        robot.MoveL(target_i)

        # -----------------------------
        # Post multiply: relative to the tool
        #target_i = target_ref * rotz(ang) * transl(R,0,0) * rotz(-ang)
        # robot.MoveL(target_i)

    # move back to the center, then home:
    robot.MoveL(target_ref)


app = flask.Flask(__name__)
app.config["DEBUG"] = True


def getRobots():
    robots = RDK.ItemList(filter=ITEM_TYPE_ROBOT)
    if (len(robots) == 0):
        raise Exception('No robots found in scene!')
    return robots


def createMover(): return lambda index: moveRobot(getRobots()[index])


move = createMover()


@app.route('/', methods=['POST', 'GET'])
def home():
    if(request.method == 'POST'):
        index = request.get_json()['robot']
        move(index)
        return jsonify({'am_preluat': request.get_json()['robot']})
    else:
        return jsonify({'robots': len(getRobots())})


app.run(port=1235)
