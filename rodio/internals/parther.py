import posixpath as xpath


class ScriptRelativePathTransformer:
    def __init__(self, script_path):
        self.script_path = script_path

    def transform(self, path):
        return transform(self.script_path, path)


def transform(scriptpath, relpath):
    this_path = xpath.dirname(scriptpath)
    return xpath.normpath(xpath.join(this_path, relpath))


def getTransformer(spath):
    return lambda path: transform(spath, path)


def getTransformerObject(path):
    return ScriptRelativePathTransformer(path)
