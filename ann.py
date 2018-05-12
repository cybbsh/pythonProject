import numpy as np
import tensorflow as tf
import os
from skimage import io
import platform
from string import Template
import cv2

#神经网络封装外码111



def makeNode(index, start=0, shape='circle', num=3, height='.5'):
    code = Template('''
    node [shape=$shape,height=$height];\n
    $nodes;\n
    ''')
    node_set = [];
    nodes = ''

    for i in range(num):
        n = 'a%d' % index + '%d' % (start + i)
        node_set.append(n)
        nodes = nodes + (n + ' ')

    str = code.substitute(index=index, shape=shape, nodes=nodes, height=height)
    return node_set, str


def makeLayer(index, color='red2', node_num=3, maxNum=2, name=''):
    code = Template('''subgraph cluster_$index {\n 
    color=white;\n
    node [style=solid,color=$color];\n
    $nodesB$nodesM$nodesE
    label = "layer $name($node_num)";\n
    }\n
    ''')
    nodesB = ''
    nodesM = ''
    nodesE = ''
    node_set = [];
    if node_num > maxNum:
        headNum = maxNum // 2
        bset, nodesB = makeNode(index=index, num=headNum)
        _, nodesM = makeNode(index=index, start=headNum, shape='point', height='.02')
        eset, nodesE = makeNode(index=index, start=(node_num - headNum), num=headNum)
        node_set = (bset + eset)
    else:
        nodes, nodesM = makeNode(index=index, num=node_num)
        node_set = nodes
    if name == '':
        name = index
    str = code.substitute(index=index, name=name, color=color, nodesB=nodesB, nodesM=nodesM, nodesE=nodesE,
                          node_num=node_num)
    return node_set, str


def makeLines(connects, node_sets):
    str = ''
    for c in connects:
        for i1 in node_sets[c[0]]:
            for i2 in node_sets[c[1]]:
                str = str + (i1 + ' -> ' + i2) + '\n'
    return str;


def makeFrame(args):
    code = Template('''digraph G {\n 
    rankdir=LR\n
    splines=line\n
    nodesep=.05;\n
    node [label=""];\n
    $layers\n
    $lines\n
    } 
    ''')
    node_sets = []
    layer_num = args["layers_num"]
    layers_cfg = args['layers_cfg']
    connects = args['connects']
    visual_num = args['visual_num']
    layers = '';
    for i in range(layer_num):
        node_set, str = makeLayer(i, layers_cfg[i][2], layers_cfg[i][1], visual_num, layers_cfg[i][0])
        node_sets.append(node_set)
        layers = layers + str

    lines = makeLines(connects, node_sets)
    return code.substitute(layers=layers, lines=lines)


def saveFile(str, path):
    print(path)
    f = open(path, 'w')
    f.write(str)
    f.close()


def makeDefConfig(i,h,o):
    args = dict()
    # path

    path = 'C:\\Users\\cybbsh\\'   # <span style="color:#ff0000;">此处做出修改</span>
    args.update({'input':  'nn.gv'})
    args.update({'output': 'nn.png'})
    # visual nodes number
    args.update({'visual_num': 10})
    # layers config:(name,nodes number,color)
    args.update({'layers_cfg': (
    ('input', i, 'blue4'), ('h1', h, 'red2'), ('out', o, 'seagreen2'))})
    layers = args['layers_cfg']
    args.update({'layers_num': len(layers)})
    # connects:layer_i->lay_j
    args.update({'connects': ([0, 1], [1, 2])})
    return args

def ann(x,y,x_pred,n):
    tf_x = tf.placeholder(tf.float32, [None,n])     # input x
    tf_y = tf.placeholder(tf.float32, [None,1])     # input y

    # neural network layers
    l1 = tf.layers.dense(tf_x, 20, tf.nn.relu)          # hidden layer
    output = tf.layers.dense(l1, 1)                     # output layer

    loss = tf.losses.mean_squared_error(tf_y, output)   # compute cost
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1)
    train_op = optimizer.minimize(loss)

    sess = tf.Session()                                 # control training and others
    sess.run(tf.global_variables_initializer())         # initialize var in graph


    for step in range(150):
        # train and net output
        _, l, pred = sess.run([train_op, loss, output], {tf_x: x, tf_y: y})
        if step % 10 == 0:
            print('loss is: ' + str(l))
            # print('prediction is:' + str(pred))

    output_pred = sess.run(output,{tf_x:x_pred})
    print('input is:' + str(x_pred[0][:]))
    print('output is:' + str(output_pred[0][0]))
    return output_pred[0][0];





x = [[100,3,50,20],[88,8,70,30],[180,20,120,49],[140,16,90,58]]
y = [[11],[17.5],[25],[22]]
# y = [11,12.5,20,18]
x_pred = [[120,5,85,22]]
result=ann(x,y,x_pred,4)
args = makeDefConfig(5, 3, 1)

str = makeFrame(args)
saveFile(str, args['input'])

cmd = 'dot ' + args['input'] + ' -Tpng -O ' + args['output']
os.system(cmd)

img = cv2.imread(r'nn.gv.png')
cv2.imshow("result", img)
while True:
    if cv2.waitKey(20) == 27:
     break