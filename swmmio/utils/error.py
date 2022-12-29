"""
Error.py contains the long noted error strings to assist the users in quickly
identifying what is wrong with their code.
"""

NO_TRACE_FOUND = \
    """

    No path has been discovered between your start and end nodes.
    If you are sure there IS a path, look over your links to see
    if any need to be reversed in your INP file.  The network
    traverse features are one-directional. Alternately, you might have
    parallel loop items present in the include nodes/links.

    """

class NoTraceFound(Exception):
    """
    Exception raised for impossible network trace.
    """
    def __init__(self):
        self.message = NO_TRACE_FOUND
        super().__init__()


class NodeNotInInputFile(Exception):
    """
    Exception raised for incomplete simulation.
    """
    def __init__(self, node):
        self.message = "Node {} is not present in INP file.".format(node)
        print(self.message)
        super().__init__(self.message)

class LinkNotInInputFile(Exception):
    """
    Exception raised for incomplete simulation.
    """
    def __init__(self, link):
        self.message = "Link {} is not present in INP file.".format(link)
        print(self.message)
        super().__init__(self.message)
