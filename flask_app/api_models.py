class API_Tag():
    def __init__(self, tag=None, category=None):
        self.tag = tag
        self.category = category

class API_File():
    def __init__(self, file_id=None, folder_id=None, name=None, tags=[], description=None):
        self.file_id = file_id
        self.folder_id = folder_id
        self.name = name
        self.tags = tags
        self.description = description

class API_File_No_Tags():
    def __init__(self, file_id=None, folder_id=None, name=None, description=None):
        self.file_id = file_id
        self.folder_id = folder_id
        self.name = name
        self.description = description

class API_Folder():
    def __init__(self, folder_id=None, parent_id=None, files=[], children=[], name=None, description=None):
        self.folder_id = folder_id
        self.parent_id = parent_id
        self.files = files
        self.children = children
        self.name = name
        self.description = description
