import os

from PIL import Image
from pyglet import clock
from pyglet import window
from pyglet.gl import *  # TODO

from objects.face import Face
from objects.graph import Graph
from objects.half_edge import HalfEdge
from objects.node import Node
from voronoi_image import VoronoiImage


class MainWindow(window.Window):
    def __init__(self, width, height, image_name, name):
        window.Window.__init__(self, width, height, name)
        self.showEdge = False
        self.width = width
        self.height = height
        self.voronoi_image = VoronoiImage(image_name)
        
        # Mannually add 4 nodes with triangulation edges far outside the sight to make it easy to make the delaunay and voronoi calculations.
        node1 = Node(-9999999, -9999999)
        node2 = Node(9999999, -9999999)
        node3 = Node(0, 9999999)
        
        face1 = Face(node1, node2, node3)
        
        halfEdge1 = HalfEdge(node1, face1)
        halfEdge2 = HalfEdge(node2, face1)
        halfEdge3 = HalfEdge(node3, face1)
        
        # It is possible that there isn't a adjacent Edge. This is the case for the outer edges.
        halfEdge1.next_edge = halfEdge2
        halfEdge2.next_edge = halfEdge3
        halfEdge3.next_edge = halfEdge1
        
        face1.edge = halfEdge1
        
        nodes = []
        nodes.append(node1)
        nodes.append(node2)
        nodes.append(node3)
        faces = []
        faces.append(face1)
        halfEdges = []
        halfEdges.append(halfEdge1)
        halfEdges.append(halfEdge2)
        halfEdges.append(halfEdge3)
        
        # We will select a sorta random edge that is not on the outside.
        self.theEdgeToShow = halfEdges[2]
        self.show_face = False
        self.showAllFaces = False
        self.showVoronoiFaces = False
        self.showNextEdge = False
        self.getAdjacentEdge = False
        self.flipEdge = False
        self.amountOfNodes = 200
        
        self.graph = Graph(nodes, halfEdges, faces)
    
    def main_loop(self):
        clock.set_fps_limit(30)
        nodeSize = 5
        
        timer = 0
        while not self.has_exit:
            self.dispatch_events()
            self.clear()
            
            timer += 1
            if timer == 20:
                nodeX = 737
                nodeY = 702
                nodeNew = Node(nodeX, nodeY)
                self.graph.addNode(nodeNew)
            
            if timer == 50:
                nodeX = 190
                nodeY = 210
                nodeNew = Node(nodeX, nodeY)
                self.graph.addNode(nodeNew)
            
            if self.showNextEdge:
                self.showNextEdge = False
                self.theEdgeToShow = self.theEdgeToShow.next_edge
            if self.getAdjacentEdge:
                self.getAdjacentEdge = False
                if self.theEdgeToShow.adjacent_edge is not None:
                    self.theEdgeToShow = self.theEdgeToShow.adjacent_edge
            
            if self.flipEdge:
                temp = self.graph.manuallyFlipEdge(self.theEdgeToShow)
                if temp != None:
                    self.theEdgeToShow = temp
                self.flipEdge = False
                print("flipping edge :)")
            
            # White, so reset the colour
            glColor4f(1, 1, 1, 1)
            gl.glLineWidth(1)
            self.draw()
            
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            # Draw the nodes with how you can give it a colour
            
            if self.showAllFaces:
                
                for f in self.graph.get_faces():
                    colour = f.colour
                    glColor4f(colour[0] / 256, colour[1] / 256, colour[2] / 256, colour[3])
                    n1 = f.node1
                    n2 = f.node2
                    n3 = f.node3
                    pyglet.graphics.draw(3, GL_POLYGON,
                                         ('v2f', [n1.x, n1.y, n2.x, n2.y, n3.x, n3.y]))
            
            if self.showVoronoiFaces:
                print("show Voronoi faces")
            
            glColor4f(1, 0, 0, 1.0)
            for n in self.graph.nodes:
                nodeX = n.x
                nodeY = n.y
                pyglet.graphics.draw(4, GL_QUADS, ('v2f', [
                    nodeX - nodeSize, nodeY - nodeSize,
                    nodeX - nodeSize, nodeY + nodeSize,
                    nodeX + nodeSize, nodeY + nodeSize,
                    nodeX + nodeSize, nodeY - nodeSize
                ]))
            # draw the edges using the half edge data structure
            glColor4f(0, 1, 0, 1.0)
            for e in self.graph.edges:
                adjacentEdge = e.adjacent_edge
                # It is possible that there is no adjacent edge, this is the case for the outer edges, we don't need to draw them.
                if adjacentEdge != None:
                    nodeFrom = e.adjacent_edge.node
                    nodeTo = e.node
                    pyglet.graphics.draw(4, GL_LINES, (
                        'v2f', (0, 0, 0, height, nodeFrom.x, nodeFrom.y, nodeTo.x, nodeTo.y)))
            
            if self.showEdge:
                # Some visual debugging, show the edge as thicker and blue and draw the face.
                gl.glLineWidth(5)
                glColor4f(0, 0, 1, 1.0)
                adjacentEdge = self.theEdgeToShow.adjacent_edge
                if adjacentEdge != None:
                    nodeFrom = self.theEdgeToShow.adjacent_edge.node
                    nodeTo = self.theEdgeToShow.node
                    # print("edge name is " + self.showEdge)
                    pyglet.graphics.draw(4, GL_LINES, (
                        'v2f', (0, 0, 0, height, nodeFrom.x, nodeFrom.y, nodeTo.x, nodeTo.y)))
                
                if self.show_face:
                    current_face = self.theEdgeToShow.face
                    n1 = current_face.node1
                    n2 = current_face.node2
                    n3 = current_face.node3
                    pyglet.graphics.draw(3, GL_POLYGON,
                                         ('v2f', [n1.x, n1.y, n2.x, n2.y, n3.x, n3.y]))
            
            # Draw the voronoi polygons (numberOfPoints, GL_POLYGON, ('v2f', [all x,y coordinates]))
            # pyglet.graphics.draw(8, GL_POLYGON, ('v2f', [300,300, 300,400, 400,500, 500,500, 600,400, 600,300, 500,200, 400,200]))
            
            glColor4f(0, 0, 0, 1.0)
            clock.tick()
            self.flip()
    
    def draw(self):
        self.voronoi_image.draw()
    
    # Event handlers
    def on_mouse_motion(self, x, y, dx, dy):
        pass
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass
    
    def on_mouse_press(self, x, y, button, modifiers):
        pass
    
    def on_mouse_release(self, x, y, button, modifiers):
        print("node added at x:", x, "y:", y)
        nodeNew = Node(x, y)
        self.graph.addNode(nodeNew)
    
    def on_key_press(self, symbol, modifiers):
        print("symbol", str(symbol))
        if symbol == 97:
            # key press A
            print("a pressed")
            pressedA = True
        elif symbol == 65307:
            # escape key is pressed
            exit()
        elif symbol == 98:
            self.showEdge = True
        elif symbol == 118:
            self.showEdge = False
        elif symbol == 110:
            self.showNextEdge = True
        elif symbol == 102:
            self.show_face = True
        elif symbol == 103:
            self.show_face = False
        elif symbol == 116:
            self.getAdjacentEdge = True
        elif symbol == 112:
            self.flipEdge = True
        elif symbol == 122:
            self.showAllFaces = True
        elif symbol == 120:
            self.showAllFaces = False
        elif symbol == 119:
            self.showVoronoiFaces = True
        elif symbol == 101:
            self.showVoronoiFaces = False
    
    def on_key_release(self, symbol, modifiers):
        pass


if __name__ == "__main__":
    imageName = "Oudegracht_Utrecht_2.png"
    imagePath = os.path.abspath(os.path.dirname(__file__))
    imagePath = os.path.join(imagePath, 'data')
    imagePath = os.path.join(imagePath, imageName)
    im = Image.open(imagePath)
    (width, height) = im.size
    
    window = MainWindow(width, height, imageName, "Voronoi art project")
    window.main_loop()
