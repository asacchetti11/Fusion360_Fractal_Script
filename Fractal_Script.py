#Author- Alessandro Sacchetti
#Description- Generates a space filling fractal using inputted lines

import adsk.core, adsk.fusion, adsk.cam, traceback

#creates a r by c matrix of 0's
def m_create(r, c):
    output = []
    for i in range(r):
        output.append([0] * c)
    return output

def m_identity(n):
    output = m_create(n,n)
    for i in range(n):
        output[i][i] = 1
    return output

#both matrices should be same size
def m_add(X, Y): 
    output = m_create(len(X), len(X[0]))

    for i in range(len(X)):
        for j in range(len(X[i])):
            output[i][j] = X[i][j] + Y[i][j]
    return output

# X - Y
def m_subt(X, Y):
    output = m_create(len(X), len(X[0]))

    for i in range(len(X)):
        for j in range(len(X[i])):
            output[i][j] = X[i][j] - Y[i][j]
    return output

def m_scale(a, X):
    output = m_create(len(X), len(X[0]))

    for i in range(len(X)):
        for j in range(len(X[0])):
            output[i][j] = X[i][j] * a
    return output

def m_mult(X, Y):
    if (len(X[0])!=len(Y)):
        print(f"ERROR CANNOT MULTIPLY {len(X)}x{len(X[0])} by {len(Y)}x{len(Y[0])}")

    #print("X:"+str(X))
    #print("Y:"+str(Y))
    output = m_create(len(X),len(Y[0]))
    #print(str(output))
    for i in range(len(X)):
        for j in range(len(Y[0])):
            for k in range(len(Y)):
                output[i][j] += X[i][k] * Y[k][j]
    return output

def m_det(X):
    if (len(X) == 2):
        return X[0][0] * X[1][1] - X[0][1] * X[1][0]
    elif (len(X) == 1):
        return X[0]
    elif (len(X) == 0):
        return 0
    
    output = 0
    for i in range(len(X[0])):
        temp_matrix = []
        for a in range(1, len(X)):
            temp_row = []
            for b in range(len(X[a])):
                if (b != i):
                    temp_row.append(X[a][b])
            temp_matrix.append(temp_row)

        output += (-1 if i%2 else 1) * X[0][i] * m_det(temp_matrix)

    return output

#currently only for 3x3
def m_inv3(X):
    a = m_det([[X[1][1], X[1][2]],
               [X[2][1], X[2][2]]])
    b = m_det([[X[0][2], X[0][1]],
               [X[2][2], X[2][1]]])
    c = m_det([[X[0][1], X[0][2]],
               [X[1][1], X[1][2]]])
    d = m_det([[X[1][2], X[1][0]],
               [X[2][2], X[2][0]]])
    e = m_det([[X[0][0], X[0][2]],
               [X[2][0], X[2][2]]])
    f = m_det([[X[0][2], X[0][0]],
               [X[1][2], X[1][0]]])
    g = m_det([[X[1][0], X[1][1]],
               [X[2][0], X[2][1]]])
    h = m_det([[X[0][1], X[0][0]],
               [X[2][1], X[2][0]]])
    i = m_det([[X[0][0], X[0][1]],
               [X[1][0], X[1][1]]])
    return m_scale(1/m_det(X), [[a,b,c],[d,e,f],[g,h,i]])

#currently only for 2x2
def m_inv2(X):
    a = X[0][0]
    b = X[0][1]
    c = X[1][0]
    d = X[1][1]

    return m_scale(1/m_det(X), [[d, -b],[-c,a]])

#when inputted a list of points returns a list of lines created from those points
def create_lines(points):
    lines = []

    for i in range(len(points)-1):
        lines.append(adsk.core.Line3D.create(points[i], points[i+1]))
    
    return lines

#only works in 2d for now returns (B-coord origin, D-coord origin, and matrix)
#transforms from 1->2
def create_transformation_matrix2(line1: adsk.core.Line3D, line2: adsk.core.Line3D):
    origin1 = line1.startPoint
    origin2 = line2.startPoint

    end1 = line1.endPoint
    end2 = line2.endPoint
    
    x1 = end1.x - origin1.x
    y1 = end1.y - origin1.y

    B = [[x1, -y1],
         [y1, x1]]

    x2 = end2.x - origin2.x
    y2 = end2.y - origin2.y

    D = [[x2, -y2],
         [y2, x2]]

    B_inverse = m_inv2(B)
    #print("B_inv:"+str(B_inverse))
    #print("DB-1:"+str(m_mult(D, B_inverse)))
    return (origin1, origin2, m_mult(D, B_inverse))


#takes in a 2d list tranform_matrix and Point3D
def apply_transformation(B_origin, D_origin, transform_matrix, point):
    coords = [[point.x - B_origin.x], [point.y - B_origin.y]]#, [point.z - B_origin.z]]
    coords = m_mult(transform_matrix, coords)
    return adsk.core.Point3D.create(coords[0][0] + D_origin.x, coords[1][0] + D_origin.y, D_origin.z)#coords[2][0] + D_origin.z)

# reference_line is used as the place holder for the next itteration of the fractal
# seed is your shape you are fractal-ing defined by a list of points
# total_depth is the number of iterations you want it to run for
def create_fractal_lines(sketch, reference_line, seed, total_depth, depth=0):
    if (depth >= total_depth):
        for line in create_lines(seed):
            sketch.sketchCurves.sketchLines.addByTwoPoints(line.startPoint,line.endPoint)
        return
    #print(str(seed))
    for i in range(len(seed)-1):
        new_points = []
        line = adsk.core.Line3D.create(seed[i], seed[i+1])
        #sketch.sketchCurves.sketchLines.addByTwoPoints(seed[i],seed[i+1])
        (o1, o2, t_matrix) = create_transformation_matrix2(reference_line,line)
        #print(str(i)+"-"+str(depth)+":"+str(t_matrix))
        for point in seed:
            transformed_point = apply_transformation(o1, o2, t_matrix, point)
            new_points.append(transformed_point)
            #sketch.sketchPoints.add(point)
        
        create_fractal_lines(sketch, line, new_points, total_depth,depth+1)
    return

ui = None

def run(context):
#    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Fractal script running!')

        design = app.activeProduct

        # Get the root component of the active design.
        rootComp = design.rootComponent

        # create new sketch on XY plane
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)

        #These points will be used as the seed
        points = []
        
        points.append(adsk.core.Point3D.create(0,0,0))
        points.append(adsk.core.Point3D.create(25,0,0))
        points.append(adsk.core.Point3D.create(25,10,0))
        points.append(adsk.core.Point3D.create(30,20,0))
        points.append(adsk.core.Point3D.create(35,10,0))
        points.append(adsk.core.Point3D.create(35,0,0))
        points.append(adsk.core.Point3D.create(60,0,0))
        
        # this is the reference line used in create_fractal_lines() - no need to edit this
        ref_line = adsk.core.Line3D.create(points[0],points[-1])

        #using the seed create a fractal and draw all lines, this is the heavy lifting
        #that number 2 is the number of repetitions of the fractal - change the value! *3+ causes slowdowns*
        create_fractal_lines(sketch,ref_line, points, 2) 

        #draw the reference line
        sketch.sketchCurves.sketchLines.addByTwoPoints(ref_line.startPoint,ref_line.endPoint)
        
        adsk.autoTerminate(True)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Script Finished')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))